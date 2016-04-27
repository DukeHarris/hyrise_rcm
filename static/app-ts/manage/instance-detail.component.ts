import {Component} from 'angular2/core';
import {Instance} from './instance';

@Component({
  selector: 'instance-tile',
  template: `
      <div class="col-sm-4">
        <div class="tile">
          <h3 class="title">{{instance.type}}</h3>
          <p>Node: <b>{{instance.node}}</b></p>
          <p>Load: <b>{{instance.load}}</b></p>
          <p *ngIf="instance.type != 'dispatcher'" >Avg Latency: <b>{{instance.avgLatency}}</b></p>
        </div>
      </div>
    `,
  inputs: ['instance']
})
export class InstanceDetailComponent {

  instance: Instance;

}