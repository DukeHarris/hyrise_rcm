import {Component, OnInit} from 'angular2/core';
import {Node} from './node';
import {NodeDetailComponent} from './node-detail.component'
import {DataService} from '../service/data.service';


@Component({
    selector: 'nodes',
    template: `
      <div class="row">
        <div class="col-md-12">
          <h1><strong>Active Swarm Nodes</strong></h1>
        </div>
      </div>
      <div class="row">
        <node-tile *ngFor="#node of nodes; #i = index" [node]="node" [nodeId]="i+1"></node-tile>
      </div>
    `,
    directives: [NodeDetailComponent]
})
export class NodesComponent implements OnInit {

    nodes: Node[];
    subscription;

    constructor(private _dataService: DataService) { }

    ngOnInit() {
      this.nodes = this._dataService.getNodes();
      this.subscription = this._dataService.nodes$.subscribe(updatedNodes => {
        this.nodes = updatedNodes;
      });
    }

    ngOnDestroy() {
      this.subscription.unsubscribe();
    }

}