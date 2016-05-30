import {Component} from 'angular2/core';
import {Instance} from './instance';

@Component({
  selector: 'instance-tile',
  template: `
      <div class="col-sm-3">
        <div class="tile">
          <h3 class="title">{{instance.type}}</h3>
          <p>Hostname: <b>{{instance.node}}</b></p>
          <p *ngIf="instance.type != 'Dispatcher'" ># Queries: <b>{{instance.queries}}</b></p>
        </div>
      </div>
    `,
  inputs: ['instance']
})
export class InstanceDetailComponent {

  instance: Instance;

}