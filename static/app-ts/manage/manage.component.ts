import {Component, OnInit} from 'angular2/core';
import {Instance} from './instance';
import {InstanceDetailComponent} from './instance-detail.component';
import {DataService} from '../service/data.service';


@Component({
    selector: 'manage',
    template: `
        <div class="row">
            <div class="col-md-12">
                <h1><strong>Hyrise-R Instances</strong></h1>
            </div>
        </div>

        <div class="row">
            <div class="col-md-12">
                <div class="tile center" [innerHTML]="statusText"></div>
            </div>
        </div>

        <div class="row">
            <instance-tile *ngFor="#instance of instances" [instance]="instance"></instance-tile>
        </div>

        <div class="row">
            <div class="col-md-12">
                <div class="tile center">
                    <button id="start_dispatcher" (click)="startDispatcher()" class="btn btn-primary">Start Dispatcher</button>
                    <button id="start_master" (click)="startMaster()" class="btn btn-default">Start Master</button>
                    <button id="start_replica" (click)="startReplica()" class="btn btn-default">Start Replica</button>
                    <button id="reset_instances" (click)="resetInstances()" class="btn btn-danger">Stop All Instances</button>
                </div>
            </div>
        </div>
    `,
    directives: [InstanceDetailComponent]
})

export class ManageComponent implements OnInit {

    instances: Instance[] = [];
    statusText: String;
    subscription;

    constructor(private _dataService: DataService) { }

    ngOnInit() {
        this.instances = this._dataService.getInstances();
        this.updateStatusText();
        this.subscription =this._dataService.instances$.subscribe(updatedInstances => {
            this.instances = updatedInstances;
            this.updateStatusText();
        });
    }

    ngOnDestroy() {
        this.subscription.unsubscribe();
    }

    updateStatusText() {
        var dispatcherCount: number = 0;
        var masterCount: number = 0;
        var replicaCount: number = 0;

        for (var i = 0; i < this.instances.length; i++) {
            if (this.instances[i].type === "dispatcher") {
                dispatcherCount++;
            } else if (this.instances[i].type === "master") {
                masterCount++;
            } else if (this.instances[i].type === "replica") {
                replicaCount++;
            }
        }

        this.statusText = ""
            + "<b>Dispatcher:</b> <span class='" + (dispatcherCount == 0 ? "not-" : "") + "running'>" + (dispatcherCount == 0 ? "not " : "") + "running</span> | "
            + "<b>Master:</b> <span class='" + (masterCount == 0 ? "not-" : "") + "running'>" + (masterCount == 0 ? "not " : "") + "running</span> | "
            + "<b>Replica:</b> <span class='" + (replicaCount == 0 ? "not-" : "") + "running'>" + (replicaCount == 0 ? "not " : "") + "running</span>"

    }

    startDispatcher(){
        this._dataService.startDispatcher();
    }
    startMaster() {
        this._dataService.startMaster();
    }
    startReplica(){
        this._dataService.startReplica();
    }
    resetInstances() {
        this._dataService.resetInstances();
    }
}