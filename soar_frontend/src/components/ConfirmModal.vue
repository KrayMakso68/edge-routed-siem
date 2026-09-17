<template>
  <Teleport to="body">
    <Transition name="confirm-fade">
      <div v-if="visible" class="fixed inset-0 z-[100] flex items-center justify-center" @click.self="onCancel">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
        <Transition name="confirm-scale">
          <div v-if="visible" class="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-[420px] overflow-hidden border border-gray-200 dark:border-gray-700">
            <!-- Colored top bar -->
            <div :class="barColor" class="h-1.5"></div>

            <div class="p-6">
              <!-- Icon + Title -->
              <div class="flex items-center space-x-3 mb-3">
                <div :class="iconBg" class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0">
                  <!-- Warning icon -->
                  <svg v-if="type === 'danger'" class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                  </svg>
                  <!-- Info icon -->
                  <svg v-else class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0Zm-9-3.75h.008v.008H12V8.25Z" />
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ title }}</h3>
              </div>

              <!-- Message -->
              <p class="text-sm text-gray-600 dark:text-gray-400 ml-[52px] mb-6">{{ message }}</p>

              <!-- Buttons -->
              <div class="flex justify-end space-x-3">
                <button
                  @click="onCancel"
                  class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                >{{ cancelText }}</button>
                <button
                  @click="onConfirm"
                  :class="confirmBtnClass"
                  class="px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors"
                >{{ confirmText }}</button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: '' },
  message: { type: String, default: '' },
  confirmText: { type: String, default: 'OK' },
  cancelText: { type: String, default: 'Cancel' },
  type: { type: String, default: 'danger' } // 'danger' | 'info'
})

const emit = defineEmits(['confirm', 'cancel'])

const barColor = computed(() => props.type === 'danger' ? 'bg-red-500' : 'bg-blue-500')
const iconBg = computed(() => props.type === 'danger' ? 'bg-red-100 dark:bg-red-900/30' : 'bg-blue-100 dark:bg-blue-900/30')
const confirmBtnClass = computed(() => props.type === 'danger'
  ? 'bg-red-600 hover:bg-red-700'
  : 'bg-blue-600 hover:bg-blue-700'
)

const onConfirm = () => emit('confirm')
const onCancel = () => emit('cancel')
</script>

<style scoped>
.confirm-fade-enter-active,
.confirm-fade-leave-active {
  transition: opacity 0.2s ease;
}
.confirm-fade-enter-from,
.confirm-fade-leave-to {
  opacity: 0;
}
.confirm-scale-enter-active {
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.confirm-scale-leave-active {
  transition: all 0.15s ease-in;
}
.confirm-scale-enter-from {
  opacity: 0;
  transform: scale(0.9);
}
.confirm-scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
