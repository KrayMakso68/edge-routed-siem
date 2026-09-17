import { createRouter, createWebHistory } from 'vue-router'
const Dashboard = () => import('./views/Dashboard.vue')
const Sensors = () => import('./views/Sensors.vue')
const Rules = () => import('./views/Rules.vue')
const Pcap = () => import('./views/Pcap.vue')
const Vpn = () => import('./views/Vpn.vue')
const RuleSources = () => import('./views/RuleSources.vue')

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Dashboard },
    { path: '/sensors', component: Sensors },
    { path: '/rules', component: Rules },
    { path: '/rule-sources', component: RuleSources },
    { path: '/pcap', component: Pcap },
    { path: '/vpn', component: Vpn },
  ],
})
