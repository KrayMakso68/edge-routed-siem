<template>
  <div class="bg-white dark:bg-kibana-dark_sidebar p-8 rounded border border-gray-200 dark:border-gray-700 shadow-sm relative">
    
    <!-- Title Row -->
    <div class="mb-4">
      <h2 class="text-xl font-bold text-gray-800 dark:text-gray-100 flex items-center">
        {{ $t('pcap.title') }}
      </h2>
    </div>

    <!-- Sensor Selection Row -->
    <div class="mb-4">
      <select v-model="selectedSensor" @change="fetchPcaps" class="w-64 px-3 py-1.5 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200 outline-none">
        <option :value="null" disabled>{{ $t('rules.select_sensor') }}</option>
        <option v-for="s in sensors" :value="s.id" :key="s.id">{{ s.name }} ({{ s.ip }})</option>
      </select>
    </div>

    <!-- Action Buttons Row -->
    <div v-if="selectedSensor" class="flex space-x-3 mb-6">
      <button @click="fetchPcaps" class="bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 py-1.5 px-4 rounded text-sm font-medium transition-colors">
        {{ $t('pcap.refresh') }}
      </button>
      <button @click="downloadSelected" :disabled="selected.length === 0" class="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white py-1.5 px-4 rounded text-sm font-medium transition-colors">
        {{ $t('pcap.download_btn') }}
      </button>
    </div>
    
    <div v-if="!selectedSensor" class="py-12 text-center text-gray-500 dark:text-gray-400 border-2 border-dashed border-gray-200 dark:border-gray-700 rounded">
      {{ $t('pcap.desc') }}
    </div>

    <div v-else class="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th class="w-12 px-4 py-3"><input type="checkbox" @change="toggleAll" :checked="selected.length === files.length && files.length > 0" class="rounded border-gray-300"></th>
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('pcap.filename') }}</th>
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('pcap.size') }}</th>
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('pcap.date') }}</th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-kibana-dark_sidebar divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-if="loading"><td colspan="4" class="px-6 py-6 text-center text-sm text-gray-500">{{ $t('common.loading') }}</td></tr>
          <tr v-else-if="files.length === 0"><td colspan="4" class="px-6 py-6 text-center text-sm text-gray-500">{{ $t('pcap.empty') }}</td></tr>
          <tr v-for="file in files" :key="file.filename" class="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer" @click="toggleSelect(file.filename)">
            <td class="px-4 py-3 text-center" @click.stop><input type="checkbox" :value="file.filename" v-model="selected" class="rounded border-gray-300"></td>
            <td class="px-6 py-3 text-sm font-mono text-gray-800 dark:text-gray-200">{{ file.filename }}</td>
            <td class="px-6 py-3 text-sm text-gray-600 dark:text-gray-400">{{ file.size }}</td>
            <td class="px-6 py-3 text-sm text-gray-600 dark:text-gray-400">{{ file.date }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { API_BASE } from '../api'

const sensors = ref([])
const selectedSensor = ref(null)
const files = ref([])
const selected = ref([])
const loading = ref(false)

const fetchSensors = async () => {
  const res = await api.get('/api/sensors/')
  sensors.value = res.data
}

const fetchPcaps = async () => {
  if (!selectedSensor.value) return;
  loading.value = true
  selected.value = []
  try {
    const res = await api.get(`/api/pcap/list/${selectedSensor.value}`)
    files.value = res.data.files
  } finally {
    loading.value = false
  }
}

const toggleAll = (e) => {
  selected.value = e.target.checked ? files.value.map(f => f.filename) : []
}

const toggleSelect = (filename) => {
  const index = selected.value.indexOf(filename)
  if (index === -1) {
    selected.value.push(filename)
  } else {
    selected.value.splice(index, 1)
  }
}

const downloadSelected = () => {
  selected.value.forEach((filename, index) => {
    setTimeout(() => {
      const link = document.createElement('a')
      link.href = `${API_BASE}/api/pcap/download/${selectedSensor.value}/${filename}`
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }, index * 500)
  })
}

onMounted(fetchSensors)
</script>
