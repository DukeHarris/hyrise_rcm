#!/bin/python
import sys
import time
from threading import Thread

from flask import *
from flask_socketio import SocketIO, emit

from SwarmConnector import SwarmConnector
from query_hyrise import benchmark, query_hyrise


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()





# Setup Flask app.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread2 = None
swarm = SwarmConnector("")


def background_thread():
    while True:
        time.sleep(2)
        swarm.update_nodes_and_instances()
        nodes = swarm.get_nodes()
        socketio.emit('nodes', {'data': nodes}, namespace='/hyrise')
        instances = swarm.get_instances()
        socketio.emit('instances', {'data': instances}, namespace='/hyrise')


def workload_thread():
    while True:
        if swarm.workload_is_set:
            print("Load data")
            with open('./queries/1_load_docker.json', 'r') as query_f:
                query = query_f.read()
                print(query_hyrise(swarm.dispatcher_ip, 8080, query))
            swarm.throughput = benchmark(swarm.dispatcher_ip, 8080, './queries/q1.json', 3, 3)
            print("Bench start..")
            swarm.throughput = benchmark(swarm.dispatcher_ip, 8080, './queries/q1.json', 9, 18)
            print("Bench stop..")
            throughput = swarm.get_throughput()
            socketio.emit('throughput', {'data': throughput}, namespace='/hyrise')
        else:
            time.sleep(1)



# Routes
@app.route('/')
@app.route('/<path:path>')
def index(path=None):
    global thread, thread2
    if thread is None:
        thread = Thread(target=background_thread)
        thread2 = Thread(target=workload_thread)
        #thread.daemon = True
        thread.start()
        #thread2.daemon = True
        thread2.start()
    return app.send_static_file('index.html')

@app.route('/css/<path:path>')
def css_proxy(path):
    return send_from_directory('static/css', path)

@app.route('/img/<path:path>')
def img_proxy(path):
    return send_from_directory('static/img', path)

@app.route('/node_modules/<path:path>')
def node_proxy(path):
    return send_from_directory('static/node_modules', path)

@app.route('/app/<path:path>')
def app_proxy(path):
    return send_from_directory('static/app', path)

@app.route('/app-ts/<path:path>')
def app_ts_proxy(path):
    return send_from_directory('static/app-ts', path)

# Events
@socketio.on('connect_swarm', namespace='/hyrise')
def test_connect(message):
    swarm.set_url(message["url"])
    info = swarm.connect()
    emit('connected', {'data': info})

@socketio.on('get_nodes', namespace='/hyrise')
def get_nodes():
    print("get nodes app", file=sys.stderr)
    nodes = swarm.get_nodes()
    emit('nodes', {'data': nodes})

@socketio.on('get_instances', namespace='/hyrise')
def get_instances():
    instances = swarm.get_instances()
    emit('instances', {'data': instances})

@socketio.on('reset_instances', namespace='/hyrise')
def reset_instances():
    status = swarm.reset_instances()
    emit('reset', {'data': status})

@socketio.on('start_dispatcher', namespace='/hyrise')
def start_dispatcher():
    status = swarm.start_dispatcher()
    emit('dispatcher_started', {'data': status})

@socketio.on('start_master', namespace='/hyrise')
def start_master():
    status = swarm.start_master()
    emit('master_started', {'data': status})

@socketio.on('start_replica', namespace='/hyrise')
def start_replica():
    status = swarm.start_replica()
    emit('replica_started', {'data': status})

@socketio.on('remove_replica', namespace='/hyrise')
def remove_replica():
    status = swarm.remove_replica()
    emit('replica_removed', {'data': status})

@socketio.on('set_workload', namespace='/hyrise')
def set_workload(data):
    status = swarm.set_workload(data["status"])
    emit('workload_set', {'data': status})


if __name__ == '__main__':
    socketio.run(app, debug=True)
