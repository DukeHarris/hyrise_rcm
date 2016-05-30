import { HomeComponent } from './home/home.component';
import { NodesComponent } from './nodes/nodes.component';
import { MonitorComponent } from './monitor/monitor.component';
import { Route } from 'angular2/router'

export var Routes = {
    home: new Route({ path: '/', name: 'Home', component: HomeComponent }),
    nodes: new Route({ path: '/nodes', name: 'Nodes', component: NodesComponent }),
    monitor: new Route({ path: '/monitor', name: 'Monitor', component: MonitorComponent })
}

export const APP_ROUTES = Object.keys(Routes).map(r => Routes[r]);