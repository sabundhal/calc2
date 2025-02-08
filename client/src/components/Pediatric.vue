<template>
  <div id="calculator">
    <div class="title__section">
      <div class="title__section__image title__section-item">
        <img id="calcicon" src="https://www.jackofallorgans.com/wp-content/uploads/2017/12/SyrupBottle2.png" alt="Calculator Icon" />
      </div>
      <div class="title__section-label title__section-item">Paediatric Dose Calculator</div>
    </div>

    <div class="drug_calc">
      <form id="drugform" @submit.prevent="validate">
        <div class="error__section" id="warning-message"></div>
        <div class="error__section" id="error-message"></div>


    <!-- Вес -->
    <div class="weight__section">
      <div class="weight__section-item weight__section-label">Weight (kg)</div>
      <input
        class="weight__section-item weight__section-input"
        id="theweight"
        v-model="weight"
        min="1"
        max="100"
        type="number"
        ref="weightInput"
        @click="clearResults"
        @select="clearResults"
      />
    </div>

     <!-- Выбор препарата -->
    <div class="drug__section">
      <select id="drug" ref="drugIdInput" v-model="selectedDrug" @change="validate">
        <option value="None">Select Drug</option>
        <optgroup v-for="(drugs, category) in drugsByCategories" :key="category" :label="category">
          <option v-for="drug in drugs" :key="drug.id" :value="drug.id">
            {{ drug.name }}
          </option>
        </optgroup>
      </select>
    </div>

        <div class="calculate__section">
          <input type="button" id="calcbutton" value="Calculate" @click="validate" />
        </div>

        <div class="result__section">
          <div class="result__section-mls">
            <div class="result__section-mls-item result__section-mls-label">Dose <br /> in millilitres</div>
            <div class="result__section-mls-item result__section-mls-result" id="Result" style="display: block"></div>
            <button class="result__section-mls-item clipboard btn tippy copy" data-tippy-content="Copied to Clipboard" title="Copy to Clipboard" @click="copyToClipboard('Result')">
              <i class="far fa-clipboard"></i>
            </button>
          </div>
          <div class="result__section-mgs">
            <div class="result__section-mgs-item result__section-mgs-label">Dose <br /> in milligrams</div>
            <div class="result__section-mgs-item result__section-mgs-result" id="ResultMgs" style="display: block"></div>
            <button class="result__section-mgs-item clipboard btn tippy copy" data-tippy-content="Copied to Clipboard" title="Copy to Clipboard" @click="copyToClipboard('ResultMgs')">
              <i class="far fa-clipboard"></i>
            </button>
          </div>
        </div>
      </form>
    </div>
        <!-- Сообщения об ошибках -->
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <div class="message__section-dosing" id="dosing-section" style="display: none">
      <div class="message__section-dosing-item message__section-dosing-label" id="instructions"></div>
    </div>

    <div class="calculator__footer">
      <div class="calculator__footer-item calculator__footer-information">Further Information:</div>
      <div class="tippy" data-tippy="NZ Formulary">
        <a class="calculator__footer-item" href="https://nzfchildren.org.nz" target="_blank" id="nzflink">
          <img border="0" alt="nzf" src="https://www.jackofallorgans.com/wp-content/uploads/2018/11/nzf.png" width="32" height="32" />
        </a>
      </div>
      <div class="tippy" data-tippy="BPAC Antibiotic Guide">
        <a class="calculator__footer-item" href="https://bpac.org.nz/antibiotics/guide.aspx" target="_blank">
          <img border="0" alt="nzf" src="https://www.jackofallorgans.com/wp-content/uploads/2018/11/bpac-1.png" width="32" height="32" />
        </a>
      </div>
      <div class="tippy" data-tippy="Antimicrobial Susceptibility Report for 2017">
        <a class="calculator__footer-item" href="https://www.jackofallorgans.com/wp-content/uploads/AST-2017-Table-1.pdf" target="_blank">
          <img border="0" alt="nzf" src="https://www.jackofallorgans.com/wp-content/uploads/labtest-logo.png" width="32" height="32" />
        </a>
      </div>
    </div>

    <div class="calculator__author">
      <div class="calculator__author-item calculator__author-information">
        Calculator written by Dr Jeremy Steinberg, GP. <a href="https://www.jackofallorgans.com/contact" target="_blank">Contact</a> for suggestions
      </div>
    </div>
  </div>

</template>

<script>
import axios from 'axios';

export default {
  name: 'PediatricCalculator',
  data() {
    return {
      weight: "",
      selectedDrug: "None",
      drugsByCategories: {}, // Данные, сгруппированные по категориям
      mlsTotal: null,
      mgsTotal: null,
      errorMessage: "",
      warningMessage: "",
      weightBorder: "1px solid #cacaca",
      drugBorder: "1px solid #cacaca",
    };
  },
  methods: {
    calculateDosage() {
    const drugId = this.$refs.drugIdInput.value;
    const weight = this.$refs.weightInput.value;

    if (!drugId || !weight) {
      this.error = 'Пожалуйста, заполните все поля.';
      return;
    }

    fetch('/api/calculate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: `${localStorage.getItem('user_id')}`,
        drug_id: drugId,
        weight: weight
      })
    })
    .then(response => response.json())
    .then(data => {
      this.result = data;
    })
    .catch(error => {
      this.error = 'Ошибка при выполнении запроса: ' + error.message;
    });
  },
    validate() {
     console.log('Validate method called'); // Лог для проверки
      this.clearErrors();

      if (this.weight === "") {
        this.showError("Please input a weight", "weight");
      } else if (this.weight < 0) {
        this.showError("Cannot be negative weight.", "weight");
      } else if (this.weight > 100) {
        console.log('Validate 100'); // Лог для проверки
        this.showError("Please enter a weight below 100kg.", "weight");
      } else if (this.selectedDrug === "None") {
        this.showError("Please select a drug", "drug");
      } else {
         // Если валидация прошла успешно, вызываем расчет
      this.calculateDosage();
      }
    },

    showError(message, field) {
      this.errorMessage = message;

      if (field === "weight") {
        this.weightBorder = "1px solid red";
      } else if (field === "drug") {
        this.drugBorder = "1px solid red";
      }
    },
    clearErrors() {
      this.errorMessage = "";
      this.weightBorder = "1px solid #cacaca";
      this.drugBorder = "1px solid #cacaca";
    },
    clearResults() {
      this.mlsTotal = null;
      this.mgsTotal = null;
    },
    calculateMlsTotal() {
      // Пример расчета (замените на вашу логику)
      this.mlsTotal = this.weight * 2; // Пример: 2 мл на каждый кг
    },
    calculateMgsTotal() {
      // Пример расчета (замените на вашу логику)
      this.mgsTotal = this.weight * 5; // Пример: 5 мг на каждый кг
    },
    copyToClipboard(elementId) {
      const element = document.getElementById(elementId);
      if (element) {
        const text = element.innerText;
        navigator.clipboard.writeText(text);
      }
    },
    loadDrugs() {
      // Загружаем данные из API
      axios.get('/api/drugs')
        .then(response => {
          this.drugsByCategories = response.data;
        })
        .catch(error => {
          console.error('Error fetching drugs:', error);
        });
    },
  },
  created() {
    // Загружаем данные при создании компонента
    this.loadDrugs();
  },

};

</script>
<style scoped>
/* Добавьте ваши стили здесь */
@import '../assets/calculator-style.css';
</style>