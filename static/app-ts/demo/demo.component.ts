/// <reference path="../../typings/browser/ambient/jquery/jquery.d.ts" />
import {Component, OnInit} from 'angular2/core';
import {DataService} from '../service/data.service';
import {Ng2Highcharts} from '../ng2-highcharts/ng2-highcharts';

declare var Highcharts: any;
declare var jQuery:JQueryStatic;

@Component({
    selector: 'demo',
    template: `
        <div class="row">
            <div class="col-md-12">
                <h1><strong>Demo</strong></h1>
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
                    <button id="start_workload" (click)="startWorkload()" class="btn btn-primary">Workload 1</button>
                    <button id="increase_workload" (click)="increaseWorkload()" class="btn btn-default">Workload 2</button>
                    <button id="stop_workload" (click)="stopWorkload()" class="btn btn-danger">Stop Workload</button>
                    <button id="auto_scale" [disabled]="autoScaleActive" (click)="autoScale()" class="btn btn-success">Auto-Scale</button>
                </div>
            </div>
        </div>
    `,
    directives: [Ng2Highcharts]
})

export class DemoComponent implements OnInit {

    chartOptions = {
        credits: {
            enabled: false
        },
        chart: {
            type: 'area'
        },
        title: {
            text: 'Avg Query Execution Time'
        },
        yAxis: {
            title: {
                text: 'time in ms'
            }
        },
        xAxis: {
            type: 'datetime'
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
            name: 'Avg Query Execution Time',
            data: []
        }]
    };
    subscription: any;
    autoScaleActive: boolean = false;

    constructor(private _dataService: DataService) {}

    ngOnInit() {
        // setInterval(() => {
        //     jQuery("#graph").highcharts().series[0].addPoint([new Date().getTime(), Math.trunc(Math.random() * 10)]);
        // }, 3000);
        // this.chartOptions.series[0].data = this._dataService.getLatencies()["system"];

        this.subscription = this._dataService.latencies$.subscribe(updatedLatencies => {
            console.log(updatedLatencies);
            var chart = jQuery("#graph").highcharts();
            if (chart)
                chart.series[0].addPoint(updatedLatencies["system"]);
        });

    }
    ngOnDestroy() {
        this.subscription.unsubscribe();
    }

    startWorkload(){
        this._dataService.startWorkload();
    }

    stopWorkload() {
        this._dataService.stopWorkload();
    }

    increaseWorkload() {
        this._dataService.increaseWorkload();
    }

    autoScale() {
        this.autoScaleActive = true;
        this._dataService.autoScale();
    }
}