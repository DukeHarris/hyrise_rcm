import {Component} from 'angular2/core';
import {Node} from './node';

@Component({
  selector: 'node-tile',
  template: `
      <div class="col-sm-4">
        <div class="tile">
          <h3 class="title">Node {{nodeId}}</h3>
          <p>Hostname: <b>{{node.hostname}}</b></p>
          <p>Running Containers: <b>{{node.runningContainers}}</b></p>
        </div>
      </div>
    `,
    inputs: ['node', 'nodeId']
})
export class NodeDetailComponent {

    node : Node;
    nodeId: number;

}