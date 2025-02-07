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
            <optgroup label="Analgesics">
              <option value="Paracetamol120">Paracetamol 120mg/5mL (15mg/kg)</option>
              <option value="Paracetamol250">Paracetamol 250mg/5mL (15mg/kg)</option>
              <option value="Ibuprofen100">Ibuprofen 100mg/5mL (5-10mg/kg)</option>
            </optgroup>
            <optgroup label="Antibiotics">
              <option value="Amoxicillin125">Amoxicillin 125mg/5mL (15-30mg/kg)</option>
              <option value="Amoxicillin250">Amoxicillin 250mg/5mL (15-30mg/kg)</option>
              <option value="Cefaclor125">Cefaclor 125mg/5mL (10mg/kg)</option>
              <option value="Cefalexin125multi">Cefalexin 125mg/5mL (12.5-25mg/kg)</option>
              <option value="Cefalexin250multi">Cefalexin 250mg/5mL (12.5-25 mg/kg)</option>
              <option value="Coamoxiclav125-31.25">Coamoxiclav 125-31.25mg/5mL (15mg/kg)</option>
              <option value="Coamoxiclav250-62.5">Coamoxiclav 250-62.5mg/5mL (15mg/kg)</option>
              <option value="Cotrimoxazole480">Cotrimoxazole 240mg/5mL (24mg/kg)</option>
              <option value="Erythromycin200">Erythromycin 200mg/5mL (10-12.5mg/kg)</option>
              <option value="Erythromycin400">Erythromycin 400mg/5mL (10-12.5mg/kg)</option>
              <option value="Flucloxacillin125">Flucloxacillin 125mg/5mL (12.5mg/kg)</option>
              <option value="Flucloxacillin250">Flucloxacillin 250mg/5mL (12.5mg/kg)</option>
              <option value="Penicillin125">Phenoxymethylpenicillin 125mg/5mL (6.25-12.5mg/kg)</option>
              <option value="Penicillin250">Phenoxymethylpenicillin 250mg/5mL (6.25-12.5mg/kg)</option>
              <option value="Roxithromycin">Roxithromycin 50mg tablets (weight based)</option>
            </optgroup>
            <optgroup label="Other">
              <option value="Lactulose">Lactulose (0.5mL/kg)</option>
              <option value="Loratadine">Loratadine 1mg/1mL (age/weight based)</option>
              <option value="Macrogol">Macrogol 13.12g/sachet (0.5-1.5g/kg)</option>
              <option value="Prednisolone">Prednisolone 5mg/1mL (1-2mg/kg)</option>
              <option value="Ferrous_sulphate">Ferrous sulphate 30mg/1mL (0.5-1mg/kg)</option>
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
export default {
  name: 'PediatricCalculator',
  data() {
    return {
      weight: null,
      selectedDrug: 'None',
    };
  },
  methods: {
    validate() {
      // Логика для валидации и расчета дозы
      console.log('Weight:', this.weight);
      console.log('Selected Drug:', this.selectedDrug);
      // Добавьте вашу логику расчета здесь
    },
    clearResults() {
      // Очистка результатов
      document.getElementById('Result').innerText = '';
      document.getElementById('ResultMgs').innerText = '';
    },
    copyToClipboard(elementId) {
      const text = document.getElementById(elementId).innerText;
      navigator.clipboard.writeText(text).then(() => {
        console.log('Text copied to clipboard');
      });
    },
  },
};
</script>

<style scoped>
/* Добавьте ваши стили здесь */
@import '../assets/calculator-style.css';
</style>