from docker import Client
import time
import requests
import threading

class SwarmConnector(object):
    def __init__(self, url):
        self.url = url
        self.consul_url = "consul://vm-imdmresearch-keller-06.eaalab.hpi.uni-potsdam.de:8500"

        self.nodes = []
        self.instances = []

        self.workload_is_set = False
        self.throughput = 0

        self.docker = Client(base_url='tcp://vm-imdmresearch-keller-01.eaalab.hpi.uni-potsdam.de:8888', timeout=180) #TODO
        self.lock = threading.Lock()

        self.dispatcher_url = "" #internal ip
        self.master_url = ""
        self.dispatcher_node_url = ""
        self.dispatcher_ip = "" # external ip to receive queries


    def set_url(self, url):
        self.url = url

    def connect(self):
        self.docker = Client(base_url=self.url, timeout=180)
        self.connected = True
        return self.docker.info()

    def update_nodes_and_instances(self):

        ## Nodes
        self.lock.acquire()
        try:
            # We need to use a local client here as this command cannot be executed within swarm
            local_docker = Client(base_url='tcp://vm-imdmresearch-keller-01.eaalab.hpi.uni-potsdam.de:2375') # TODO: remove remote IP
            container = local_docker.create_container(image='swarm', command='list {}'.format(self.consul_url))
            start = local_docker.start(container=container.get('Id'))
            wait = local_docker.wait(container=container.get('Id'))
            output = local_docker.logs(container=container.get('Id'))
            local_docker.remove_container(container=container.get('Id'), force=True)

            # swarm list prints an info line before the actual nodes
            response = [n for n in output.decode("utf-8").split('\n') if "level" not in n]

            print(response)

            if response:
                self.nodes = [{"hostname": n.split('.')[0].replace('keller-', ''), "runningContainers": 0} for n in response if n != ''] # TODO: find a more reliable way to return the hostname

            if self.dispatcher_node_url != "":
                r = requests.get("http://" + self.dispatcher_node_url + ":8080/node_info")
                instances_info = r.json()['hosts']
            else:
                instances_info = None
            print(instances_info)

            ## Instances

            if not self.docker:
                return "Error: not connected to swarm"

            containers = self.docker.containers(all=True, filters={'status': 'running'})
            instances = []
            for container in containers:
                info = self.docker.inspect_container(container=container.get('Id'))

                if "hyrise/dispatcher" in container["Image"]:
                    instances.append({
                        "type": "Dispatcher",
                        "name": container["Names"][0],
                        "node": container["Names"][0].split('/')[1].replace('keller-', ''),
                        "Id": container["Id"],
                        "ip": info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]
                    })
                    self.dispatcher_url = info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]
                    self.dispatcher_node_url = info["Node"]["Addr"].split(':')[0]
                    self.dispatcher_ip = info["Node"]["IP"]

                elif "hyrise/hyrise_nvm" in container["Image"]:
                    swarm_ip = info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]
                    queries = 0
                    total_time = 0
                    throughput = "n.a."
                    if instances_info:
                        info = [i for i in instances_info if i['ip'] == swarm_ip]
                        if len(info) == 1:
                            queries = int(info[0]['total_queries'])
                            total_time = int(info[0]['total_time'])
                            if queries != 0:
                                throughput = "%.2f ms" % (total_time/queries/1000)

                    instances.append({
                        "type": container["Labels"]["type"].capitalize(),
                        "name": container["Names"][0],
                        "node": container["Names"][0].split('/')[1].replace('keller-', ''),
                        "Id": container["Id"],
                        "ip": swarm_ip,
                        "throughput": throughput,
                        "totalTime": total_time,
                        "queries": queries
                    })
            self.instances = instances
            for node in self.nodes:
                node["runningContainers"] = sum(1 for i in instances if i["node"] == node["hostname"])


            for instance in self.instances:
                container_exec = self.docker.exec_create(
                    container=instance["Id"],
                    cmd="cat /proc/loadavg",
                )

                load = self.docker.exec_start(
                    exec_id=container_exec["Id"]
                )

                instance["load"] = load.decode(encoding='UTF-8').split(' ')[0] # TODO: do the split with awk in exec cmd
        except Exception:
            print("Exception")
        self.lock.release()


    def get_nodes(self):
        return self.nodes

    def get_instances(self):
        return self.instances

    def reset_instances(self):
        if not self.docker:
            return "Error: not connected to swarm"

        self.lock.acquire()
        containers = self.docker.containers(all=True)
        for container in containers:
            if "hyrise" in container["Image"]:
                self.docker.remove_container(container=container.get('Id'), force=True)
        self.instances = []
        for node in self.nodes:
            node["runningContainers"] = 0

        self.dispatcher_url = ""
        self.master_url = ""
        self.dispatcher_node_url = ""
        self.dispatcher_ip = ""
        self.lock.release()


    def start_dispatcher(self):
        container = self.docker.create_container(
            image='hyrise/dispatcher:docker',
            command='./start_dispatcher 8080 settings.json',
            ports=[8080],
            labels={"type": "dispatcher"},
            host_config=self.docker.create_host_config(port_bindings={
                8080: 8080, # expose dispatcher for debugging. TODO: remove
            })
        )
        start = self.docker.start(container=container.get('Id'))
        connect = self.docker.connect_container_to_network(container=container.get('Id'), net_id="swarm_network")
        info = self.docker.inspect_container(container=container.get('Id'))

        self.dispatcher_url = info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]

        # for accessing the dispatcher from outside the swarm cluster
        self.dispatcher_node_url = info["Node"]["Addr"].split(':')[0]

        return {"node": info["Node"]["Addr"], "ip": info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]}

    def start_master(self):
        container = self.docker.create_container(
            image='hyrise/hyrise_nvm:latest',
            command='/bin/bash -c "sleep 2 && wget http://vm-imdmresearch-keller-01.eaalab.hpi.uni-potsdam.de:8000/ORDER_LINE.tbl && \
                     ./build/hyrise-server_release --dispatcherurl="{}" --dispatcherport="8080" --port=5001 --corecount=2 --nodeId=0"'.format(self.dispatcher_url),
            ports=[5001],
            labels={"type": "master"}
        )
        start = self.docker.start(container=container.get('Id'))
        connect = self.docker.connect_container_to_network(container=container.get('Id'), net_id="swarm_network")
        info = self.docker.inspect_container(container=container.get('Id'))

        self.master_url = info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]
        return {"node": info["Node"]["Addr"], "ip": info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]}


    def start_replica(self):
        container = self.docker.create_container(
            image='hyrise/hyrise_nvm:latest',
            command='/bin/bash -c "sleep 2 && wget http://vm-imdmresearch-keller-01.eaalab.hpi.uni-potsdam.de:8000/ORDER_LINE.tbl && \
                     ./build/hyrise-server_release --masterurl="{}" --dispatcherurl="{}" --dispatcherport="8080" --port=5001 --corecount=2 --nodeId={}"'.format(self.master_url, self.dispatcher_url, len(self.instances)),
            ports=[5001],
            labels={"type": "replica"}
        )
        start = self.docker.start(container=container.get('Id'))
        connect = self.docker.connect_container_to_network(container=container.get('Id'), net_id="swarm_network")
        info = self.docker.inspect_container(container=container.get('Id'))

        return {"node": info["Node"]["Addr"], "ip": info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]}

    def remove_replica(self):
        if not self.docker:
            return "Error: not connected to swarm"

        self.lock.acquire()
        containers = self.docker.containers(all=True)
        for container in containers:
            if "hyrise/hyrise_nvm" in container["Image"]:
                info = self.docker.inspect_container(container=container.get('Id'))
                ip = info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]
                if ip != self.master_url:
                    print('remove_node')
                    try:
                        requests.get("http://" + self.dispatcher_node_url + ":8080/remove_node/%s:" % ip, timeout=1)
                    except Exception:
                        print('remove')
                        self.docker.remove_container(container=container.get('Id'), force=True)
                        print('removed')
                        break
        self.lock.release()
        return


    def get_throughput(self):
        return {"system": [time.time(), self.throughput]}


    def set_workload(self, status):
        print("set workload", status)
        if int(status) == 1:
            self.workload_is_set = True
        else:
            self.workload_is_set = False
        return
