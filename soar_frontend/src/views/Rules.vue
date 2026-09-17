<template>
  <div class="bg-white dark:bg-kibana-dark_sidebar p-8 rounded border border-gray-200 dark:border-gray-700 shadow-sm relative">
    
    <!-- Title Row -->
    <div class="mb-4">
      <h2 class="text-xl font-bold text-gray-800 dark:text-gray-100 flex items-center">
        {{ $t('rules.title') }}
      </h2>
    </div>

    <!-- Sensor Selection Row -->
    <div class="mb-4">
      <select v-model="selectedSensor" @change="fetchRules" class="w-64 px-3 py-1.5 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200 outline-none">
        <option :value="null" disabled>{{ $t('rules.select_sensor') }}</option>
        <option v-for="s in sensors" :value="s.id" :key="s.id">{{ s.name }} ({{ s.ip }})</option>
      </select>
    </div>

    <!-- Action Buttons Row -->
    <div v-if="selectedSensor" class="flex items-center justify-between mb-6">
      <div class="flex space-x-3">
        <button @click="showAddModal = true" class="bg-blue-600 hover:bg-blue-700 text-white py-1.5 px-4 rounded text-sm font-medium transition-colors">
          + {{ $t('common.add') }}
        </button>
        <button @click="confirmDelete" :disabled="selected.length === 0" class="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white py-1.5 px-4 rounded text-sm font-medium transition-colors">
          {{ $t('common.delete') }}
        </button>
      </div>
      
      <div class="flex items-center space-x-2">
        <select v-model="selectedSource" class="w-56 px-3 py-1.5 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200 outline-none">
          <option :value="null" disabled>{{ $t('rules.select_source') }}</option>
          <option v-for="src in ruleSources" :value="src.id" :key="src.id">{{ src.name }}</option>
        </select>
        <button @click="syncFromSource" :disabled="!selectedSource || loading" class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white py-1.5 px-4 rounded text-sm font-medium transition-colors">
          {{ $t('rules.update_from_source') }}
        </button>
      </div>
    </div>

    <!-- Заглушка, если сенсор не выбран -->
    <div v-if="!selectedSensor" class="py-12 text-center text-gray-500 dark:text-gray-400 border-2 border-dashed border-gray-200 dark:border-gray-700 rounded">
      {{ $t('rules.no_sensor') }}
    </div>

    <!-- Широкое поле с правилами -->
    <div v-else class="border border-gray-200 dark:border-gray-700 rounded overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th class="w-12 px-6 py-3"><input type="checkbox" @change="toggleAll" :checked="selected.length === rules.length && rules.length > 0" class="rounded border-gray-300"></th>
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('rules.existing_rules') }}</th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-kibana-dark_sidebar divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-if="loading && !isBatchDeploying"><td colspan="2" class="px-6 py-4 text-center text-sm text-gray-500">{{ $t('common.loading') }}</td></tr>
          <tr v-else-if="rules.length === 0 && !isBatchDeploying"><td colspan="2" class="px-6 py-4 text-center text-sm text-gray-500">{{ $t('rules.empty') }}</td></tr>
          <tr v-for="r in rules" :key="r.id" class="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer" @click="toggleSelect(r.rule_text)">
            <td class="px-6 py-3 text-center" @click.stop><input type="checkbox" :value="r.rule_text" v-model="selected" class="rounded border-gray-300"></td>
            <td class="px-6 py-4 text-sm font-mono text-gray-700 dark:text-gray-300 break-all">{{ r.rule_text }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Модальное окно добавления правила -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]">
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-[600px]">
        <h3 class="text-lg font-bold mb-4 text-gray-800 dark:text-gray-100">{{ $t('rules.new_rule') }}</h3>
        <textarea v-model="newRuleText" rows="6" :placeholder="$t('rules.placeholder')" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm font-mono text-gray-800 dark:text-gray-200 mb-4 focus:outline-none focus:ring-1 focus:ring-blue-500"></textarea>
        <div class="flex justify-end space-x-3">
          <button @click="showAddModal = false" class="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">{{ $t('common.cancel') }}</button>
          <button @click="startBatchAdd" :disabled="!newRuleText.trim() || loading" class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">{{ $t('common.save') }}</button>
        </div>
      </div>
    </div>

    <!-- Оверлей при пакетном добавлении / синхронизации (анимация загрузки) -->
    <div v-if="isBatchDeploying" class="fixed inset-0 bg-white/60 dark:bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center z-[70]">
      <div class="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mb-4"></div>
      <div class="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-2">
        {{ syncMode ? $t('rules.syncing') : $t('rules.deploying') }}
      </div>
      <div v-if="!syncMode" class="text-sm text-gray-600 dark:text-gray-300 font-medium bg-white dark:bg-gray-800 px-4 py-2 rounded shadow-sm border border-gray-200 dark:border-gray-700">
        {{ $t('rules.batch_progress', { current: currentRuleIndex, total: totalRulesToDeploy }) }}
      </div>
    </div>

    <!-- Подтверждение удаления -->
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
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'
import ConfirmModal from '../components/ConfirmModal.vue'

