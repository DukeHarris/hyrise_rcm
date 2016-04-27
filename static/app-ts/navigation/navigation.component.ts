import {Component} from 'angular2/core';
import { ROUTER_DIRECTIVES, Location, Router } from 'angular2/router';

@Component({
    selector: 'nav-bar',
    template: `
		<nav class="navbar navbar-default navbar-fixed-top">
		  <div class="container">
		    <div class="navbar-header">
                <a class="navbar-brand" [routerLink]="['Home']">HYRISE-R<b>CM</b></a>
		    </div>
		    <div id="navbar" class="collapse navbar-collapse">
		      <ul class="nav navbar-nav">
		        <li [class.active]="router.isRouteActive(router.generate(['Nodes']))"><a [routerLink]="['Nodes']">Swarm</a></li>
		        <li [class.active]="router.isRouteActive(router.generate(['Manage']))"><a [routerLink]="['Manage']">Manage HYRISE-R</a></li>
		        <li [class.active]="router.isRouteActive(router.generate(['Monitor']))"><a [routerLink]="['Monitor']">Monitor</a></li>
		        <li [class.active]="router.isRouteActive(router.generate(['Demo']))"><a [routerLink]="['Demo']">Demo</a></li>
            <li><a>Configure</a></li>
		      </ul>

          <ul class="nav navbar-nav navbar-right">
            <a class="navbar-brand hpi_logo" href="http://hpi.de" target="_blank"><img src="/img/hpi_logo.png" /></a>
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