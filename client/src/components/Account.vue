<template>
  <v-container>
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="10">
          <h1 class="text-h5 text-center">Счета</h1>
          <v-divider class="my-4"></v-divider>

          <!-- Кнопки -->
          <v-btn class="mr-3" @click="toggleAddAccountModal">
            Добавить счет
          </v-btn>
          <v-btn @click="fetchAccounts">
            Обновить
          </v-btn>

          <!-- Таблица -->
          <v-data-table
            :headers="headers"
            :items="accountActual"
            item-value="id"
            class="elevation-1 my-4"
            dense
          >
            <template #item="{ item }">
              <tr>
                <td>{{ item.name }}</td>
                <td>{{ item.id }}</td>
                <td>{{ item.accountReportPeriod }}</td>
                <td>{{ item.currentVersionRevision }}</td>
                <td>{{ item.currentState }}</td>
                <td>
                  <v-icon color="blue" @click="toggleEditAccountModal(item)">
                    mdi-pencil
                  </v-icon>
                  <v-icon color="red" @click="handleDeleteAccount(item)">
                    mdi-delete
                  </v-icon>
                  <v-btn class="ml-3" @click="handleResetAccount(item)">
                    Сбросить
                  </v-btn>
                </td>
              </tr>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>


    <!-- Модальное окно добавления -->
    <v-dialog v-model="activeAddAccountModal" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="text-h6">Добавить новый счет</span>
        </v-card-title>
        <v-card-text>
          <v-form>
            <v-text-field
              v-model="accountForm.name"
              label="Название счета"
              outlined
            ></v-text-field>
            <v-combobox
              v-model="accountForm.id"
              label="ID счета"
              :items="accountIds"
            ></v-combobox>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" @click="handleAddSubmit">
            Сохранить
          </v-btn>
          <v-btn color="red" @click="toggleAddAccountModal">
            Закрыть
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Модальное окно редактирования -->
    <v-dialog v-model="activeEditAccountModal" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="text-h6">Редактировать счет</span>
        </v-card-title>
        <v-card-text>
          <v-form>
            <v-text-field
              v-model="accountForm.name"
              label="Название счета"
              outlined
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" @click="handleEditSubmit">
            Сохранить
          </v-btn>
          <v-btn color="red" @click="toggleEditAccountModal">
            Закрыть
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      message: "",
      accounts: [],
      accountFilters: [],
      accountActual: [],
      activeAddAccountModal: false,
      activeEditAccountModal: false,
      headers: [
        { title: 'Название', key: 'name' },
        { title: 'ID', key: 'id' },
        { title: 'Отчетный период', key: 'account_report_period' },
        { title: 'Текущая версия', key: 'current_version_revision' },
        { title: 'Текущее состояние', key: 'current_state' },
        { title: 'Действия', key: 'actions', sortable: false },
      ],
      accountForm: {
        name: "",
        id: "",
      },
    };
  },
  computed: {
    accountIds() {
      return this.accounts.map(account => account.id);
    },
  },
  watch: {
    accountFilters: {
      handler(newVal, oldVal) {
        this.mergeAccountFilters();
      },
      deep: true,
    },
    accounts: {
      handler(newVal, oldVal) {
        this.mergeAccountFilters();
      },
      deep: true,
    },
  },
  methods: {
    async fetchAccounts() {
      try {
        const response = await axios.get("http://localhost:8080/api/account/lock?stand=dev");
        this.accounts = response.data;
        this.mergeAccountFilters();
      } catch (error) {
        console.error("Ошибка загрузки счетов:", error);
      }
    },
    mergeAccountFilters() {
      this.accountActual = [];
      this.accountFilters.forEach((filter) => {
        const account = this.accounts.find(acc => acc.id === filter.id);
        this.accountActual.push({
          ...filter,
          ...(account || {}),
        });
      });
    },
    toggleAddAccountModal() {
      this.accountForm = { name: "", id: "" };
      this.activeAddAccountModal = !this.activeAddAccountModal;
    },
    toggleEditAccountModal(account = null) {
      if (account) {
        this.accountForm = { ...account };
      }
      this.activeEditAccountModal = !this.activeEditAccountModal;
    },

    async handleAddSubmit() {
      if (!this.accountForm.name || !this.accountForm.id) {
        this.message = "Все поля должны быть заполнены!";
        return;
      }
      this.accountFilters.push({ ...this.accountForm });
      this.saveAccountFiltersToStorage();
      this.toggleAddAccountModal();
    },
    async handleEditSubmit() {
      const index = this.accountFilters.findIndex((acc) => acc.id === this.accountForm.id);
      if (index !== -1) {
        this.accountFilters.splice(index, 1, { ...this.accountForm });
      }
      this.saveAccountFiltersToStorage();
      this.toggleEditAccountModal();
    },

    async handleDeleteAccount(account) {
      const index = this.accountFilters.findIndex((acc) => acc.id === account.id);
      if (index !== -1) {
        this.accountFilters.splice(index, 1);
      }
      this.saveAccountFiltersToStorage();
    },
    async handleResetAccount(account) {
      try {
        const response = await axios.patch("http://localhost:8080/api/account/lock?stand=dev", {
          id: account.id,
        });
        const updatedAccount = response.data;
        const index = this.accounts.findIndex((acc) => acc.id === updatedAccount.id);
        if (index !== -1) {
          this.accounts.splice(index, 1, updatedAccount);
        }
        this.message = `Счет с ID ${updatedAccount.id} успешно сброшен.`;
      } catch (error) {
        console.error("Ошибка сброса счета:", error);
      }
    },
      loadAccountFiltersFromStorage() {
      const savedFilters = localStorage.getItem('accountFilters');
      this.accountFilters = savedFilters ? JSON.parse(savedFilters) : [];
    },
      saveAccountFiltersToStorage() {
      localStorage.setItem('accountFilters', JSON.stringify(this.accountFilters));
    },

  },
  mounted() {
    this.loadAccountFiltersFromStorage();
    this.fetchAccounts();
  },
};
</script>

<style scoped>
.modal-backdrop {
  display: none !important;
}
</style>
