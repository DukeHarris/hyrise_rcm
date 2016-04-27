# clustermanager

## Installation

```
pip install -r requirements.txt
cd static
npm install
npm run tsc
```

## Start
python app.py







### Setup Swarm Cluster

For all swarm features to work, make sure you are using at least kernel 3.19. ON ubuntu 14.04 (LTS) you can install the 3.19 kernel via:

```
apt-get install linux-generic-lts-vivid
```

We need a key-value store for multi host networking. You can use etcd/consul/zookeeper

```
docker run -d \
	-p "8500:8500" \
	-h "consul" \
	progrium/consul -server -bootstrap
```

Start docker daemons with consul backend and make them listen on for swarm support. On ubuntu, add this to /etc/default/docker
```
DOCKER_OPTS="-H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock --cluster-store=consul://vm-imdmresearch-keller-06.eaalab.hpi.uni-potsdam.de:8500 --cluster-advertise=eth0:2376"

```

```
docker run --rm swarm create
docker run -d -p 8888:2375 swarm manage consul://<consul address>:8500
docker run -d swarm join --addr="<node address>:2376" consul://<consul address>:8500
docker run --rm swarm list token://<token>
docker -H <swarm master >network create swarm_network
```
