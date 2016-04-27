import { HomeComponent } from './home/home.component';
import { NodesComponent } from './nodes/nodes.component';
import { ManageComponent } from './manage/manage.component';
import { MonitorComponent } from './monitor/monitor.component';
import { DemoComponent } from './demo/demo.component';
import { Route } from 'angular2/router'

export var Routes = {
    home: new Route({ path: '/', name: 'Home', component: HomeComponent }),
    nodes: new Route({ path: '/nodes', name: 'Nodes', component: NodesComponent }),
    manage: new Route({ path: '/manage', name: 'Manage', component: ManageComponent }),
    monitor: new Route({ path: '/monitor', name: 'Monitor', component: MonitorComponent }),
    demo: new Route({ path: '/demo', name: 'Demo', component: DemoComponent })
}

export const APP_ROUTES = Object.keys(Routes).map(r => Routes[r]);