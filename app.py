#!/bin/python
from flask import *
from flask.ext.socketio import SocketIO, emit
from threading import Thread
import time
from SwarmConnector import SwarmConnector
import sys


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
loadThread = None
swarm = SwarmConnector("")


def background_thread():
    while True:
        time.sleep(5)
        swarm.updateNodesAndInstances();
        nodes = swarm.getNodes()
        socketio.emit('nodes', {'data': nodes}, namespace='/hyrise')
        instances = swarm.getInstances()
        socketio.emit('instances', {'data': instances}, namespace='/hyrise')
        latencies = swarm.getLatencies()
        socketio.emit('latencies', {'data': latencies}, namespace='/hyrise')

# Routes
@app.route('/')
@app.route('/<path:path>')
def index(path=None):
    global thread, loadThread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
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
    swarm.setURL(message["url"])
    info = swarm.connect()
    emit('connected', {'data': info})

@socketio.on('get_nodes', namespace='/hyrise')
def get_nodes():
    print("get nodes app", file=sys.stderr)
    nodes = swarm.getNodes()
    emit('nodes', {'data': nodes})

@socketio.on('get_instances', namespace='/hyrise')
def get_instances():
    instances = swarm.getInstances()
    emit('instances', {'data': instances})

@socketio.on('reset_instances', namespace='/hyrise')
def reset_instances():
    status = swarm.resetInstances()
    emit('reset', {'data': status})

@socketio.on('start_dispatcher', namespace='/hyrise')
def start_dispatcher():
    status = swarm.startDispatcher()
    emit('dispatcher_started', {'data': status})

@socketio.on('start_master', namespace='/hyrise')
def start_master():
    status = swarm.startMaster()
    emit('master_started', {'data': status})

@socketio.on('start_replica', namespace='/hyrise')
def start_replica():
    status = swarm.startReplica()
    emit('replica_started', {'data': status})

@socketio.on('set_mode', namespace='/hyrise')
def set_mode(data):
    status = swarm.setMode(data["mode"])
    emit('mode_set', {'data': status})

@socketio.on('start_autoscale', namespace='/hyrise')
def start_autoscale():
    status = swarm.startAutoScale()
    emit('autoscale_started', {'data': status})

if __name__ == '__main__':
    socketio.run(app, debug=True)