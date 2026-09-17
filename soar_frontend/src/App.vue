<template>
  <div :class="{ dark: isDark }" class="min-h-screen flex">
    <aside class="w-56 flex-shrink-0 bg-kibana-sidebar dark:bg-kibana-dark_sidebar border-r border-kibana-border dark:border-gray-700 flex flex-col shadow-sm">
      <div class="h-16 flex items-center px-6 border-b border-kibana-border dark:border-gray-700">
        <span class="font-bold text-xl tracking-tight text-kibana-primary">
          SOAR<span class="text-kibana-text dark:text-gray-200">Panel</span>
        </span>
      </div>
      <nav class="flex-1 px-4 py-6 space-y-2">
        <router-link to="/" class="block px-4 py-2 rounded text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-kibana-primary transition-colors" active-class="bg-gray-100 dark:bg-gray-800 text-kibana-primary font-semibold">
          {{ $t('menu.dashboard') }}
        </router-link>
        <router-link to="/sensors" class="block px-4 py-2 rounded text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-kibana-primary transition-colors" active-class="bg-gray-100 dark:bg-gray-800 text-kibana-primary font-semibold">
          {{ $t('menu.sensors') }}
        </router-link>
        <router-link to="/rules" class="block px-4 py-2 rounded text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-kibana-primary transition-colors" active-class="bg-gray-100 dark:bg-gray-800 text-kibana-primary font-semibold">
          {{ $t('menu.rules') }}
        </router-link>
        <router-link to="/rule-sources" class="block px-4 py-2 rounded text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-kibana-primary transition-colors" active-class="bg-gray-100 dark:bg-gray-800 text-kibana-primary font-semibold">
          {{ $t('menu.rule_sources') }}
        </router-link>
        <router-link to="/pcap" class="block px-4 py-2 rounded text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-kibana-primary transition-colors" active-class="bg-gray-100 dark:bg-gray-800 text-kibana-primary font-semibold">
          {{ $t('menu.pcap') }}
        </router-link>
        <router-link to="/vpn" class="block px-4 py-2 rounded text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-kibana-primary transition-colors" active-class="bg-gray-100 dark:bg-gray-800 text-kibana-primary font-semibold">
          {{ $t('menu.vpn') }}
        </router-link>
      </nav>
    </aside>

    <main class="flex-1 flex flex-col bg-kibana-bg dark:bg-kibana-dark_bg">
      <header class="h-16 bg-white dark:bg-kibana-dark_sidebar border-b border-kibana-border dark:border-gray-700 flex items-center justify-between px-8 shadow-sm">
        <h1 class="text-lg font-semibold text-gray-800 dark:text-gray-100">{{ $t('header.title') }}</h1>
        <div class="flex items-center space-x-3">
          <button @click="toggleTheme" class="px-3 py-1 text-sm font-medium border border-kibana-border dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors">
            {{ isDark ? $t('header.theme_light') : $t('header.theme_dark') }}
          </button>
          <button @click="toggleLanguage" class="px-3 py-1 text-sm font-medium border border-kibana-border dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors">
            {{ $t('header.lang') }}
          </button>
        </div>
      </header>

      <div class="p-8">
        <router-view></router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { locale } = useI18n()
const isDark = ref(false)
const toggleLanguage = () => { locale.value = locale.value === 'ru' ? 'en' : 'ru' }
const toggleTheme = () => { isDark.value = !isDark.value }
</script>
