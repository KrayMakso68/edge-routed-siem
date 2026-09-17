<template>
  <div class="bg-white dark:bg-kibana-dark_sidebar p-8 rounded border border-gray-200 dark:border-gray-700 shadow-sm">
    <!-- Title Row -->
    <div class="mb-4">
      <h2 class="text-xl font-bold text-gray-800 dark:text-gray-100">{{ $t('sensors.title') }}</h2>
    </div>

    <!-- Action Buttons Row (Below title, above table) -->
    <div class="flex space-x-3 mb-6">
      <button @click="openAddModal" class="bg-blue-600 hover:bg-blue-700 text-white py-1.5 px-4 rounded text-sm font-medium transition-colors">
        + {{ $t('common.add') }}
      </button>
      <button @click="openEditModal" :disabled="selected.length !== 1" class="bg-amber-500 hover:bg-amber-600 disabled:bg-gray-400 text-white py-1.5 px-4 rounded text-sm font-medium transition-colors">
        {{ $t('common.edit') }}
      </button>
      <button @click="confirmDelete" :disabled="selected.length === 0" class="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white py-1.5 px-4 rounded text-sm font-medium transition-colors">
        {{ $t('common.delete') }}
      </button>
    </div>

    <!-- Таблица сенсоров -->
    <div class="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th class="w-12 px-4 py-3"><input type="checkbox" @change="toggleAll" :checked="selected.length === sensors.length && sensors.length > 0" class="rounded border-gray-300"></th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('sensors.name') }}</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('common.status') }}</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">CPU (%)</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">RAM (%)</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('sensors.ip') }}</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('sensors.network') }}</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('sensors.desc') }}</th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-kibana-dark_sidebar divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-if="sensors.length === 0">
            <td colspan="8" class="px-4 py-6 text-center text-sm text-gray-500">{{ $t('common.loading') }}</td>
          </tr>
          <tr v-for="s in sensors" :key="s.id" class="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer" @click="toggleSelect(s.id)">
            <td class="px-4 py-3 text-center" @click.stop><input type="checkbox" :value="s.id" v-model="selected" class="rounded border-gray-300"></td>
            <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-200">{{ s.name }}</td>
            <td class="px-4 py-3 text-sm">
              <span v-if="getSensorOnline(s.name)" class="text-green-600 bg-green-100 px-2 inline-flex text-xs leading-5 font-semibold rounded-full dark:bg-opacity-20">Online</span>
              <span v-else class="text-gray-500 bg-gray-100 px-2 inline-flex text-xs leading-5 font-semibold rounded-full dark:bg-opacity-20">Offline</span>
            </td>
            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 font-mono">{{ getSensorCpu(s.name) }}</td>
            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 font-mono">{{ getSensorRam(s.name) }}</td>
            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 font-mono">{{ s.ip }}</td>
            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{{ s.network }}</td>
            <td class="px-4 py-3 text-sm text-gray-500 dark:text-gray-500">{{ s.description }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Модальное окно добавления / редактирования -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-96">
        <h3 class="text-lg font-bold mb-4 text-gray-800 dark:text-gray-100">{{ isEdit ? $t('sensors.edit_sensor') : $t('sensors.add_new') }}</h3>
        <div class="space-y-3">
          <input v-model="form.name" :placeholder="$t('sensors.name')" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200" />
          <input v-model="form.ip" :placeholder="$t('sensors.ip')" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200" />
          <input v-model="form.network" :placeholder="$t('sensors.network')" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200" />
          <input v-model="form.description" :placeholder="$t('sensors.desc')" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200" />
        </div>
        <div class="mt-6 flex justify-end space-x-3">
          <button @click="showModal = false" class="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">{{ $t('common.cancel') }}</button>
          <button @click="saveSensor" class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">{{ $t('common.save') }}</button>
        </div>
      </div>
    </div>

    <ConfirmModal
      :visible="showDeleteConfirm"
      :title="$t('common.confirm_title')"
      :message="$t('common.confirm_text')"
      :confirmText="$t('common.confirm_yes')"
      :cancelText="$t('common.confirm_no')"
      type="danger"
      @confirm="executeDelete"
      @cancel="showDeleteConfirm = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'
import ConfirmModal from '../components/ConfirmModal.vue'

const { t } = useI18n()
const sensors = ref([])
const selected = ref([])

const showModal = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const form = ref({ name: '', ip: '', network: '', description: '' })

const showDeleteConfirm = ref(false)

const fetchSensors = async () => {
  const res = await api.get('/api/sensors/')
  sensors.value = res.data
}

const toggleAll = (e) => {
  selected.value = e.target.checked ? sensors.value.map(s => s.id) : []
}

const toggleSelect = (id) => {
  const index = selected.value.indexOf(id)
  if (index === -1) {
    selected.value.push(id)
  } else {
    selected.value.splice(index, 1)
  }
}

const openAddModal = () => {
  isEdit.value = false
  editingId.value = null
  form.value = { name: '', ip: '', network: '', description: '' }
  showModal.value = true
}

const openEditModal = () => {
  if (selected.value.length !== 1) return;
  const sensor = sensors.value.find(s => s.id === selected.value[0])
  if (sensor) {
    isEdit.value = true
    editingId.value = sensor.id
    form.value = { ...sensor, description: sensor.description || '' }
    showModal.value = true
  }
}

const saveSensor = async () => {
  if (isEdit.value && editingId.value) {
    await api.put(`/api/sensors/${editingId.value}`, form.value)
  } else {
    await api.post('/api/sensors/', form.value)
  }
  showModal.value = false
  selected.value = []
  fetchSensors()
}

const confirmDelete = () => {
  if (selected.value.length > 0) {
    showDeleteConfirm.value = true
  }
}

const executeDelete = async () => {
  showDeleteConfirm.value = false
  for (let id of selected.value) {
    await api.delete(`/api/sensors/${id}`)
  }
  selected.value = []
  fetchSensors()
}

const sensorStatusMap = ref({})

const fetchStatus = async () => {
  try {
    const res = await api.get('/api/sensors/status')
    sensorStatusMap.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const getSensorOnline = (name) => {
  const stat = sensorStatusMap.value[name]
  if (!stat) return false
  const nowSec = Date.now() / 1000
  return (nowSec - stat.last_seen) < 25
}

const getSensorCpu = (name) => {
  const stat = sensorStatusMap.value[name]
  if (!stat || !getSensorOnline(name)) return '-'
  return stat.cpu + '%'
}

const getSensorRam = (name) => {
  const stat = sensorStatusMap.value[name]
  if (!stat || !getSensorOnline(name)) return '-'
  return stat.ram + '%'
}

let statusInterval
onMounted(() => {
  fetchSensors()
  fetchStatus()
  statusInterval = setInterval(fetchStatus, 5000)
})

onUnmounted(() => {
  clearInterval(statusInterval)
})
</script>
