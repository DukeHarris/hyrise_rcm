import { Component } from 'angular2/core';
import { RouteConfig, ROUTER_DIRECTIVES } from 'angular2/router';
import {APP_ROUTES, Routes} from "./routes.config";
import { NavigationComponent } from './navigation/navigation.component';
import {DataService} from './service/data.service';

@Component({
    selector: 'hyrise-rcm',
    template: `
        <nav-bar></nav-bar>
        <div class="container">
            <router-outlet></router-outlet>
        </div>
        <footer class="footer">
            <div class="container">
                <p class="text-muted"></p>
            </div>
        </footer>
    `,
    directives: [
        ROUTER_DIRECTIVES,
        NavigationComponent
    ]
})

@RouteConfig(APP_ROUTES)


export class AppComponent {

    constructor(dataService: DataService) { }

}