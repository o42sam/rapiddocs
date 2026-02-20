var D=Object.defineProperty;var F=(i,e,t)=>e in i?D(i,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):i[e]=t;var m=(i,e,t)=>F(i,typeof e!="symbol"?e+"":e,t);import{a as h,c as T,b as g,r as x}from"./index-Dwqr2h1J.js";const w={async generateDocument(i){const e=new FormData;return e.append("description",i.description),e.append("length",i.length.toString()),e.append("document_type",i.document_type),e.append("use_watermark",i.use_watermark.toString()),e.append("statistics",JSON.stringify(i.statistics)),e.append("design_spec",JSON.stringify(i.design_spec)),i.logo&&e.append("logo",i.logo),i.skip_validation!==void 0&&e.append("skip_validation",i.skip_validation.toString()),(await h.post("/generate/document",e,{headers:{"Content-Type":"multipart/form-data"}})).data},async getJobStatus(i){return(await h.get(`/generate/status/${i}`)).data},async downloadDocument(i){return(await h.get(`/generate/download/${i}`,{responseType:"blob"})).data},async listDocuments(){return(await h.get("/documents")).data},async getDocument(i){return(await h.get(`/documents/${i}`)).data},async deleteDocument(i){await h.delete(`/documents/${i}`)}},_=i=>!i||i.trim().length<10?"Description must be at least 10 characters":i.length>2e3?"Description must be less than 2000 characters":null,A=i=>i<500?"Document length must be at least 500 words":i>1e4?"Document length must not exceed 10,000 words":null,M=(i,e,t)=>!i||i.trim().length===0?"Statistic name is required":i.length>100?"Statistic name must be less than 100 characters":isNaN(e)?"Statistic value must be a number":t&&t.length>20?"Unit must be less than 20 characters":null,S=i=>{const e=parseInt("5242880"),t="image/png,image/jpeg,image/svg+xml".split(",");return i.size>e?`File size must be less than ${(e/1024/1024).toFixed(1)}MB`:t.includes(i.type)?null:"Invalid file format. Allowed: PNG, JPG, SVG"},E=[{name:"Ocean Blue",background:"#FFFFFF",foreground1:"#2563EB",foreground2:"#06B6D4"},{name:"Corporate Red",background:"#FFFFFF",foreground1:"#DC2626",foreground2:"#F97316"},{name:"Forest Green",background:"#FFFFFF",foreground1:"#059669",foreground2:"#14B8A6"},{name:"Royal Purple",background:"#FFFFFF",foreground1:"#7C3AED",foreground2:"#EC4899"},{name:"Sunset Orange",background:"#FFFFFF",foreground1:"#EA580C",foreground2:"#EAB308"}];class ${constructor(e){m(this,"container");m(this,"selectedTheme");m(this,"onChangeCallback");const t=document.getElementById(e);if(!t)throw new Error(`Element with id ${e} not found`);this.container=t,this.selectedTheme=E[0],this.render()}onChange(e){this.onChangeCallback=e}getSelectedTheme(){return{background_color:this.selectedTheme.background,foreground_color_1:this.selectedTheme.foreground1,foreground_color_2:this.selectedTheme.foreground2,theme_name:this.selectedTheme.name}}render(){this.container.innerHTML=`
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
    `,this.attachEventListeners()}attachEventListeners(){this.container.querySelectorAll(".theme-option").forEach(t=>{t.addEventListener("click",o=>{const s=o.currentTarget,n=parseInt(s.dataset.themeIndex||"0");this.selectTheme(n)})})}selectTheme(e){this.selectedTheme=E[e],this.container.querySelectorAll(".theme-option").forEach((o,s)=>{s===e?(o.classList.add("border-primary-500","bg-primary-50"),o.classList.remove("border-gray-200")):(o.classList.remove("border-primary-500","bg-primary-50"),o.classList.add("border-gray-200"))}),this.onChangeCallback&&this.onChangeCallback(this.getSelectedTheme())}}class P{constructor(e){m(this,"container");m(this,"statistics",[]);m(this,"nextId",1);const t=document.getElementById(e);if(!t)throw new Error(`Element with id ${e} not found`);this.container=t,this.render()}getStatistics(){return this.statistics}render(){this.container.innerHTML=`
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
    `}attachEventListeners(){const e=document.getElementById("add-statistic-btn");e&&e.addEventListener("click",()=>this.addStatistic());const t=document.getElementById("statistics-list");t&&(t.addEventListener("click",o=>{const s=o.target;if(s.closest(".remove-stat-btn")){const n=s.closest(".statistic-item");n&&this.removeStatistic(n.dataset.id||"")}}),t.addEventListener("input",o=>{o.target.closest(".statistic-item")&&this.updateStatistics()}))}addStatistic(){if(this.statistics.length>=10)return;const e={id:`stat-${this.nextId++}`,name:"",value:0,unit:"",visualization_type:"bar"};this.statistics.push(e),this.render()}removeStatistic(e){this.statistics=this.statistics.filter(t=>t.id!==e),this.render()}updateStatistics(){this.container.querySelectorAll(".statistic-item").forEach(t=>{const o=t.dataset.id,s=this.statistics.find(n=>n.id===o);if(s){const n=t.querySelector(".stat-name"),r=t.querySelector(".stat-value"),l=t.querySelector(".stat-unit"),a=t.querySelector(".stat-viz-type");s.name=n.value,s.value=parseFloat(r.value)||0,s.unit=l.value||void 0,s.visualization_type=a.value}})}validate(){const e=[];return this.updateStatistics(),this.statistics.forEach((t,o)=>{const s=M(t.name,t.value,t.unit);s&&e.push(`Statistic ${o+1}: ${s}`)}),e}}class z{constructor(e){m(this,"form");m(this,"colorPalette");m(this,"statisticsForm");m(this,"currentJobId",null);m(this,"statusCheckInterval",null);const t=document.getElementById(e);if(!t||!(t instanceof HTMLFormElement))throw new Error(`Form with id ${e} not found`);this.form=t,this.colorPalette=new $("color-palette-container"),this.statisticsForm=new P("statistics-form-container"),this.attachEventListeners()}attachEventListeners(){this.form.addEventListener("submit",o=>{o.preventDefault(),this.handleSubmit()});const e=document.getElementById("logo-input");e&&e.addEventListener("change",o=>{var r;const n=(r=o.target.files)==null?void 0:r[0];this.updateFilePreview(n),this.updateWatermarkVisibility()});const t=document.getElementById("document-type-select");t&&t.addEventListener("change",()=>{this.updateWatermarkVisibility()})}updateWatermarkVisibility(){const e=document.getElementById("watermark-container");if(!e)return;const t=document.getElementById("document-type-select"),o=(t==null?void 0:t.value)||"infographic",s=document.getElementById("logo-input"),n=s.files&&s.files.length>0;if((o==="formal"||o==="invoice")&&n)e.classList.remove("hidden");else{e.classList.add("hidden");const r=document.getElementById("use-watermark");r&&(r.checked=!1)}}updateFilePreview(e){const t=document.getElementById("file-preview");if(t)if(e){const o=S(e);o?t.innerHTML=`<p class="text-sm text-red-600">${o}</p>`:t.innerHTML=`
          <p class="text-sm text-green-600">
            ✓ ${e.name} (${(e.size/1024).toFixed(1)} KB)
          </p>
        `}else t.innerHTML=""}async handleSubmit(){var k,I,L,B,C;this.clearErrors();const e=document.getElementById("description").value,t=parseInt(document.getElementById("length").value),s=(k=document.getElementById("logo-input").files)==null?void 0:k[0],n=document.getElementById("document-type-select"),r=(n==null?void 0:n.value)||"infographic",l=document.getElementById("use-watermark"),a=(l==null?void 0:l.checked)||!1,d=[],u=_(e);if(u&&d.push(u),r!=="invoice"){const c=A(t);c&&d.push(c)}if(s){const c=S(s);c&&d.push(c)}const p=this.statisticsForm.validate();if(d.push(...p),d.length>0){this.showErrors(d);return}let y=!1;if(r==="invoice"){const c=await this.validateInvoicePrompt(e);if(!c.proceed)return;y=c.skipValidation||!1}const b={description:e,length:t,document_type:r,use_watermark:a,statistics:this.statisticsForm.getStatistics(),design_spec:this.colorPalette.getSelectedTheme(),logo:s,skip_validation:y};try{this.showLoading(!0);try{const f=await T.deductCredits(r),v=g.user;v&&g.setAuthenticated({...v,credits:f.new_balance}),console.log(`Credits deducted: ${f.credits_deducted}, New balance: ${f.new_balance}`)}catch(f){const v=((L=(I=f.response)==null?void 0:I.data)==null?void 0:L.detail)||"Failed to deduct credits";this.showErrors([v]),this.showLoading(!1);return}const c=await w.generateDocument(b);if(c.status==="validation_failed"){if(!(await this.showIncompleteDataDialog(c.missing_fields||[])).proceed){this.showLoading(!1);return}b.skip_validation=!0;const v=await w.generateDocument(b);this.currentJobId=v.job_id,this.startStatusPolling()}else this.currentJobId=c.job_id,this.startStatusPolling()}catch(c){this.showErrors([((C=(B=c.response)==null?void 0:B.data)==null?void 0:C.detail)||"Failed to start document generation"]),this.showLoading(!1)}}startStatusPolling(){this.currentJobId&&(this.updateProgress(0,"Initializing..."),this.statusCheckInterval=window.setInterval(async()=>{if(this.currentJobId)try{const e=await w.getJobStatus(this.currentJobId);this.handleStatusUpdate(e)}catch(e){console.error("Failed to check status:",e)}},3e3))}handleStatusUpdate(e){this.updateProgress(e.progress,e.current_step),e.status==="completed"?(this.stopStatusPolling(),this.showSuccess(e.job_id)):e.status==="failed"&&(this.stopStatusPolling(),this.showErrors([e.error_message||"Document generation failed"]),this.showLoading(!1))}stopStatusPolling(){this.statusCheckInterval&&(clearInterval(this.statusCheckInterval),this.statusCheckInterval=null)}updateProgress(e,t){const o=document.getElementById("progress-bar"),s=document.getElementById("progress-text");o&&(o.style.width=`${e}%`),s&&(s.textContent=`${e}% - ${this.formatStep(t)}`)}formatStep(e){return{initializing:"Initializing...",generating_text:"Generating document text...",generating_images:"Creating AI images...",generating_visualizations:"Creating data visualizations...",assembling_pdf:"Assembling PDF document...",completed:"Completed!"}[e]||e}showSuccess(e){const t=document.getElementById("result-container");if(!t)return;t.innerHTML=`
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
    `;const o=document.getElementById("download-btn");o&&o.addEventListener("click",()=>this.downloadPDF(e)),this.showLoading(!1)}async downloadPDF(e){var t,o;try{const s=await w.downloadDocument(e),n=window.URL.createObjectURL(s),r=document.createElement("a");r.href=n,r.download=`document-${Date.now()}.pdf`,document.body.appendChild(r),r.click(),window.URL.revokeObjectURL(n),document.body.removeChild(r)}catch(s){this.showErrors([((o=(t=s.response)==null?void 0:t.data)==null?void 0:o.detail)||"Failed to download PDF"])}}showLoading(e){const t=document.getElementById("loading-container"),o=document.getElementById("submit-btn");t&&t.classList.toggle("hidden",!e),o&&(o.disabled=e,o.textContent=e?"Generating...":"Generate Document")}showErrors(e){const t=document.getElementById("error-container");t&&(t.innerHTML=`
      <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-red-800 mb-2">Please fix the following errors:</h4>
        <ul class="list-disc list-inside space-y-1">
          ${e.map(o=>`<li class="text-sm text-red-600">${o}</li>`).join("")}
        </ul>
      </div>
    `,t.classList.remove("hidden"))}clearErrors(){const e=document.getElementById("error-container");e&&(e.classList.add("hidden"),e.innerHTML="");const t=document.getElementById("result-container");t&&(t.innerHTML="")}async validateInvoicePrompt(e){try{const t=new FormData;t.append("description",e);const s=(await h.post("/validate/invoice",t,{headers:{"Content-Type":"multipart/form-data"}})).data;return s.is_complete?{proceed:!0}:await this.showIncompleteDataDialog(s.missing_fields)}catch(t){return console.error("Validation failed:",t),{proceed:!0}}}showIncompleteDataDialog(e){return new Promise(t=>{const o=document.getElementById("description");o&&o.classList.add("halo-effect");const s=document.createElement("div");s.className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center",s.innerHTML=`
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div class="flex items-start mb-4">
            <svg class="w-6 h-6 text-yellow-500 mr-2 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Incomplete Invoice Information</h3>
              <p class="text-sm text-gray-600 mb-3">The following information is missing or using placeholders:</p>
              <ul class="list-disc list-inside text-sm text-gray-700 space-y-1 mb-4">
                ${e.map(l=>`<li>${l}</li>`).join("")}
              </ul>
              <p class="text-sm text-gray-600">Would you like to continue anyway or update your description?</p>
            </div>
          </div>
          <div class="flex justify-end space-x-3">
            <button id="dialog-cancel" class="px-4 py-2 text-gray-600 hover:text-gray-800 transition">
              Update Description
            </button>
            <button id="dialog-proceed" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
              Continue Anyway
            </button>
          </div>
        </div>
      `,document.body.appendChild(s);const n=document.getElementById("dialog-cancel"),r=document.getElementById("dialog-proceed");n&&n.addEventListener("click",()=>{document.body.removeChild(s),o&&(o.focus(),setTimeout(()=>{o.classList.remove("halo-effect")},3e3)),t({proceed:!1})}),r&&r.addEventListener("click",()=>{document.body.removeChild(s),o&&o.classList.remove("halo-effect"),t({proceed:!0,skipValidation:!0})})})}}class j{render(){const e=document.getElementById("app");if(!e)return;const t=document.getElementById("nav-container");t&&(t.style.display=""),e.innerHTML=`
      <div class="min-h-screen bg-gray-50 pb-12 pt-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <!-- Page Header -->
          <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">Generate Your Document</h1>
            <p class="text-xl text-gray-600">Create professional documents with AI in seconds</p>
          </div>

          <!-- Auth Warning (shown if not authenticated) -->
          ${g.isAuthenticated?"":`
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
    `;try{new z("document-form")}catch(o){console.error("Failed to initialize document form:",o)}this.attachEventListeners(),this.setupGenerationListener(),this.restoreFormData(),this.setupCreditsCheck(),this.setupDescriptionGuide(),this.setupWatermarkToggle(),this.setupLengthVisibility()}attachEventListeners(){const e=document.getElementById("buy-credits-from-warning-btn");e&&e.addEventListener("click",()=>{window.dispatchEvent(new CustomEvent("open-credits-modal"))});const t=document.getElementById("document-form");t&&t.addEventListener("submit",a=>{if(!g.isAuthenticated)return a.preventDefault(),a.stopPropagation(),a.stopImmediatePropagation(),this.saveFormData(),x.navigate("/login"),!1;const d=document.getElementById("document-type-select"),u=document.getElementById("logo-input"),p=d==null?void 0:d.value,y=!!(u!=null&&u.files&&u.files.length>0);if((p==="formal"||p==="invoice")&&!y)return a.preventDefault(),a.stopPropagation(),a.stopImmediatePropagation(),this.showNoLogoModal(),!1},!0),t&&(t.addEventListener("input",()=>{g.isAuthenticated||this.saveFormData()}),t.addEventListener("change",()=>{g.isAuthenticated||this.saveFormData()})),document.addEventListener("click",a=>{const u=a.target.closest("[data-route]");if(u){a.preventDefault();const p=u.getAttribute("data-route");p&&x.navigate(p)}});const o=document.getElementById("modal-register-btn"),s=document.getElementById("modal-login-btn"),n=document.getElementById("modal-close-btn");o&&o.addEventListener("click",()=>{x.navigate("/register")}),s&&s.addEventListener("click",()=>{x.navigate("/login")}),n&&n.addEventListener("click",()=>{this.hideAuthModal()});const r=document.getElementById("modal-add-logo-btn"),l=document.getElementById("modal-continue-without-logo-btn");r&&r.addEventListener("click",()=>{this.hideNoLogoModal(),this.scrollToAndHighlightLogo()}),l&&l.addEventListener("click",()=>{this.hideNoLogoModal(),this.proceedWithGeneration()})}setupGenerationListener(){window.addEventListener("document-generated",e=>{console.log("Document generated:",e.detail.documentId),g.isAuthenticated||this.showAuthModal()})}showAuthModal(){const e=document.getElementById("auth-required-modal");e&&e.classList.remove("hidden")}hideAuthModal(){const e=document.getElementById("auth-required-modal");e&&e.classList.add("hidden")}showNoLogoModal(){const e=document.getElementById("no-logo-modal");e&&e.classList.remove("hidden")}hideNoLogoModal(){const e=document.getElementById("no-logo-modal");e&&e.classList.add("hidden")}scrollToAndHighlightLogo(){var t,o;const e=(o=(t=document.getElementById("logo-input"))==null?void 0:t.parentElement)==null?void 0:o.parentElement;if(e){e.scrollIntoView({behavior:"smooth",block:"center"});const s="animate-halo",n=document.createElement("style");n.textContent=`
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
      `,document.getElementById("halo-animation-style")||(n.id="halo-animation-style",document.head.appendChild(n)),e.classList.add(s),setTimeout(()=>{e.classList.remove(s)},6e3)}}proceedWithGeneration(){const e=document.getElementById("document-form");if(e){const t=new Event("submit",{bubbles:!0,cancelable:!0});e.dispatchEvent(t)}}saveFormData(){var o,s,n,r;if(!document.getElementById("document-form"))return;const t={description:((o=document.getElementById("description"))==null?void 0:o.value)||"",length:((s=document.getElementById("length"))==null?void 0:s.value)||"2000",documentType:((n=document.getElementById("document-type-select"))==null?void 0:n.value)||"infographic",useWatermark:((r=document.getElementById("use-watermark"))==null?void 0:r.checked)||!1};sessionStorage.setItem("generate_form_data",JSON.stringify(t)),console.log("Form data saved to sessionStorage")}restoreFormData(){const e=sessionStorage.getItem("generate_form_data");if(e)try{const t=JSON.parse(e);console.log("Restoring form data:",t);const o=document.getElementById("description");o&&t.description&&(o.value=t.description);const s=document.getElementById("length");if(s&&t.length&&(s.value=t.length),t.documentType){const r=document.getElementById("document-type-select");r&&(r.value=t.documentType)}const n=document.getElementById("use-watermark");n&&t.useWatermark!==void 0&&(n.checked=t.useWatermark),g.isAuthenticated&&(sessionStorage.removeItem("generate_form_data"),console.log("Form data restored and cleared from sessionStorage"))}catch(t){console.error("Failed to restore form data:",t),sessionStorage.removeItem("generate_form_data")}}setupCreditsCheck(){if(!g.isAuthenticated)return;const e={formal:34,infographic:52,invoice:28},t=()=>{var u;const s=document.getElementById("document-type-select"),n=(s==null?void 0:s.value)||"infographic",r=e[n],l=((u=g.user)==null?void 0:u.credits)??0,a=document.getElementById("submit-btn"),d=document.getElementById("insufficient-credits-warning");l<r?(a&&(a.disabled=!0,a.classList.add("opacity-50","cursor-not-allowed"),a.title="Insufficient credits"),d==null||d.classList.remove("hidden")):(a&&(a.disabled=!1,a.classList.remove("opacity-50","cursor-not-allowed"),a.title=""),d==null||d.classList.add("hidden"))};t();const o=document.getElementById("document-type-select");o&&o.addEventListener("change",t),g.subscribe((s,n)=>{s&&n&&t()})}setupDescriptionGuide(){const e={formal:`
        <strong>Be specific and structured:</strong> Describe the purpose, key topics, and target audience.
        Include section names you want (e.g., "Executive Summary, Market Analysis, Financial Overview").
        Mention the tone (professional, authoritative, persuasive).
        <br><br>
        <strong>Example:</strong> "Create a comprehensive business proposal for a SaaS product launch.
        Include sections on market opportunity, product features, competitive analysis, pricing strategy,
        and implementation timeline. Use a professional, persuasive tone targeting C-level executives."
      `,infographic:`
        <strong>Describe your topic, data, and visuals:</strong> Our AI automatically extracts statistics,
        selects optimal chart types (bar, line, pie, gauge), generates relevant images, and structures your document.
        Include specific numbers/percentages for automatic visualization.
        <br><br>
        <strong>Example:</strong> "Create a quarterly business performance report for Q4 2024, approximately 800 words.
        Include statistics: revenue grew 35% to $2.4M, customer satisfaction at 92%, new users increased by 12,000 (up 28%),
        and market share reached 18%. Show a pie chart of revenue by region (North America 45%, Europe 30%, Asia 25%).
        Generate images of a modern office workspace, team collaboration, and data analytics dashboard.
        Use a professional tone with sections covering financial highlights, customer metrics, growth initiatives, and 2025 outlook.
        Color theme: corporate blue and green."
      `,invoice:`
        <strong>Provide complete transaction details:</strong> Include vendor (your business) name and full address,
        customer/client name and address, detailed list of items/services with prices and quantities,
        payment terms, and any special notes.
        <br><br>
        <strong>Example:</strong> "Vendor: Fashion Boutique Ltd, 456 Style Avenue, Los Angeles, CA 90015, USA.
        Customer: Sarah Johnson at Digital Innovations Inc, 789 Tech Plaza, San Francisco, CA 94105.
        Items: Blue Denim Jeans ($45 x 2), White Cotton T-Shirt ($25 x 3), Black Leather Jacket ($120 x 1),
        Red Summer Dress ($60 x 2). Payment terms: Net 30 days. Tax rate: 10%.
        Notes: Thank you for your continued business! Contact us at sales@fashionboutique.com for any questions."
      `},t=()=>{const s=document.getElementById("document-type-select"),n=document.getElementById("description-guide-text");if(!s||!n)return;const r=s.value;n.innerHTML=e[r]||e.infographic};t();const o=document.getElementById("document-type-select");o&&o.addEventListener("change",t)}setupWatermarkToggle(){let e=!1;const t=()=>{const n=document.getElementById("watermark-container"),r=document.getElementById("document-type-select"),l=document.getElementById("use-watermark");if(!n||!r)return;const a=r.value;(a==="formal"||a==="invoice")&&e?n.classList.remove("hidden"):(n.classList.add("hidden"),l&&(l.checked=!1))},o=document.getElementById("logo-input");o&&o.addEventListener("change",n=>{const r=n.target;e=!!(r.files&&r.files.length>0),t()});const s=document.getElementById("document-type-select");s&&s.addEventListener("change",t),t()}setupLengthVisibility(){const e=()=>{const o=document.getElementById("length-container"),s=document.getElementById("length"),n=document.getElementById("document-type-select");if(!o||!n)return;const r=n.value;r==="infographic"||r==="formal"?(o.classList.remove("hidden"),s&&s.setAttribute("required","required")):(o.classList.add("hidden"),s&&s.removeAttribute("required"))},t=document.getElementById("document-type-select");t&&t.addEventListener("change",e),e()}destroy(){window.removeEventListener("document-generated",this.setupGenerationListener)}}export{j as GeneratePage};
