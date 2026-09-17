<template>
  <div class="bg-white dark:bg-kibana-dark_sidebar p-8 rounded border border-gray-200 dark:border-gray-700 shadow-sm">
    <!-- Title Row -->
    <div class="mb-4">
      <h2 class="text-xl font-bold text-gray-800 dark:text-gray-100">{{ $t('rule_sources.title') }}</h2>
    </div>

    <!-- Action Buttons Row -->
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

    <!-- Таблица источников правил -->
    <div class="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th class="w-12 px-4 py-3"><input type="checkbox" @change="toggleAll" :checked="selected.length === sources.length && sources.length > 0" class="rounded border-gray-300"></th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('rule_sources.name') }}</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('rule_sources.url') }}</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('rule_sources.branch') }}</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('rule_sources.path') }}</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('sensors.desc') }}</th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-kibana-dark_sidebar divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-if="loading">
            <td colspan="6" class="px-4 py-6 text-center text-sm text-gray-500">{{ $t('common.loading') }}</td>
          </tr>
          <tr v-else-if="sources.length === 0">
            <td colspan="6" class="px-4 py-6 text-center text-sm text-gray-500">{{ $t('rule_sources.empty') }}</td>
          </tr>
          <tr v-for="s in sources" :key="s.id" class="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer" @click="toggleSelect(s.id)">
            <td class="px-4 py-3 text-center" @click.stop><input type="checkbox" :value="s.id" v-model="selected" class="rounded border-gray-300"></td>
            <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-200">{{ s.name }}</td>
            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 font-mono break-all">{{ s.url }}</td>
            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 font-mono">{{ s.branch || 'main' }}</td>
            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 font-mono">{{ s.rules_path || '(все .rules файлы)' }}</td>
            <td class="px-4 py-3 text-sm text-gray-500 dark:text-gray-500">{{ s.description }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Модальное окно добавления / редактирования -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-[450px]">
        <h3 class="text-lg font-bold mb-4 text-gray-800 dark:text-gray-100">{{ isEdit ? $t('rule_sources.edit_source') : $t('rule_sources.add_new') }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase mb-1">{{ $t('rule_sources.name') }}</label>
            <input v-model="form.name" :placeholder="$t('rule_sources.name')" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase mb-1">{{ $t('rule_sources.url') }}</label>
            <input v-model="form.url" :placeholder="$t('rule_sources.url')" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase mb-1">{{ $t('rule_sources.branch') }}</label>
              <input v-model="form.branch" placeholder="main" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase mb-1">{{ $t('rule_sources.path') }}</label>
              <input v-model="form.rules_path" placeholder="custom.rules" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase mb-1">{{ $t('sensors.desc') }}</label>
            <input v-model="form.description" :placeholder="$t('sensors.desc')" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500" />
          </div>
        </div>
        <div class="mt-6 flex justify-end space-x-3">
          <button @click="showModal = false" class="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">{{ $t('common.cancel') }}</button>
          <button @click="saveSource" :disabled="!form.name || !form.url" class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">{{ $t('common.save') }}</button>
        </div>
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
const sources = ref([])
const selected = ref([])
const loading = ref(false)

const showModal = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const form = ref({ name: '', url: '', branch: 'main', rules_path: '', description: '' })

const showDeleteConfirm = ref(false)

const fetchSources = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/suricata/sources/')
    sources.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const toggleAll = (e) => {
  selected.value = e.target.checked ? sources.value.map(s => s.id) : []
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
  form.value = { name: '', url: '', branch: 'main', rules_path: '', description: '' }
  showModal.value = true
}

const openEditModal = () => {
  if (selected.value.length !== 1) return;
  const source = sources.value.find(s => s.id === selected.value[0])
  if (source) {
    isEdit.value = true
    editingId.value = source.id
    form.value = { ...source }
    showModal.value = true
  }
}

const saveSource = async () => {
  try {
    if (isEdit.value && editingId.value) {
      await api.put(`/api/suricata/sources/${editingId.value}`, form.value)
    } else {
      await api.post('/api/suricata/sources/', form.value)
    }
    showModal.value = false
    selected.value = []
    fetchSources()
  } catch (e) {
    alert(t('common.error') + ": " + (e.response?.data?.detail || e.message))
  }
}

const confirmDelete = () => {
  if (selected.value.length > 0) {
    showDeleteConfirm.value = true
  }
}

const executeDelete = async () => {
  showDeleteConfirm.value = false
  try {
    for (let id of selected.value) {
      await api.delete(`/api/suricata/sources/${id}`)
    }
    selected.value = []
    fetchSources()
  } catch (e) {
    alert(t('common.error') + ": " + e.message)
  }
}

onMounted(fetchSources)
</script>
