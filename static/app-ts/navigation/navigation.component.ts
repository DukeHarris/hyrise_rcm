import {Component} from 'angular2/core';
import { ROUTER_DIRECTIVES, Location, Router } from 'angular2/router';

@Component({
    selector: 'nav-bar',
    template: `
    <nav class="navbar navbar-default navbar-fixed-top">
      <div class="container">
          <ul class="nav navbar-nav navbar-left">
                  <a class="navbar-brand hpi_logo" href="http://hpi.de" target="_blank"><img src="/img/logo_transparent.png" /></a>
                </ul>
          <div id="navbar" class="collapse navbar-collapse">
              <ul class="nav navbar-nav">
                <li [class.active]="router.isRouteActive(router.generate(['Nodes']))"><a [routerLink]="['Nodes']">Cloud Nodes</a></li>
                <li [class.active]="router.isRouteActive(router.generate(['Monitor']))"><a [routerLink]="['Monitor']">Manage & Monitor Replication</a></li>
              </ul>

                <ul class="nav navbar-nav navbar-right">
                  <a class="navbar-brand hpi_logo" href="http://hpi.de" target="_blank"><img src="/img/hpi_logo_transparent.png" /></a>
                </ul>
          </div>
        </div>
    </nav>
    `,
    directives: [
        ROUTER_DIRECTIVES
    ]
})

export class NavigationComponent {
    constructor(public router: Router) {
    }
}