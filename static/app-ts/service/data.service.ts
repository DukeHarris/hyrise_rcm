import {Injectable} from 'angular2/core';
import {Node} from '../nodes/node';
import {Instance} from '../manage/instance';
import {Observable} from 'rxjs/Observable';
import 'rxjs/add/operator/share';

declare var io: any;

@Injectable()
export class DataService {

    socket: any;
    private _nodesObserver: any;
    private _instancesObserver: any;
    private _latenciesObserver: any;
    private _dataStore: {
        nodes: Array<Node>,
        instances: Array<Instance>,
        latencies: {
            "system": Array<Array<number>>
        }
    };
    public nodes$: Observable<Array<Node>>;
    public instances$: Observable<Array<Instance>>;
    public latencies$: Observable<Array<Instance>>;

    constructor() {
        var me = this;
        this.socket = io.connect('http://' + document.domain + ':' + location.port + '/hyrise');
        console.log(this.socket);

        this.instances$ = new Observable(observer => {
            this._instancesObserver = observer;
        }).share();

        this.nodes$ = new Observable(observer => {
            this._nodesObserver = observer;
        }).share();

        this.latencies$ = new Observable(observer => {
            this._latenciesObserver = observer;
        }).share();

        this._dataStore = { instances: [], nodes: [], latencies: { "system": [] } };



        this.socket.on('nodes', (msg) => {
            this._dataStore.nodes = msg.data;
            if (this._nodesObserver) // apparently an observer will only be created after something subscribed to the observable
                this._nodesObserver.next(this._dataStore.nodes);
            console.log(msg.data);
        });

        this.socket.on('instances',(msg) => {
            this._dataStore.instances = msg.data;
            if (this._instancesObserver) // apparently an observer will only be created after something subscribed to the observable
                this._instancesObserver.next(this._dataStore.instances);
            console.log(msg.data);
        });

        this.socket.on('latencies', (msg) => {
            this._dataStore.latencies["system"].push(msg.data["system"]);
            this._dataStore.latencies["system"].sort(function(a,b) {
                var x = a[0];
                var y = b[0];
                return y - x;
            });
            if (this._latenciesObserver) // apparently an observer will only be created after something subscribed to the observable
                this._latenciesObserver.next(msg.data);
            console.log(msg.data);
        });
    }


    getNodes() {
        return this._dataStore.nodes;
    }

    getInstances() {
        return this._dataStore.instances;
    }

    getLatencies() {
        return this._dataStore.latencies;
    }

    startDispatcher(){
        this.socket.emit('start_dispatcher');
    }

    startMaster() {
        this.socket.emit('start_master');
    }

    startReplica() {
        this.socket.emit('start_replica');
    }

    resetInstances() {
        this.socket.emit('reset_instances');
    }

    startWorkload() {
        console.log("starting load");
        this.socket.emit('set_mode', {mode: "load1"});
    }

    stopWorkload() {
        this.socket.emit('set_mode', { mode: "idle" });
    }

    increaseWorkload() {
        this.socket.emit('set_mode', { mode: "load2" });
    }

    autoScale() {
        this.socket.emit('start_autoscale');
    }
}