const { t } = useI18n()
const sensors = ref([])
const selectedSensor = ref(null)
const rules = ref([])
const newRuleText = ref('')
const loading = ref(false)
const showAddModal = ref(false)

// State for batch deploy animation
const isBatchDeploying = ref(false)
const currentRuleIndex = ref(0)
const totalRulesToDeploy = ref(0)

// State for deletion
const showDeleteConfirm = ref(false)
const selected = ref([])

const toggleAll = (e) => {
  selected.value = e.target.checked ? rules.value.map(r => r.rule_text) : []
}

const toggleSelect = (rule_text) => {
  const index = selected.value.indexOf(rule_text)
  if (index === -1) {
    selected.value.push(rule_text)
  } else {
    selected.value.splice(index, 1)
  }
}

const selectedSource = ref(null)
const ruleSources = ref([])
const syncMode = ref(false)

const fetchSensors = async () => {
  const res = await api.get('/api/sensors/')
  sensors.value = res.data
}

const fetchRuleSources = async () => {
  try {
    const res = await api.get('/api/suricata/sources/')
    ruleSources.value = res.data
  } catch (e) {
    console.error("Error fetching rule sources:", e)
  }
}

const syncFromSource = async () => {
  if (!selectedSensor.value || !selectedSource.value) return;
  
  syncMode.value = true
  isBatchDeploying.value = true
  
  try {
    // 0.5с начальная задержка для визуального эффекта
    await new Promise(r => setTimeout(r, 500))
    await api.post(`/api/suricata/rules/${selectedSensor.value}/sync`, { source_id: selectedSource.value })
    await fetchRules()
  } catch (e) {
    alert(t('common.error') + ": " + (e.response?.data?.detail || e.message))
  } finally {
    isBatchDeploying.value = false
    syncMode.value = false
  }
}

const fetchRules = async () => {
  if (!selectedSensor.value) return;
  selected.value = [] // Очищаем выбор при смене/загрузке
  loading.value = true
  try {
    const res = await api.get(`/api/suricata/rules/${selectedSensor.value}?_t=${Date.now()}`)
    rules.value = res.data
  } finally {
    loading.value = false
  }
}

const startBatchAdd = async () => {
  if (!newRuleText.value.trim()) return;
  
  // Split by newline and remove empty lines
  const rulesToDeploy = newRuleText.value.split('\n')
    .map(r => r.trim())
    .filter(r => r.length > 0)

  if (rulesToDeploy.length === 0) return;

  // Close modal and start animation
  showAddModal.value = false
  newRuleText.value = ''
  
  syncMode.value = false
  isBatchDeploying.value = true
  totalRulesToDeploy.value = rulesToDeploy.length
  currentRuleIndex.value = 0

  // 0.5s initial delay for visual effect
  await new Promise(r => setTimeout(r, 500))

  for (let i = 0; i < rulesToDeploy.length; i++) {
    currentRuleIndex.value = i + 1
    try {
      await api.post(`/api/suricata/rules/${selectedSensor.value}`, { rule_text: rulesToDeploy[i] })
    } catch (e) {
      console.error("Error adding rule:", rulesToDeploy[i], e)
    }
  }

  // Brief pause at 100% completion before hiding
  await new Promise(r => setTimeout(r, 500))
  
  isBatchDeploying.value = false
  await fetchRules()
}

const confirmDelete = () => {
  if (selected.value.length > 0) {
    showDeleteConfirm.value = true
  }
}

const executeDelete = async () => {
  if (selected.value.length === 0) return;
  
  showDeleteConfirm.value = false
  loading.value = true
  
  try {
    await api.post(`/api/suricata/rules/${selectedSensor.value}/batch-delete`, { rule_texts: selected.value })
    selected.value = []
    await fetchRules()
  } catch (e) {
    alert(t('common.error') + ": " + (e.response?.data?.detail || e.message))
    loading.value = false
  }
}

onMounted(() => {
  fetchSensors()
  fetchRuleSources()
})
</script>
