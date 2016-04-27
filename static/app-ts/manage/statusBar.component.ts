import {Component} from 'angular2/core';
import {Instance} from './instance';


@Component({
  selector: 'status-bar',
  template: `
    <div class="tile" [innerHTML]="statusText">
    </div>
    `,
  inputs: ['instances']
})
export class StatusBarComponent {

  instances: Instance[];
  statusText: String = "<b>dispatcher:</b> <span class='not-running'>not running</span> | "
  + "<b>master:</b> <span class='not-running'>not running</span> | "
  + "<b>replica:</b> <span class='not-running'>not running</span>";

  onChange(map) {
    console.log("change event on status bar");
    if (map.instances) {
      this.updateStatusText();
    }
  }

  updateStatusText(){
    var dispatcherCount: number = 0;
    var masterCount: number = 0;
    var replicaCount: number = 0;

    for (var i = 0; i < this.instances.length; i++){
      if (this.instances[i].type === "dispatcher"){
        dispatcherCount++;
      } else if (this.instances[i].type === "master") {
        masterCount++;
      } else if (this.instances[i].type === "replica") {
        replicaCount++;
      }
    }

    this.statusText = ""
      + "<b>dispatcher:</b> <span class='" + (dispatcherCount == 0 ? "not-" : "") + "running'>" + (dispatcherCount == 0 ? "not " : "") + "running</span> | "
      + "<b>master:</b> <span class='" + (masterCount == 0 ? "not-" : "") + "running'>" + (masterCount == 0 ? "not " : "") + "running</span> | "
      + "<b>replica:</b> <span class='" + (replicaCount == 0 ? "not-" : "") + "running'>" + (replicaCount == 0 ? "not " : "") + "running</span> | "

  }

}