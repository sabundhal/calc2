<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col cols="12" sm="6" md="4">
        <v-card>
          <v-card-title class="text-h6 text-center">Логи Kubernetes</v-card-title>
          <v-card-text>
            <v-select
              v-model="selectedStand"
              :items="stands"
              label="Выберите стенд"
              @change="fetchPods"
              outlined
              dense
            ></v-select>
            <v-combobox
              v-model="selectedPod"
              label="Выберите pod"
              :items="pods"
              clearable
              outlined
              dense
              class="mt-4"
            ></v-combobox>
          </v-card-text>
          <v-card-actions class="justify-center flex-column">
            <v-btn :disabled="!isPodValid || loading" @click="downloadLogs" color="primary">
              Скачать логи
            </v-btn>
            <div v-if="loading" class="mt-2 text-caption">
              {{ downloadedSize }} MB загружено
            </div>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      stands: ['dev', 'test'],
      selectedStand: localStorage.getItem('selectedStand') || 'dev',
      pods: [],
      selectedPod: null,
      loading: false,
      downloadedSize: 0,
    };
  },
  computed: {
    isPodValid() {
      return this.pods.includes(this.selectedPod);
    }
  },
  watch: {
    selectedStand() {
      localStorage.setItem('selectedStand', this.selectedStand);
      this.fetchPods();
    }
  },
  methods: {
    async fetchPods() {
      try {
        const response = await axios.get(`/api/kubernetes/pods?stand=${this.selectedStand}`);
        this.pods = [...new Set(response.data)];
        this.selectedPod = null;
      } catch (error) {
        console.error('Ошибка при получении pod:', error);
      }
    },
    async downloadLogs() {
      if (!this.selectedPod) return;
      this.loading = true;
      this.downloadedSize = 0;
      try {
        const response = await axios.get(`/api/kubernetes/logs?stand=${this.selectedStand}&podShortName=${this.selectedPod}`, {
          responseType: 'blob',
          onDownloadProgress: (progressEvent) => {
            this.downloadedSize = (progressEvent.loaded / (1024 * 1024)).toFixed(2);
          }
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${this.selectedPod}_logs.log`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (error) {
        console.error('Ошибка при скачивании логов:', error);
      } finally {
        this.loading = false;
      }
    },
  },
  mounted() {
    this.fetchPods();
  },
};
</script>