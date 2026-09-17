<template>
  <div class="space-y-6">
    <div v-if="!kafkaConnected" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 rounded-md flex items-start">
      <svg class="h-5 w-5 text-red-500 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
      </svg>
      <div>
        <h3 class="text-sm font-medium text-red-800 dark:text-red-400">Внимание: Брокер очередей Kafka недоступен!</h3>
        <p class="mt-1 text-sm text-red-700 dark:text-red-300">Соединение с брокером сообщений потеряно. Прием телеметрии и алертов ML приостановлен до восстановления связи.</p>
      </div>
    </div>

    <!-- Status Card -->
    <div class="bg-white dark:bg-kibana-dark_sidebar p-6 rounded border border-kibana-border dark:border-gray-700 shadow-sm flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold mb-2 text-gray-800 dark:text-gray-100">{{ $t('dashboard.ml_status') }}</h2>
        <div class="flex items-center space-x-2">
          <div :class="[isActive ? 'bg-green-500' : 'bg-red-500', 'w-3 h-3 rounded-full']"></div>
          <span class="text-sm font-medium text-gray-600 dark:text-gray-300">
            {{ isActive ? $t('dashboard.status_active') : $t('dashboard.status_inactive') }}
          </span>
        </div>
      </div>
      <div class="flex space-x-3">
        <button 
          @click="startAgent" 
          :disabled="isActive"
          class="px-4 py-2 bg-green-600 text-white font-medium rounded hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          {{ $t('dashboard.start_agent') }}
        </button>
        <button 
          @click="stopAgent"
          :disabled="!isActive"
          class="px-4 py-2 bg-red-600 text-white font-medium rounded hover:bg-red-700 disabled:opacity-50 transition-colors"
        >
          {{ $t('dashboard.stop_agent') }}
        </button>
      </div>
    </div>

    <!-- Alerts Feed -->
    <div class="bg-white dark:bg-kibana-dark_sidebar p-6 rounded border border-kibana-border dark:border-gray-700 shadow-sm">
      <h2 class="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-100">{{ $t('dashboard.recent_alerts') }}</h2>
      
      <div v-if="alerts.length === 0" class="text-gray-500 text-sm py-4 italic border-t border-gray-100 dark:border-gray-800">
        {{ isActive ? $t('dashboard.empty_active') : $t('dashboard.empty_inactive') }}
      </div>
      
      <div v-else class="space-y-4">
        <div 
          v-for="alert in alerts" 
          :key="alert._id"
          class="border border-gray-200 dark:border-gray-700 rounded overflow-hidden shadow-sm hover:shadow transition-shadow"
        >
          <!-- Compact Header -->
          <div 
            @click="toggleAlert(alert._id)"
            class="p-4 bg-gray-50 dark:bg-gray-800 flex items-center justify-between cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <div class="flex items-center space-x-4">
              <span :class="[
                alert.event.severity === 1 ? 'bg-red-500 text-white' : 'bg-orange-500 text-white',
                'px-2 py-1 text-xs font-bold rounded'
              ]">
                {{ $t('dashboard.severity') }}: {{ alert.event.severity }}
              </span>
              <span class="font-mono text-sm dark:text-gray-200">{{ alert.source.ip }}</span>
              <span class="text-sm text-gray-500 dark:text-gray-400">
                <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                {{ alert.agent_name }}
              </span>
            </div>
            <div class="flex items-center space-x-4">
              <span class="text-sm font-semibold text-gray-800 dark:text-gray-200">{{ alert.message }}</span>
              <span class="text-xs text-gray-500 dark:text-gray-400 font-mono">{{ new Date(alert['@timestamp']).toLocaleTimeString() }}</span>
              <svg :class="['w-5 h-5 text-gray-400 transition-transform', expandedAlerts.includes(alert._id) ? 'transform rotate-180' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>
          
          <!-- Expanded Details -->
          <div v-show="expandedAlerts.includes(alert._id)" class="p-4 bg-white dark:bg-kibana-dark_sidebar border-t border-gray-200 dark:border-gray-700">
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm mb-4">
              <div class="bg-gray-50 dark:bg-gray-800 p-3 rounded">
                <span class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ $t('dashboard.sensor') }}</span>
                <span class="font-semibold text-gray-800 dark:text-gray-200">{{ alert.agent_name }}</span>
              </div>
              <div class="bg-gray-50 dark:bg-gray-800 p-3 rounded">
                <span class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ $t('dashboard.score') }}</span>
                <span class="font-mono font-semibold text-kibana-primary">{{ alert.ml.anomaly_score }}</span>
              </div>
              <div class="bg-gray-50 dark:bg-gray-800 p-3 rounded">
                <span class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ $t('dashboard.algorithm') }}</span>
                <span class="font-semibold text-gray-800 dark:text-gray-200">{{ alert.ml.model_type }}</span>
              </div>
              <div class="bg-gray-50 dark:bg-gray-800 p-3 rounded">
                <span class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ $t('dashboard.src_ip') }}</span>
                <span class="font-mono font-semibold text-gray-800 dark:text-gray-200">{{ alert.source.ip }}</span>
              </div>
            </div>
            
            <div class="flex justify-end mt-4">
              <a 
                :href="alert.kibana_investigate_url" 
                target="_blank"
                class="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border border-blue-200 dark:border-blue-800 rounded hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors text-sm font-medium shadow-sm"
              >
                {{ $t('dashboard.kibana') }}
                <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'

const isActive = ref(false)
const kafkaConnected = ref(true)
const alerts = ref([])
const expandedAlerts = ref([])
let statusInterval = null

import { API_BASE as BASE_URL } from '../api'

const API_BASE = `${BASE_URL}/api/ml`

const fetchStatus = async () => {
  try {
    const res = await fetch(`${API_BASE}/status`)
    if (res.ok) {
      const data = await res.json()
      isActive.value = data.is_active
    }
  } catch (e) {
    console.error('Failed to fetch ML status', e)
  }
}

const startAgent = async () => {
  try {
    await fetch(`${API_BASE}/start`, { method: 'POST' })
    fetchStatus()
  } catch (e) {
    console.error('Failed to start agent', e)
  }
}

const stopAgent = async () => {
  try {
    await fetch(`${API_BASE}/stop`, { method: 'POST' })
    fetchStatus()
  } catch (e) {
    console.error('Failed to stop agent', e)
  }
}

const toggleAlert = (id) => {
  const i = expandedAlerts.value.indexOf(id)
  if (i > -1) {
    expandedAlerts.value.splice(i, 1)
  } else {
    expandedAlerts.value.push(id)
  }
}

const fetchAlerts = async () => {
  try {
    const res = await fetch(`${API_BASE}/alerts`)
    if (res.ok) {
      const data = await res.json()
      // Добавляем локальный _id для корректного рендеринга v-for
      alerts.value = data.map((item, index) => ({...item, _id: item._id || index}))
    }
  } catch (e) {
    console.error('Failed to fetch alerts:', e)
  }
}

const fetchSystemStatus = async () => {
  try {
    const res = await fetch(`${BASE_URL}/api/system/status`)
    if (res.ok) {
      const data = await res.json()
      kafkaConnected.value = data.kafka_connected
    }
  } catch (e) {
    kafkaConnected.value = false
    console.error('Failed to fetch system status:', e)
  }
}

onMounted(() => {
  fetchStatus()
  fetchAlerts()
  fetchSystemStatus()
  statusInterval = setInterval(() => {
    fetchStatus()
    fetchAlerts()
    fetchSystemStatus()
  }, 3000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})
</script>
