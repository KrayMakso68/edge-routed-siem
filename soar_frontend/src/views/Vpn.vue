<template>
  <div class="bg-white dark:bg-kibana-dark_sidebar p-8 rounded border border-gray-200 dark:border-gray-700 shadow-sm">
    <div class="mb-4">
      <h2 class="text-xl font-bold text-gray-800 dark:text-gray-100">{{ $t('vpn.title') }}</h2>
    </div>

    <!-- Actions -->
    <div class="flex space-x-3 mb-6">
      <button @click="showAddModal = true" class="bg-blue-600 hover:bg-blue-700 text-white py-1.5 px-4 rounded text-sm font-medium transition-colors">
        + {{ $t('vpn.create') }}
      </button>
      <button @click="downloadSelectedProfile" :disabled="selected.length !== 1" class="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white py-1.5 px-4 rounded text-sm font-medium transition-colors">
        {{ $t('common.download') }}
      </button>
      <button @click="executeRevoke" :disabled="selected.length === 0 || isProcessing" class="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white py-1.5 px-4 rounded text-sm font-medium transition-colors">
        {{ isProcessing ? $t('vpn.revoking') : $t('vpn.revoke') }}
      </button>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th class="w-12 px-4 py-3"><input type="checkbox" @change="toggleAll" :checked="selected.length === certs.length && certs.length > 0" class="rounded border-gray-300"></th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('vpn.name') }}</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('vpn.status') }}</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{{ $t('vpn.serial') }}</th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-kibana-dark_sidebar divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-if="certs.length === 0">
            <td colspan="4" class="px-4 py-6 text-center text-sm text-gray-500">{{ $t('vpn.empty') }}</td>
          </tr>
          <tr v-for="c in certs" :key="c.name" class="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer" @click="toggleSelect(c.name)">
            <td class="px-4 py-3 text-center" @click.stop><input type="checkbox" :value="c.name" v-model="selected" class="rounded border-gray-300" :disabled="c.status !== 'Valid'"></td>
            <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-200">{{ c.name }}</td>
            <td class="px-4 py-3 text-sm">
              <span :class="{'text-green-600 bg-green-100': c.status === 'Valid', 'text-red-600 bg-red-100': c.status === 'Revoked'}" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full dark:bg-opacity-20">
                {{ c.status === 'Valid' ? $t('vpn.status_valid') : $t('vpn.status_revoked') }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 font-mono">{{ c.serial }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create Profile Modal -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-96">
        <h3 class="text-lg font-bold mb-4 text-gray-800 dark:text-gray-100">{{ $t('vpn.create') }}</h3>
        <div class="space-y-3">
          <input v-model="newProfileName" :placeholder="$t('vpn.name')" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200" />
        </div>
        <div class="mt-6 flex justify-end space-x-3">
          <button @click="showAddModal = false" :disabled="isCreating" class="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">{{ $t('common.cancel') }}</button>
          <button @click="createProfile" :disabled="isCreating || !newProfileName" class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center">
            <span v-if="isCreating" class="mr-2">{{ $t('vpn.creating') }}</span>
            <span v-else>{{ $t('common.save') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'

const { t } = useI18n()

const certs = ref([])
const selected = ref([])
const showAddModal = ref(false)
const newProfileName = ref('')
const isCreating = ref(false)
const isProcessing = ref(false)

const fetchCerts = async () => {
  try {
    const res = await api.get('/api/vpn/certs')
    certs.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const toggleAll = (e) => {
  if (e.target.checked) {
    selected.value = certs.value.filter(c => c.status === 'Valid').map(c => c.name)
  } else {
    selected.value = []
  }
}

const toggleSelect = (name) => {
  const c = certs.value.find(x => x.name === name)
  if (c && c.status !== 'Valid') return;
  const index = selected.value.indexOf(name)
  if (index === -1) {
    selected.value.push(name)
  } else {
    selected.value.splice(index, 1)
  }
}

const createProfile = async () => {
  if (!newProfileName.value) return;
  isCreating.value = true
  try {
    const res = await api.post('/api/vpn/create', { name: newProfileName.value }, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${newProfileName.value}.ovpn`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    showAddModal.value = false
    newProfileName.value = ''
    fetchCerts()
  } catch (e) {
    console.error(e)
    if (e.response && e.response.data instanceof Blob) {
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const errMsg = JSON.parse(reader.result).detail;
          alert(t('vpn.err_create') + ": " + errMsg);
        } catch {
          alert(t('vpn.err_create'));
        }
      };
      reader.readAsText(e.response.data);
    } else {
      alert(t('vpn.err_create') + ": " + e.message);
    }
  } finally {
    isCreating.value = false
  }
}

const downloadSelectedProfile = async () => {
  if (selected.value.length !== 1) return;
  const name = selected.value[0];
  try {
    const res = await api.get(`/api/vpn/download/${name}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${name}.ovpn`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (e) {
    alert(t('vpn.err_download'))
  }
}

const executeRevoke = async () => {
  if (selected.value.length === 0) return;
  if (!confirm(t('vpn.confirm_revoke'))) return;
  isProcessing.value = true
  try {
    for (let name of selected.value) {
      await api.post('/api/vpn/revoke', { name })
    }
    selected.value = []
    fetchCerts()
  } catch (e) {
    console.error(e)
    const errMsg = e.response?.data?.detail || e.message
    alert(t('vpn.err_revoke') + ": " + errMsg)
  } finally {
    isProcessing.value = false
  }
}

onMounted(fetchCerts)
</script>
