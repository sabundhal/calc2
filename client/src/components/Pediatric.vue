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

        <div class="weight__section">
          <div class="weight__section-item weight__section-label">Weight (kg)</div>
          <input
            class="weight__section-item weight__section-input"
            id="theweight"
            v-model="weight"
            min="1"
            max="100"
            type="number"
            @click="clearResults"
            @select="clearResults"
          />
        </div>

     <div class="drug__section">
  <select id="drug" v-model="selectedDrug" @change="validate">
    <option value="None">Select Drug</option>
    <optgroup v-for="(drugs, category) in drugsByCategories" :key="category" :label="category">
      <option v-for="drug in drugs" :key="drug.id" :value="drug.id">
        {{ drug.name }} <!-- Пояснение удалено -->
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
      selectedDrug: 'None',
      drugsByCategories: {}  // Для хранения данных, сгруппированных по категориям
    };
  },
  methods: {
    validate() {
      console.log('Selected Drug:', this.selectedDrug);
      // Ваша логика расчёта дозы
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
    }
  },
  created() {
    // Загружаем данные при создании компонента
    this.loadDrugs();
  }
};

</script>

<style scoped>
/* Добавьте ваши стили здесь */
@import '../assets/calculator-style.css';
</style>