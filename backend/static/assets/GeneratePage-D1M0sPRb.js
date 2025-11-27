var S=Object.defineProperty;var F=(i,e,t)=>e in i?S(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t;var u=(i,e,t)=>F(i,typeof e!="symbol"?e+"":e,t);import{a as h,c as D,b as m,r as y}from"./index-CqQJt02h.js";const w={async generateDocument(i){const e=new FormData;return e.append("description",i.description),e.append("length",i.length.toString()),e.append("document_type",i.document_type),e.append("use_watermark",i.use_watermark.toString()),e.append("statistics",JSON.stringify(i.statistics)),e.append("design_spec",JSON.stringify(i.design_spec)),i.logo&&e.append("logo",i.logo),(await h.post("/generate/document",e,{headers:{"Content-Type":"multipart/form-data"}})).data},async getJobStatus(i){return(await h.get(`/generate/status/${i}`)).data},async downloadDocument(i){return(await h.get(`/generate/download/${i}`,{responseType:"blob"})).data},async listDocuments(){return(await h.get("/documents")).data},async getDocument(i){return(await h.get(`/documents/${i}`)).data},async deleteDocument(i){await h.delete(`/documents/${i}`)}},T=i=>!i||i.trim().length<10?"Description must be at least 10 characters":i.length>2e3?"Description must be less than 2000 characters":null,M=i=>i<500?"Document length must be at least 500 words":i>1e4?"Document length must not exceed 10,000 words":null,_=(i,e,t)=>!i||i.trim().length===0?"Statistic name is required":i.length>100?"Statistic name must be less than 100 characters":isNaN(e)?"Statistic value must be a number":t&&t.length>20?"Unit must be less than 20 characters":null,C=i=>{const e=parseInt("5242880"),t="image/png,image/jpeg,image/svg+xml".split(",");return i.size>e?`File size must be less than ${(e/1024/1024).toFixed(1)}MB`:t.includes(i.type)?null:"Invalid file format. Allowed: PNG, JPG, SVG"},E=[{name:"Ocean Blue",background:"#FFFFFF",foreground1:"#2563EB",foreground2:"#06B6D4"},{name:"Corporate Red",background:"#FFFFFF",foreground1:"#DC2626",foreground2:"#F97316"},{name:"Forest Green",background:"#FFFFFF",foreground1:"#059669",foreground2:"#14B8A6"},{name:"Royal Purple",background:"#FFFFFF",foreground1:"#7C3AED",foreground2:"#EC4899"},{name:"Sunset Orange",background:"#FFFFFF",foreground1:"#EA580C",foreground2:"#EAB308"}];class ${constructor(e){u(this,"container");u(this,"selectedTheme");u(this,"onChangeCallback");const t=document.getElementById(e);if(!t)throw new Error(`Element with id ${e} not found`);this.container=t,this.selectedTheme=E[0],this.render()}onChange(e){this.onChangeCallback=e}getSelectedTheme(){return{background_color:this.selectedTheme.background,foreground_color_1:this.selectedTheme.foreground1,foreground_color_2:this.selectedTheme.foreground2,theme_name:this.selectedTheme.name}}render(){this.container.innerHTML=`
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Color Theme
      </label>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        ${E.map((e,t)=>`
          <button
            type="button"
            data-theme-index="${t}"
            class="theme-option p-4 border-2 rounded-lg transition-all hover:shadow-lg ${t===0?"border-primary-500 bg-primary-50":"border-gray-200"}"
          >
            <div class="flex gap-2 mb-2">
              <div class="w-8 h-8 rounded" style="background-color: ${e.foreground1}"></div>
              <div class="w-8 h-8 rounded" style="background-color: ${e.foreground2}"></div>
            </div>
            <div class="text-xs font-medium text-gray-700">${e.name}</div>
          </button>
        `).join("")}
      </div>
    `,this.attachEventListeners()}attachEventListeners(){this.container.querySelectorAll(".theme-option").forEach(t=>{t.addEventListener("click",n=>{const s=n.currentTarget,o=parseInt(s.dataset.themeIndex||"0");this.selectTheme(o)})})}selectTheme(e){this.selectedTheme=E[e],this.container.querySelectorAll(".theme-option").forEach((n,s)=>{s===e?(n.classList.add("border-primary-500","bg-primary-50"),n.classList.remove("border-gray-200")):(n.classList.remove("border-primary-500","bg-primary-50"),n.classList.add("border-gray-200"))}),this.onChangeCallback&&this.onChangeCallback(this.getSelectedTheme())}}class A{constructor(e){u(this,"container");u(this,"statistics",[]);u(this,"nextId",1);const t=document.getElementById(e);if(!t)throw new Error(`Element with id ${e} not found`);this.container=t,this.render()}getStatistics(){return this.statistics}render(){this.container.innerHTML=`
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <label class="block text-sm font-medium text-gray-700">
            Company Statistics (Optional, max 10)
          </label>
          <button
            type="button"
            id="add-statistic-btn"
            class="px-3 py-1 text-sm bg-primary-600 text-white rounded hover:bg-primary-700 transition disabled:bg-gray-400"
            ${this.statistics.length>=10?"disabled":""}
          >
            + Add Statistic
          </button>
        </div>
        <div id="statistics-list" class="space-y-3">
          ${this.statistics.length===0?'<p class="text-sm text-gray-500 italic">No statistics added yet</p>':this.statistics.map(e=>this.renderStatistic(e)).join("")}
        </div>
      </div>
    `,this.attachEventListeners()}renderStatistic(e){return`
      <div class="statistic-item p-4 border border-gray-200 rounded-lg bg-gray-50" data-id="${e.id}">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Name</label>
            <input
              type="text"
              class="stat-name w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              value="${e.name}"
              placeholder="e.g., Revenue Growth"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Value</label>
            <input
              type="number"
              class="stat-value w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              value="${e.value}"
              step="0.01"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Unit</label>
            <input
              type="text"
              class="stat-unit w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              value="${e.unit||""}"
              placeholder="e.g., %, $M"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Chart Type</label>
            <div class="flex gap-2 items-center">
              <select class="stat-viz-type flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm">
                <option value="bar" ${e.visualization_type==="bar"?"selected":""}>Bar</option>
                <option value="line" ${e.visualization_type==="line"?"selected":""}>Line</option>
                <option value="pie" ${e.visualization_type==="pie"?"selected":""}>Pie</option>
                <option value="gauge" ${e.visualization_type==="gauge"?"selected":""}>Gauge</option>
              </select>
              <button
                type="button"
                class="remove-stat-btn px-2 py-2 text-red-600 hover:bg-red-50 rounded transition"
                title="Remove"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    `}attachEventListeners(){const e=document.getElementById("add-statistic-btn");e&&e.addEventListener("click",()=>this.addStatistic());const t=document.getElementById("statistics-list");t&&(t.addEventListener("click",n=>{const s=n.target;if(s.closest(".remove-stat-btn")){const o=s.closest(".statistic-item");o&&this.removeStatistic(o.dataset.id||"")}}),t.addEventListener("input",n=>{n.target.closest(".statistic-item")&&this.updateStatistics()}))}addStatistic(){if(this.statistics.length>=10)return;const e={id:`stat-${this.nextId++}`,name:"",value:0,unit:"",visualization_type:"bar"};this.statistics.push(e),this.render()}removeStatistic(e){this.statistics=this.statistics.filter(t=>t.id!==e),this.render()}updateStatistics(){this.container.querySelectorAll(".statistic-item").forEach(t=>{const n=t.dataset.id,s=this.statistics.find(o=>o.id===n);if(s){const o=t.querySelector(".stat-name"),r=t.querySelector(".stat-value"),l=t.querySelector(".stat-unit"),a=t.querySelector(".stat-viz-type");s.name=o.value,s.value=parseFloat(r.value)||0,s.unit=l.value||void 0,s.visualization_type=a.value}})}validate(){const e=[];return this.updateStatistics(),this.statistics.forEach((t,n)=>{const s=_(t.name,t.value,t.unit);s&&e.push(`Statistic ${n+1}: ${s}`)}),e}}class P{constructor(e){u(this,"form");u(this,"colorPalette");u(this,"statisticsForm");u(this,"currentJobId",null);u(this,"statusCheckInterval",null);const t=document.getElementById(e);if(!t||!(t instanceof HTMLFormElement))throw new Error(`Form with id ${e} not found`);this.form=t,this.colorPalette=new $("color-palette-container"),this.statisticsForm=new A("statistics-form-container"),this.attachEventListeners()}attachEventListeners(){this.form.addEventListener("submit",n=>{n.preventDefault(),this.handleSubmit()});const e=document.getElementById("logo-input");e&&e.addEventListener("change",n=>{var r;const o=(r=n.target.files)==null?void 0:r[0];this.updateFilePreview(o),this.updateWatermarkVisibility()});const t=document.getElementById("document-type-select");t&&t.addEventListener("change",()=>{this.updateWatermarkVisibility()})}updateWatermarkVisibility(){const e=document.getElementById("watermark-container");if(!e)return;const t=document.getElementById("document-type-select"),n=(t==null?void 0:t.value)||"infographic",s=document.getElementById("logo-input"),o=s.files&&s.files.length>0;if((n==="formal"||n==="invoice")&&o)e.classList.remove("hidden");else{e.classList.add("hidden");const r=document.getElementById("use-watermark");r&&(r.checked=!1)}}updateFilePreview(e){const t=document.getElementById("file-preview");if(t)if(e){const n=C(e);n?t.innerHTML=`<p class="text-sm text-red-600">${n}</p>`:t.innerHTML=`
          <p class="text-sm text-green-600">
            ✓ ${e.name} (${(e.size/1024).toFixed(1)} KB)
          </p>
        `}else t.innerHTML=""}async handleSubmit(){var x,k,I,L,B;this.clearErrors();const e=document.getElementById("description").value,t=parseInt(document.getElementById("length").value),s=(x=document.getElementById("logo-input").files)==null?void 0:x[0],o=document.getElementById("document-type-select"),r=(o==null?void 0:o.value)||"infographic",l=document.getElementById("use-watermark"),a=(l==null?void 0:l.checked)||!1,d=[],c=T(e);if(c&&d.push(c),r!=="invoice"){const g=M(t);g&&d.push(g)}if(s){const g=C(s);g&&d.push(g)}const p=this.statisticsForm.validate();if(d.push(...p),d.length>0){this.showErrors(d);return}const b={description:e,length:t,document_type:r,use_watermark:a,statistics:this.statisticsForm.getStatistics(),design_spec:this.colorPalette.getSelectedTheme(),logo:s};try{this.showLoading(!0);try{const f=await D.deductCredits(r),v=m.user;v&&m.setAuthenticated({...v,credits:f.new_balance}),console.log(`Credits deducted: ${f.credits_deducted}, New balance: ${f.new_balance}`)}catch(f){const v=((I=(k=f.response)==null?void 0:k.data)==null?void 0:I.detail)||"Failed to deduct credits";this.showErrors([v]),this.showLoading(!1);return}const g=await w.generateDocument(b);this.currentJobId=g.job_id,this.startStatusPolling()}catch(g){this.showErrors([((B=(L=g.response)==null?void 0:L.data)==null?void 0:B.detail)||"Failed to start document generation"]),this.showLoading(!1)}}startStatusPolling(){this.currentJobId&&(this.updateProgress(0,"Initializing..."),this.statusCheckInterval=window.setInterval(async()=>{if(this.currentJobId)try{const e=await w.getJobStatus(this.currentJobId);this.handleStatusUpdate(e)}catch(e){console.error("Failed to check status:",e)}},3e3))}handleStatusUpdate(e){this.updateProgress(e.progress,e.current_step),e.status==="completed"?(this.stopStatusPolling(),this.showSuccess(e.job_id)):e.status==="failed"&&(this.stopStatusPolling(),this.showErrors([e.error_message||"Document generation failed"]),this.showLoading(!1))}stopStatusPolling(){this.statusCheckInterval&&(clearInterval(this.statusCheckInterval),this.statusCheckInterval=null)}updateProgress(e,t){const n=document.getElementById("progress-bar"),s=document.getElementById("progress-text");n&&(n.style.width=`${e}%`),s&&(s.textContent=`${e}% - ${this.formatStep(t)}`)}formatStep(e){return{initializing:"Initializing...",generating_text:"Generating document text...",generating_images:"Creating AI images...",generating_visualizations:"Creating data visualizations...",assembling_pdf:"Assembling PDF document...",completed:"Completed!"}[e]||e}showSuccess(e){const t=document.getElementById("result-container");if(!t)return;t.innerHTML=`
      <div class="bg-green-50 border border-green-200 rounded-lg p-6">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-lg font-semibold text-green-800">Document Generated Successfully!</h3>
        </div>
        <button
          id="download-btn"
          class="px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition"
        >
          Download PDF
        </button>
      </div>
    `;const n=document.getElementById("download-btn");n&&n.addEventListener("click",()=>this.downloadPDF(e)),this.showLoading(!1)}async downloadPDF(e){var t,n;try{const s=await w.downloadDocument(e),o=window.URL.createObjectURL(s),r=document.createElement("a");r.href=o,r.download=`document-${Date.now()}.pdf`,document.body.appendChild(r),r.click(),window.URL.revokeObjectURL(o),document.body.removeChild(r)}catch(s){this.showErrors([((n=(t=s.response)==null?void 0:t.data)==null?void 0:n.detail)||"Failed to download PDF"])}}showLoading(e){const t=document.getElementById("loading-container"),n=document.getElementById("submit-btn");t&&t.classList.toggle("hidden",!e),n&&(n.disabled=e,n.textContent=e?"Generating...":"Generate Document")}showErrors(e){const t=document.getElementById("error-container");t&&(t.innerHTML=`
      <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-red-800 mb-2">Please fix the following errors:</h4>
        <ul class="list-disc list-inside space-y-1">
          ${e.map(n=>`<li class="text-sm text-red-600">${n}</li>`).join("")}
        </ul>
      </div>
    `,t.classList.remove("hidden"))}clearErrors(){const e=document.getElementById("error-container");e&&(e.classList.add("hidden"),e.innerHTML="");const t=document.getElementById("result-container");t&&(t.innerHTML="")}}class N{render(){const e=document.getElementById("app");if(!e)return;const t=document.getElementById("nav-container");t&&(t.style.display=""),e.innerHTML=`
      <div class="min-h-screen bg-gray-50 pb-12 pt-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <!-- Page Header -->
          <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">Generate Your Document</h1>
            <p class="text-xl text-gray-600">Create professional documents with AI in seconds</p>
          </div>

          <!-- Auth Warning (shown if not authenticated) -->
          ${m.isAuthenticated?"":`
            <div class="mb-8 bg-primary-50 border-l-4 border-primary-400 p-4 rounded-lg">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm text-primary-700">
                    <strong>Please log in to generate documents.</strong> You'll be redirected to the login page when you click "Generate Document". Don't have an account? <a href="/register" data-route="/register" class="font-semibold underline hover:text-primary-800">Sign up here</a>.
                  </p>
                </div>
              </div>
            </div>
          `}

          <!-- Document Generation Form Container -->
          <div class="bg-white rounded-lg shadow-md p-6 md:p-8">
            <form id="document-form" class="space-y-8">
              <!-- Document Description -->
              <div>
                <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
                  Document Description
                  <span class="text-red-500">*</span>
                </label>
                <textarea
                  id="description"
                  name="description"
                  rows="5"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition"
                  placeholder="Describe your document..."
                  required
                ></textarea>
                <div id="description-guide" class="mt-2 p-3 bg-primary-50 border border-primary-200 rounded-lg">
                  <p class="text-xs text-primary-900 font-medium mb-1">💡 Tips for best results:</p>
                  <p id="description-guide-text" class="text-xs text-primary-800 leading-relaxed"></p>
                </div>
                <p class="mt-2 text-xs text-gray-500">Minimum 10 characters, maximum 2000 characters</p>
              </div>

              <!-- Document Length -->
              <div id="length-container">
                <label for="length" class="block text-sm font-medium text-gray-700 mb-2">
                  Document Length (words)
                  <span class="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="length"
                  name="length"
                  min="500"
                  max="10000"
                  value="2000"
                  class="w-full md:w-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition"
                  required
                />
                <p class="mt-1 text-xs text-gray-500">Between 500 and 10,000 words</p>
              </div>

              <!-- Document Type -->
              <div>
                <label for="document-type-select" class="block text-sm font-medium text-gray-700 mb-2">
                  Document Type
                  <span class="text-red-500">*</span>
                </label>
                <select
                  id="document-type-select"
                  name="document_type"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition bg-white"
                  required
                >
                  <option value="formal">Formal Document - Text with decorative lines (⚡ ~60s, 34 credits)</option>
                  <option value="infographic" selected>Infographic Document - Text + AI images + charts (⏱️ ~120s, 52 credits)</option>
                  <option value="invoice">Invoice - Professional invoice with line items and totals (⚡ ~45s, 28 credits)</option>
                </select>
                <p class="mt-2 text-xs text-gray-600">
                  <strong>Formal:</strong> Professional text with decorative elements |
                  <strong>Infographic:</strong> Visual document with AI images and data charts |
                  <strong>Invoice:</strong> Structured billing document with itemized costs
                </p>
              </div>

              <!-- Company Logo -->
              <div>
                <label for="logo-input" class="block text-sm font-medium text-gray-700 mb-2">Company Logo (Optional)</label>
                <div class="flex items-center gap-4">
                  <label for="logo-input" class="px-4 py-2 bg-gray-100 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-200 transition text-sm font-medium text-gray-700">
                    Choose File
                  </label>
                  <input type="file" id="logo-input" name="logo" accept="image/png,image/jpeg,image/svg+xml" class="hidden" />
                  <div id="file-preview" class="flex-1"></div>
                </div>
                <p class="mt-1 text-xs text-gray-500">PNG, JPG, or SVG. Max 5MB</p>
              </div>

              <!-- Watermark Option -->
              <div id="watermark-container" class="hidden">
                <div class="flex items-center gap-3 p-4 bg-primary-50 border border-primary-200 rounded-lg">
                  <input type="checkbox" id="use-watermark" name="use_watermark" class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-2 focus:ring-primary-500" />
                  <label for="use-watermark" class="flex-1 cursor-pointer">
                    <span class="text-sm font-medium text-gray-900">Use logo as watermark</span>
                    <p class="text-xs text-gray-600 mt-1">Display your logo as a semi-transparent watermark on all pages (except cover)</p>
                  </label>
                </div>
              </div>

              <!-- Color Theme -->
              <div id="color-palette-container"></div>

              <!-- Statistics -->
              <div id="statistics-form-container"></div>

              <!-- Error Container -->
              <div id="error-container" class="hidden"></div>

              <!-- Insufficient Credits Warning -->
              <div id="insufficient-credits-warning" class="hidden bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div class="flex items-start">
                  <svg class="w-5 h-5 text-red-600 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                  <div class="flex-1">
                    <h3 class="text-sm font-medium text-red-800">Insufficient Credits</h3>
                    <p class="text-sm text-red-700 mt-1">
                      You don't have enough credits to generate this document. Please purchase more credits to continue.
                    </p>
                    <button
                      id="buy-credits-from-warning-btn"
                      class="mt-3 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700 transition-colors"
                    >
                      Buy Credits Now
                    </button>
                  </div>
                </div>
              </div>

              <!-- Submit Button -->
              <div class="flex justify-end">
                <button type="submit" id="submit-btn" class="btn-primary flex items-center gap-2">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Generate Document
                </button>
              </div>
            </form>

            <!-- Loading Container -->
            <div id="loading-container" class="hidden mt-8">
              <div class="bg-primary-50 border border-primary-200 rounded-lg p-6">
                <div class="flex items-center mb-4">
                  <svg class="animate-spin h-5 w-5 text-primary-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <h3 class="text-lg font-semibold text-primary-800">Generating Your Document</h3>
                </div>
                <div class="mb-3">
                  <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div id="progress-bar" class="bg-primary-600 h-3 rounded-full transition-all duration-300" style="width: 0%"></div>
                  </div>
                </div>
                <p id="progress-text" class="text-sm text-gray-700 font-medium">0% - Initializing...</p>
                <p class="text-xs text-gray-600 mt-4">This may take 1-3 minutes depending on document complexity. Please don't close this page.</p>
              </div>
            </div>

            <!-- Result Container -->
            <div id="result-container" class="mt-8"></div>
          </div>

          <!-- Download Modal (shown after generation for non-authenticated users) -->
          <div id="auth-required-modal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div class="mt-3 text-center">
                <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-primary-100">
                  <svg class="h-6 w-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 class="text-lg leading-6 font-medium text-gray-900 mt-5">Document Generated!</h3>
                <div class="mt-2 px-7 py-3">
                  <p class="text-sm text-gray-500">
                    Your document has been generated successfully. Create an account to download it and save it to your library.
                  </p>
                </div>
                <div class="items-center px-4 py-3 space-y-3">
                  <button
                    id="modal-register-btn"
                    class="px-4 py-2 bg-primary-600 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    Create Account
                  </button>
                  <button
                    id="modal-login-btn"
                    class="px-4 py-2 bg-white text-gray-700 text-base font-medium rounded-md w-full border border-gray-300 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    I Have an Account
                  </button>
                  <button
                    id="modal-close-btn"
                    class="px-4 py-2 bg-white text-gray-500 text-sm font-medium rounded-md w-full hover:text-gray-700"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- No Logo Modal -->
          <div id="no-logo-modal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
              <div class="mt-3">
                <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
                  <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <h3 class="text-lg leading-6 font-medium text-gray-900 mt-4 text-center">No Logo Uploaded</h3>
                <div class="mt-3 px-4 py-3">
                  <p class="text-sm text-gray-600 text-center">
                    You haven't uploaded a company logo yet. Documents with business logos appear more professional and strengthen your brand identity.
                  </p>
                  <p class="text-sm text-gray-600 text-center mt-3">
                    Would you like to go back and add a logo, or continue without one?
                  </p>
                </div>
                <div class="items-center px-4 py-3 space-y-2">
                  <button
                    id="modal-add-logo-btn"
                    class="px-4 py-2 bg-primary-600 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors"
                  >
                    Add Logo
                  </button>
                  <button
                    id="modal-continue-without-logo-btn"
                    class="px-4 py-2 bg-white text-gray-700 text-base font-medium rounded-md w-full border border-gray-300 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
                  >
                    Continue Without Logo
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;try{new P("document-form")}catch(n){console.error("Failed to initialize document form:",n)}this.attachEventListeners(),this.setupGenerationListener(),this.restoreFormData(),this.setupCreditsCheck(),this.setupDescriptionGuide(),this.setupWatermarkToggle(),this.setupLengthVisibility()}attachEventListeners(){const e=document.getElementById("buy-credits-from-warning-btn");e&&e.addEventListener("click",()=>{window.dispatchEvent(new CustomEvent("open-credits-modal"))});const t=document.getElementById("document-form");t&&t.addEventListener("submit",a=>{if(!m.isAuthenticated)return a.preventDefault(),a.stopPropagation(),a.stopImmediatePropagation(),this.saveFormData(),y.navigate("/login"),!1;const d=document.getElementById("document-type-select"),c=document.getElementById("logo-input"),p=d==null?void 0:d.value,b=!!(c!=null&&c.files&&c.files.length>0);if((p==="formal"||p==="invoice")&&!b)return a.preventDefault(),a.stopPropagation(),a.stopImmediatePropagation(),this.showNoLogoModal(),!1},!0),t&&(t.addEventListener("input",()=>{m.isAuthenticated||this.saveFormData()}),t.addEventListener("change",()=>{m.isAuthenticated||this.saveFormData()})),document.addEventListener("click",a=>{const c=a.target.closest("[data-route]");if(c){a.preventDefault();const p=c.getAttribute("data-route");p&&y.navigate(p)}});const n=document.getElementById("modal-register-btn"),s=document.getElementById("modal-login-btn"),o=document.getElementById("modal-close-btn");n&&n.addEventListener("click",()=>{y.navigate("/register")}),s&&s.addEventListener("click",()=>{y.navigate("/login")}),o&&o.addEventListener("click",()=>{this.hideAuthModal()});const r=document.getElementById("modal-add-logo-btn"),l=document.getElementById("modal-continue-without-logo-btn");r&&r.addEventListener("click",()=>{this.hideNoLogoModal(),this.scrollToAndHighlightLogo()}),l&&l.addEventListener("click",()=>{this.hideNoLogoModal(),this.proceedWithGeneration()})}setupGenerationListener(){window.addEventListener("document-generated",e=>{console.log("Document generated:",e.detail.documentId),m.isAuthenticated||this.showAuthModal()})}showAuthModal(){const e=document.getElementById("auth-required-modal");e&&e.classList.remove("hidden")}hideAuthModal(){const e=document.getElementById("auth-required-modal");e&&e.classList.add("hidden")}showNoLogoModal(){const e=document.getElementById("no-logo-modal");e&&e.classList.remove("hidden")}hideNoLogoModal(){const e=document.getElementById("no-logo-modal");e&&e.classList.add("hidden")}scrollToAndHighlightLogo(){var t,n;const e=(n=(t=document.getElementById("logo-input"))==null?void 0:t.parentElement)==null?void 0:n.parentElement;if(e){e.scrollIntoView({behavior:"smooth",block:"center"});const s="animate-halo",o=document.createElement("style");o.textContent=`
        @keyframes halo-pulse {
          0%, 100% {
            box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
            border-color: #3b82f6;
          }
          50% {
            box-shadow: 0 0 0 15px rgba(59, 130, 246, 0);
            border-color: #60a5fa;
          }
        }
        .animate-halo {
          animation: halo-pulse 2s ease-in-out 3;
          border: 2px solid #3b82f6;
          border-radius: 0.5rem;
          padding: 1rem;
          transition: all 0.3s ease;
        }
      `,document.getElementById("halo-animation-style")||(o.id="halo-animation-style",document.head.appendChild(o)),e.classList.add(s),setTimeout(()=>{e.classList.remove(s)},6e3)}}proceedWithGeneration(){const e=document.getElementById("document-form");if(e){const t=new Event("submit",{bubbles:!0,cancelable:!0});e.dispatchEvent(t)}}saveFormData(){var n,s,o,r;if(!document.getElementById("document-form"))return;const t={description:((n=document.getElementById("description"))==null?void 0:n.value)||"",length:((s=document.getElementById("length"))==null?void 0:s.value)||"2000",documentType:((o=document.getElementById("document-type-select"))==null?void 0:o.value)||"infographic",useWatermark:((r=document.getElementById("use-watermark"))==null?void 0:r.checked)||!1};sessionStorage.setItem("generate_form_data",JSON.stringify(t)),console.log("Form data saved to sessionStorage")}restoreFormData(){const e=sessionStorage.getItem("generate_form_data");if(e)try{const t=JSON.parse(e);console.log("Restoring form data:",t);const n=document.getElementById("description");n&&t.description&&(n.value=t.description);const s=document.getElementById("length");if(s&&t.length&&(s.value=t.length),t.documentType){const r=document.getElementById("document-type-select");r&&(r.value=t.documentType)}const o=document.getElementById("use-watermark");o&&t.useWatermark!==void 0&&(o.checked=t.useWatermark),m.isAuthenticated&&(sessionStorage.removeItem("generate_form_data"),console.log("Form data restored and cleared from sessionStorage"))}catch(t){console.error("Failed to restore form data:",t),sessionStorage.removeItem("generate_form_data")}}setupCreditsCheck(){if(!m.isAuthenticated)return;const e={formal:34,infographic:52,invoice:28},t=()=>{var c;const s=document.getElementById("document-type-select"),o=(s==null?void 0:s.value)||"infographic",r=e[o],l=((c=m.user)==null?void 0:c.credits)??0,a=document.getElementById("submit-btn"),d=document.getElementById("insufficient-credits-warning");l<r?(a&&(a.disabled=!0,a.classList.add("opacity-50","cursor-not-allowed"),a.title="Insufficient credits"),d==null||d.classList.remove("hidden")):(a&&(a.disabled=!1,a.classList.remove("opacity-50","cursor-not-allowed"),a.title=""),d==null||d.classList.add("hidden"))};t();const n=document.getElementById("document-type-select");n&&n.addEventListener("change",t),m.subscribe((s,o)=>{s&&o&&t()})}setupDescriptionGuide(){const e={formal:`
        <strong>Be specific and structured:</strong> Describe the purpose, key topics, and target audience.
        Include section names you want (e.g., "Executive Summary, Market Analysis, Financial Overview").
        Mention the tone (professional, authoritative, persuasive).
        <br><br>
        <strong>Example:</strong> "Create a comprehensive business proposal for a SaaS product launch.
        Include sections on market opportunity, product features, competitive analysis, pricing strategy,
        and implementation timeline. Use a professional, persuasive tone targeting C-level executives."
      `,infographic:`
        <strong>Focus on visual themes and data:</strong> Describe the main topic and visual style you want.
        Mention specific concepts that should be illustrated with images.
        Be clear about what data points should be visualized as charts.
        <br><br>
        <strong>Example:</strong> "Create a marketing infographic about sustainable energy solutions.
        Show images of solar panels and wind turbines. Include charts comparing renewable vs traditional energy costs,
        and visualize our 40% carbon reduction achievement. Use clean, modern visuals with eco-friendly themes."
      `,invoice:`
        <strong>Provide transaction details:</strong> Include your business name and address (if available),
        comma-separated items with their prices and quantities, customer name, and preferred invoice date
        (if different from today's date).
        <br><br>
        <strong>Example:</strong> "Fashion Boutique Ltd, 456 Style Avenue, Los Angeles, CA.
        Items: Blue Denim Jeans ($45 x 2), White Cotton T-Shirt ($25 x 3), Black Leather Jacket ($120 x 1),
        Red Summer Dress ($60 x 2). Customer: Sarah Johnson. Date: November 23, 2025."
      `},t=()=>{const s=document.getElementById("document-type-select"),o=document.getElementById("description-guide-text");if(!s||!o)return;const r=s.value;o.innerHTML=e[r]||e.infographic};t();const n=document.getElementById("document-type-select");n&&n.addEventListener("change",t)}setupWatermarkToggle(){let e=!1;const t=()=>{const o=document.getElementById("watermark-container"),r=document.getElementById("document-type-select"),l=document.getElementById("use-watermark");if(!o||!r)return;const a=r.value;(a==="formal"||a==="invoice")&&e?o.classList.remove("hidden"):(o.classList.add("hidden"),l&&(l.checked=!1))},n=document.getElementById("logo-input");n&&n.addEventListener("change",o=>{const r=o.target;e=!!(r.files&&r.files.length>0),t()});const s=document.getElementById("document-type-select");s&&s.addEventListener("change",t),t()}setupLengthVisibility(){const e=()=>{const n=document.getElementById("length-container"),s=document.getElementById("length"),o=document.getElementById("document-type-select");if(!n||!o)return;o.value==="invoice"?(n.classList.add("hidden"),s&&s.removeAttribute("required")):(n.classList.remove("hidden"),s&&s.setAttribute("required","required"))},t=document.getElementById("document-type-select");t&&t.addEventListener("change",e),e()}destroy(){window.removeEventListener("document-generated",this.setupGenerationListener)}}export{N as GeneratePage};
