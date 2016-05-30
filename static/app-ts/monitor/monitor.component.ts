/// <reference path="../../typings/browser/ambient/jquery/jquery.d.ts" />
import {Component, OnInit} from 'angular2/core';
import {DataService} from '../service/data.service';
import {Ng2Highcharts} from '../ng2-highcharts/ng2-highcharts';
import {Instance} from './instance';
import {InstanceDetailComponent} from './instance-detail.component';

declare var Highcharts: any;
declare var jQuery:JQueryStatic;

@Component({
    selector: 'monitor',
    template: `
        <div class="row">
            <div class="col-md-12">
                <h1><strong>Manage and Monitor Replication</strong></h1>
            </div>
        </div>

        <div class="row">
            <div class="col-md-12">
               <div [ng2-highcharts]="chartOptions" id="graph"></div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-12">
                <div class="tile center">
                    <button id="start_dispatcher" (click)="startDispatcher()" class="btn btn-default">Start Dispatcher</button>
                    <button id="start_master" (click)="startMaster()" class="btn btn-default">Start Master</button>
                    <button id="start_replica" (click)="startReplica()" class="btn btn-default">Add Replica</button>
                    <button id="remove_replica" (click)="removeReplica()" class="btn btn-default">Remove Replica</button>
                    <button id="reset_instances" (click)="resetInstances()" class="btn btn-danger">Stop All Instances</button>
                    <button id="reset_instances" (click)="setWorkload(1)" class="btn btn-primary">Start Workload</button>
                    <button id="reset_instances" (click)="setWorkload(0)" class="btn btn-primary">Stop Workload</button>
                </div>
            </div>
        </div>

        <div class="row">
            <instance-tile *ngFor="#instance of instances" [instance]="instance"></instance-tile>
        </div>

    `,
    directives: [Ng2Highcharts, InstanceDetailComponent]
})

export class MonitorComponent implements OnInit {

    instances: Instance[] = [];

    chartOptions = {
        credits: {
            enabled: false
        },
        chart: {
            type: 'area'
        },
        title: {
            text: 'OLAP Query Throughput'
        },
        yAxis: {
            title: {
                text: '#Queries per Second'
            }
        },
        xAxis: {
            type: 'datetime',
            labels: {
                enabled: false
            }
        },
        plotOptions: {
            area: {
                marker: {
                    enabled: false
                }
            }
        },
        legend: { enabled: false },
        tooltip: { enabled: false },
        series: [{
            name: 'queries per second',
            data: []
        }]
    };
    subscription: any;
    subscription2: any;

    constructor(private _dataService: DataService) {}

    ngOnInit() {

        this.instances = this._dataService.getInstances();
        this.subscription2 =this._dataService.instances$.subscribe(updatedInstances => {
            this.instances = updatedInstances;
        });


        // setInterval(() => {
        //     jQuery("#graph").highcharts().series[0].addPoint([new Date().getTime(), Math.trunc(Math.random() * 10)]);
        // }, 3000);
        // this.chartOptions.series[0].data = this._dataService.getThroughput()["system"];

        this.subscription = this._dataService.throughput$.subscribe(updatedThroughput => {
            console.log(updatedThroughput);
            var chart = jQuery("#graph").highcharts();
            if (chart) {
                chart.series[0].addPoint(updatedThroughput["system"], true, chart.series[0].data.length > 20);
            }
        });
    }

    ngOnDestroy() {
        this.subscription.unsubscribe();
        this.subscription2.unsubscribe();
    }

    setWorkload(flag){
        this._dataService.setWorkload(flag);
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
    removeReplica(){
        this._dataService.removeReplica();
    }
    resetInstances() {
        this._dataService.resetInstances();
    }

}