from docker import Client
import sys
import datetime, calendar, time
import random
import requests
import json

class SwarmConnector(object):
    def __init__(self, url):
        self.url = url
        self.consulUrl = "consul://vm-imdmresearch-keller-06.eaalab.hpi.uni-potsdam.de:8500"

        self.nodes = []

        self.instances = []
        self.mode = "idle"
        self.autoScale = False;

        self.docker = Client(base_url='tcp://vm-imdmresearch-keller-01.eaalab.hpi.uni-potsdam.de:8888', timeout=180) #TODO

        self.dispatcherUrl = ""
        self.masterUrl = ""
        self.dispatcherNodeUrl = ""


    def setURL(self, url):
        self.url = url

    def connect(self):
        self.docker = Client(base_url=self.url, timeout=180)
        self.connected = True
        return self.docker.info()

    def updateNodesAndInstances(self):

        ## Nodes

        # We need to use a local client here as this command cannot be executed within swarm
        localDocker = Client(base_url='tcp://vm-imdmresearch-keller-01.eaalab.hpi.uni-potsdam.de:2375') # TODO: remove remote IP
        container = localDocker.create_container(image='swarm', command='list {}'.format(self.consulUrl))
        start = localDocker.start(container=container.get('Id'))
        wait = localDocker.wait(container=container.get('Id'))
        output = localDocker.logs(container=container.get('Id'))
        localDocker.remove_container(container=container.get('Id'), force=True)

        # swarm list prints an info line before the actual nodes
        response = [ n for n in output.decode("utf-8").split('\n') if "level" not in n ]

        if response:
            self.nodes = [ {"hostname": n.split('.')[0], "runningContainers": 0} for n in response ] # TODO: find a more reliable way to return the hostname


        ## Instances

        if not self.docker:
            return "Error: not connected to swarm"

        containers = self.docker.containers(all=True, filters={'status': 'running'})
        instances = []
        for container in containers:
            info = self.docker.inspect_container(container=container.get('Id'))

            if "hyrise/dispatcher" in container["Image"]:
                instances.append({
                    "type": "dispatcher",
                    "name": container["Names"][0],
                    "node": container["Names"][0].split('/')[1],
                    "Id": container["Id"],
                    "ip": info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]
                })
            elif "hyrise/hyrise_nvm" in container["Image"]:
                instances.append({
                    "type": container["Labels"]["type"],
                    "name": container["Names"][0],
                    "node": container["Names"][0].split('/')[1],
                    "Id": container["Id"],
                    "ip": info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"],
                    "avgLatency": 0
                })
        self.instances = instances
        for node in self.nodes:
            node["runningContainers"] = sum(1 for i in instances if i["node"] == node["hostname"])


        for instance in self.instances:
            containerExec = self.docker.exec_create(
                container = instance["Id"],
                cmd = "cat /proc/loadavg",
            )

            load = self.docker.exec_start(
                exec_id = containerExec["Id"]
            )

            instance["load"] = load.decode(encoding='UTF-8').split(' ')[0] # TODO: do the split with awk in exec cmd



    def getNodes(self):
        return self.nodes

    def getInstances(self):
        return self.instances

    def resetInstances(self):
        if not self.docker:
            return "Error: not connected to swarm"

        containers = self.docker.containers(all=True)
        for container in containers:
            if "hyrise" in container["Image"]:
                self.docker.remove_container(container=container.get('Id'), force=True)
        self.instances = []
        for node in self.nodes:
            node["runningContainers"] = 0


    def startDispatcher(self):
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

        self.dispatcherUrl=info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]

        # for accessing the dispatcher from outside the swarm cluster
        self.dispatcherNodeUrl = info["Node"]["Addr"].split(':')[0]

        return {"node": info["Node"]["Addr"], "ip": info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]}

    def startMaster(self):
        container = self.docker.create_container(
            image='hyrise/hyrise_nvm:latest',
            command='/bin/bash -c "sleep 10 && ./build/hyrise-server_release --dispatcherurl="{}" --dispatcherport="8080" --port=5001 --corecount=2 --nodeId=0"'.format(self.dispatcherUrl),
            ports=[5001],
            labels={"type": "master"}
        )
        start = self.docker.start(container=container.get('Id'))
        connect = self.docker.connect_container_to_network(container=container.get('Id'), net_id="swarm_network")
        info = self.docker.inspect_container(container=container.get('Id'))

        self.masterUrl=info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]
        return {"node": info["Node"]["Addr"], "ip": info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]}


    def startReplica(self):
        container = self.docker.create_container(
            image='hyrise/hyrise_nvm:latest',
            command='/bin/bash -c "sleep 10 && ./build/hyrise-server_release --masterurl="{}" --dispatcherurl="{}" --dispatcherport="8080" --port=5001 --corecount=2 --nodeId={}"'.format(self.masterUrl, self.dispatcherUrl, len(self.instances)),
            ports=[5001],
            labels={"type": "replica"}
        )
        start = self.docker.start(container=container.get('Id'))
        connect = self.docker.connect_container_to_network(container=container.get('Id'), net_id="swarm_network")
        info = self.docker.inspect_container(container=container.get('Id'))

        return {"node": info["Node"]["Addr"], "ip": info["NetworkSettings"]["Networks"]["swarm_network"]["IPAddress"]}


    def getNextNode(self):
        return sorted(self.nodes, key=lambda x: x['runningContainers'])[0]

    def getLatencies(self):


        if self.dispatcherNodeUrl != "":
            r = requests.get("http://" + self.dispatcherNodeUrl + ":8080/node_info")
            dispatcherLatencies = r.json()
        else:
            return {"system": 0}

        newLatencies = {}
        latSum = 0
        instanceCount = len([i for i in self.getInstances() if i['type'] != 'dispatcher'])
        t = datetime.datetime.now()

        print(dispatcherLatencies, file=sys.stderr)

        for host in dispatcherLatencies["hosts"]:
            for instance in self.getInstances():
                if instance["ip"] == host["ip"]:
                    hostMatches = [i for i in self.latencies if i['ip'] == host['ip']]
                    oldHost = false
                    if len(hostMatches) > 0:
                        oldHost = hostMatches[0]

                    if oldHost:
                        if host["total_queries"]-oldHost["total_queries"] > 0:
                            avgLatency = (host["total_time"]-oldHost["total_time"])/(host["total_queries"]-oldHost["total_queries"])
                        else:
                            avgLatency = 0

                    instance["avgLatency"] = avgLatency
                    latSum += avgLatency

        if instanceCount > 0:
            newLatencies["system"] = [(calendar.timegm(t.utctimetuple())*1000.0 + t.microsecond * 0.0011383651000000), latSum / instanceCount ]
        else:
            newLatencies["system"] = 0

        self.latencies = dispatcherLatencies
        return newLatencies

    def setMode(self, mode):
        # TODO set workloads
        return

    def startAutoScale(self):
        self.autoScale = True;

    def stopAutoScale(self):
        self.autoScale = False;