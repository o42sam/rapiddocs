var B=Object.defineProperty;var D=(o,e,t)=>e in o?B(o,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):o[e]=t;var c=(o,e,t)=>D(o,typeof e!="symbol"?e+"":e,t);import{a as g,c as _,b as l,r as f}from"./index-CLOizYH_.js";const b={async generateDocument(o){const e=new FormData;return e.append("description",o.description),e.append("length",o.length.toString()),e.append("document_type",o.document_type),e.append("use_watermark",o.use_watermark.toString()),e.append("statistics",JSON.stringify(o.statistics)),e.append("design_spec",JSON.stringify(o.design_spec)),o.logo&&e.append("logo",o.logo),(await g.post("/generate/document",e,{headers:{"Content-Type":"multipart/form-data"}})).data},async getJobStatus(o){return(await g.get(`/generate/status/${o}`)).data},async downloadDocument(o){return(await g.get(`/generate/download/${o}`,{responseType:"blob"})).data},async listDocuments(){return(await g.get("/documents")).data},async getDocument(o){return(await g.get(`/documents/${o}`)).data},async deleteDocument(o){await g.delete(`/documents/${o}`)}},T=o=>!o||o.trim().length<10?"Description must be at least 10 characters":o.length>2e3?"Description must be less than 2000 characters":null,$=o=>o<500?"Document length must be at least 500 words":o>1e4?"Document length must not exceed 10,000 words":null,M=(o,e,t)=>!o||o.trim().length===0?"Statistic name is required":o.length>100?"Statistic name must be less than 100 characters":isNaN(e)?"Statistic value must be a number":t&&t.length>20?"Unit must be less than 20 characters":null,L=o=>{const e=parseInt("5242880"),t="image/png,image/jpeg,image/svg+xml".split(",");return o.size>e?`File size must be less than ${(e/1024/1024).toFixed(1)}MB`:t.includes(o.type)?null:"Invalid file format. Allowed: PNG, JPG, SVG"},y=[{name:"Ocean Blue",background:"#FFFFFF",foreground1:"#2563EB",foreground2:"#06B6D4"},{name:"Corporate Red",background:"#FFFFFF",foreground1:"#DC2626",foreground2:"#F97316"},{name:"Forest Green",background:"#FFFFFF",foreground1:"#059669",foreground2:"#14B8A6"},{name:"Royal Purple",background:"#FFFFFF",foreground1:"#7C3AED",foreground2:"#EC4899"},{name:"Sunset Orange",background:"#FFFFFF",foreground1:"#EA580C",foreground2:"#EAB308"}];class z{constructor(e){c(this,"container");c(this,"selectedTheme");c(this,"onChangeCallback");const t=document.getElementById(e);if(!t)throw new Error(`Element with id ${e} not found`);this.container=t,this.selectedTheme=y[0],this.render()}onChange(e){this.onChangeCallback=e}getSelectedTheme(){return{background_color:this.selectedTheme.background,foreground_color_1:this.selectedTheme.foreground1,foreground_color_2:this.selectedTheme.foreground2,theme_name:this.selectedTheme.name}}render(){this.container.innerHTML=`
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Color Theme
      </label>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        ${y.map((e,t)=>`
          <button
            type="button"
            data-theme-index="${t}"
            class="theme-option p-4 border-2 rounded-lg transition-all hover:shadow-lg ${t===0?"border-blue-500 bg-blue-50":"border-gray-200"}"
          >
            <div class="flex gap-2 mb-2">
              <div class="w-8 h-8 rounded" style="background-color: ${e.foreground1}"></div>
              <div class="w-8 h-8 rounded" style="background-color: ${e.foreground2}"></div>
            </div>
            <div class="text-xs font-medium text-gray-700">${e.name}</div>
          </button>
        `).join("")}
      </div>
    `,this.attachEventListeners()}attachEventListeners(){this.container.querySelectorAll(".theme-option").forEach(t=>{t.addEventListener("click",s=>{const n=s.currentTarget,r=parseInt(n.dataset.themeIndex||"0");this.selectTheme(r)})})}selectTheme(e){this.selectedTheme=y[e],this.container.querySelectorAll(".theme-option").forEach((s,n)=>{n===e?(s.classList.add("border-blue-500","bg-blue-50"),s.classList.remove("border-gray-200")):(s.classList.remove("border-blue-500","bg-blue-50"),s.classList.add("border-gray-200"))}),this.onChangeCallback&&this.onChangeCallback(this.getSelectedTheme())}}class A{constructor(e){c(this,"container");c(this,"statistics",[]);c(this,"nextId",1);const t=document.getElementById(e);if(!t)throw new Error(`Element with id ${e} not found`);this.container=t,this.render()}getStatistics(){return this.statistics}render(){this.container.innerHTML=`
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <label class="block text-sm font-medium text-gray-700">
            Company Statistics (Optional, max 10)
          </label>
          <button
            type="button"
            id="add-statistic-btn"
            class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition disabled:bg-gray-400"
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
    `}attachEventListeners(){const e=document.getElementById("add-statistic-btn");e&&e.addEventListener("click",()=>this.addStatistic());const t=document.getElementById("statistics-list");t&&(t.addEventListener("click",s=>{const n=s.target;if(n.closest(".remove-stat-btn")){const r=n.closest(".statistic-item");r&&this.removeStatistic(r.dataset.id||"")}}),t.addEventListener("input",s=>{s.target.closest(".statistic-item")&&this.updateStatistics()}))}addStatistic(){if(this.statistics.length>=10)return;const e={id:`stat-${this.nextId++}`,name:"",value:0,unit:"",visualization_type:"bar"};this.statistics.push(e),this.render()}removeStatistic(e){this.statistics=this.statistics.filter(t=>t.id!==e),this.render()}updateStatistics(){this.container.querySelectorAll(".statistic-item").forEach(t=>{const s=t.dataset.id,n=this.statistics.find(r=>r.id===s);if(n){const r=t.querySelector(".stat-name"),a=t.querySelector(".stat-value"),u=t.querySelector(".stat-unit"),d=t.querySelector(".stat-viz-type");n.name=r.value,n.value=parseFloat(a.value)||0,n.unit=u.value||void 0,n.visualization_type=d.value}})}validate(){const e=[];return this.updateStatistics(),this.statistics.forEach((t,s)=>{const n=M(t.name,t.value,t.unit);n&&e.push(`Statistic ${s+1}: ${n}`)}),e}}class P{constructor(e){c(this,"form");c(this,"colorPalette");c(this,"statisticsForm");c(this,"currentJobId",null);c(this,"statusCheckInterval",null);const t=document.getElementById(e);if(!t||!(t instanceof HTMLFormElement))throw new Error(`Form with id ${e} not found`);this.form=t,this.colorPalette=new z("color-palette-container"),this.statisticsForm=new A("statistics-form-container"),this.attachEventListeners()}attachEventListeners(){this.form.addEventListener("submit",s=>{s.preventDefault(),this.handleSubmit()});const e=document.getElementById("logo-input");e&&e.addEventListener("change",s=>{var a;const r=(a=s.target.files)==null?void 0:a[0];this.updateFilePreview(r),this.updateWatermarkVisibility()}),document.querySelectorAll('input[name="document_type"]').forEach(s=>{s.addEventListener("change",()=>{this.updateWatermarkVisibility()})})}updateWatermarkVisibility(){const e=document.getElementById("watermark-container");if(!e)return;const t=document.querySelector('input[name="document_type"]:checked'),s=(t==null?void 0:t.value)||"infographic",n=document.getElementById("logo-input"),r=n.files&&n.files.length>0;if(s==="formal"&&r)e.classList.remove("hidden");else{e.classList.add("hidden");const a=document.getElementById("use-watermark");a&&(a.checked=!1)}}updateFilePreview(e){const t=document.getElementById("file-preview");if(t)if(e){const s=L(e);s?t.innerHTML=`<p class="text-sm text-red-600">${s}</p>`:t.innerHTML=`
          <p class="text-sm text-green-600">
            ✓ ${e.name} (${(e.size/1024).toFixed(1)} KB)
          </p>
        `}else t.innerHTML=""}async handleSubmit(){var w,k,E,C,I;this.clearErrors();const e=document.getElementById("description").value,t=parseInt(document.getElementById("length").value),n=(w=document.getElementById("logo-input").files)==null?void 0:w[0],r=document.querySelector('input[name="document_type"]:checked'),a=(r==null?void 0:r.value)||"infographic",u=document.getElementById("use-watermark"),d=(u==null?void 0:u.checked)||!1,i=[],p=T(e);p&&i.push(p);const x=$(t);if(x&&i.push(x),n){const m=L(n);m&&i.push(m)}const S=this.statisticsForm.validate();if(i.push(...S),i.length>0){this.showErrors(i);return}const F={description:e,length:t,document_type:a,use_watermark:d,statistics:this.statisticsForm.getStatistics(),design_spec:this.colorPalette.getSelectedTheme(),logo:n};try{this.showLoading(!0);try{const h=await _.deductCredits(a),v=l.user;v&&l.setAuthenticated({...v,credits:h.new_balance}),console.log(`Credits deducted: ${h.credits_deducted}, New balance: ${h.new_balance}`)}catch(h){const v=((E=(k=h.response)==null?void 0:k.data)==null?void 0:E.detail)||"Failed to deduct credits";this.showErrors([v]),this.showLoading(!1);return}const m=await b.generateDocument(F);this.currentJobId=m.job_id,this.startStatusPolling()}catch(m){this.showErrors([((I=(C=m.response)==null?void 0:C.data)==null?void 0:I.detail)||"Failed to start document generation"]),this.showLoading(!1)}}startStatusPolling(){this.currentJobId&&(this.updateProgress(0,"Initializing..."),this.statusCheckInterval=window.setInterval(async()=>{if(this.currentJobId)try{const e=await b.getJobStatus(this.currentJobId);this.handleStatusUpdate(e)}catch(e){console.error("Failed to check status:",e)}},3e3))}handleStatusUpdate(e){this.updateProgress(e.progress,e.current_step),e.status==="completed"?(this.stopStatusPolling(),this.showSuccess(e.job_id)):e.status==="failed"&&(this.stopStatusPolling(),this.showErrors([e.error_message||"Document generation failed"]),this.showLoading(!1))}stopStatusPolling(){this.statusCheckInterval&&(clearInterval(this.statusCheckInterval),this.statusCheckInterval=null)}updateProgress(e,t){const s=document.getElementById("progress-bar"),n=document.getElementById("progress-text");s&&(s.style.width=`${e}%`),n&&(n.textContent=`${e}% - ${this.formatStep(t)}`)}formatStep(e){return{initializing:"Initializing...",generating_text:"Generating document text...",generating_images:"Creating AI images...",generating_visualizations:"Creating data visualizations...",assembling_pdf:"Assembling PDF document...",completed:"Completed!"}[e]||e}showSuccess(e){const t=document.getElementById("result-container");if(!t)return;t.innerHTML=`
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
    `;const s=document.getElementById("download-btn");s&&s.addEventListener("click",()=>this.downloadPDF(e)),this.showLoading(!1)}async downloadPDF(e){var t,s;try{const n=await b.downloadDocument(e),r=window.URL.createObjectURL(n),a=document.createElement("a");a.href=r,a.download=`document-${Date.now()}.pdf`,document.body.appendChild(a),a.click(),window.URL.revokeObjectURL(r),document.body.removeChild(a)}catch(n){this.showErrors([((s=(t=n.response)==null?void 0:t.data)==null?void 0:s.detail)||"Failed to download PDF"])}}showLoading(e){const t=document.getElementById("loading-container"),s=document.getElementById("submit-btn");t&&t.classList.toggle("hidden",!e),s&&(s.disabled=e,s.textContent=e?"Generating...":"Generate Document")}showErrors(e){const t=document.getElementById("error-container");t&&(t.innerHTML=`
      <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-red-800 mb-2">Please fix the following errors:</h4>
        <ul class="list-disc list-inside space-y-1">
          ${e.map(s=>`<li class="text-sm text-red-600">${s}</li>`).join("")}
        </ul>
      </div>
    `,t.classList.remove("hidden"))}clearErrors(){const e=document.getElementById("error-container");e&&(e.classList.add("hidden"),e.innerHTML="");const t=document.getElementById("result-container");t&&(t.innerHTML="")}}class V{render(){const e=document.getElementById("app");if(!e)return;const t=document.getElementById("nav-container");t&&(t.style.display=""),e.innerHTML=`
      <div class="min-h-screen bg-gray-50 pb-12 pt-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <!-- Page Header -->
          <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">Generate Your Document</h1>
            <p class="text-xl text-gray-600">Create professional documents with AI in seconds</p>
          </div>

          <!-- Auth Warning (shown if not authenticated) -->
          ${l.isAuthenticated?"":`
            <div class="mb-8 bg-blue-50 border-l-4 border-blue-400 p-4 rounded-lg">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm text-blue-700">
                    <strong>Please log in to generate documents.</strong> You'll be redirected to the login page when you click "Generate Document". Don't have an account? <a href="/register" data-route="/register" class="font-semibold underline hover:text-blue-800">Sign up here</a>.
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
                  rows="4"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  placeholder="Describe the document you want to generate. For example: 'Create a quarterly business report highlighting our company's growth in the tech sector, focusing on innovation and market expansion.'"
                  required
                ></textarea>
                <p class="mt-1 text-xs text-gray-500">Minimum 10 characters, maximum 2000 characters</p>
              </div>

              <!-- Document Length -->
              <div>
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
                  class="w-full md:w-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  required
                />
                <p class="mt-1 text-xs text-gray-500">Between 500 and 10,000 words</p>
              </div>

              <!-- Document Type -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-3">
                  Document Type
                  <span class="text-red-500">*</span>
                </label>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <!-- Formal Option -->
                  <label for="type-formal" class="relative flex cursor-pointer rounded-lg border border-gray-300 bg-white p-4 hover:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500 transition">
                    <input type="radio" id="type-formal" name="document_type" value="formal" class="sr-only peer" />
                    <span class="flex flex-1">
                      <span class="flex flex-col">
                        <span class="flex items-center gap-2 text-sm font-semibold text-gray-900">
                          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          Formal Document
                        </span>
                        <span class="mt-1 text-xs text-gray-500">Professional text-only document with decorative lines. No images or charts.</span>
                        <div class="mt-2 flex items-center justify-between gap-4">
                          <span class="text-xs font-medium text-gray-600">⚡ ~60 seconds</span>
                          ${l.isAuthenticated?`
                          <span class="flex items-center gap-1 text-xs font-semibold text-blue-600">
                            <svg class="w-3.5 h-3.5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd" />
                            </svg>
                            34 credits
                          </span>
                          `:""}
                        </div>
                      </span>
                    </span>
                    <svg class="h-5 w-5 text-blue-600 opacity-0 peer-checked:opacity-100 absolute top-4 right-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    <span class="pointer-events-none absolute -inset-px rounded-lg border-2 border-transparent peer-checked:border-blue-500"></span>
                  </label>

                  <!-- Infographic Option -->
                  <label for="type-infographic" class="relative flex cursor-pointer rounded-lg border border-gray-300 bg-white p-4 hover:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500 transition">
                    <input type="radio" id="type-infographic" name="document_type" value="infographic" class="sr-only peer" checked />
                    <span class="flex flex-1">
                      <span class="flex flex-col">
                        <span class="flex items-center gap-2 text-sm font-semibold text-gray-900">
                          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                          </svg>
                          Infographic Document
                        </span>
                        <span class="mt-1 text-xs text-gray-500">Rich visual document with AI images and data charts. Perfect for presentations.</span>
                        <div class="mt-2 flex items-center justify-between gap-4">
                          <span class="text-xs font-medium text-gray-600">⏱️ ~120 seconds</span>
                          ${l.isAuthenticated?`
                          <span class="flex items-center gap-1 text-xs font-semibold text-blue-600">
                            <svg class="w-3.5 h-3.5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd" />
                            </svg>
                            52 credits
                          </span>
                          `:""}
                        </div>
                      </span>
                    </span>
                    <svg class="h-5 w-5 text-blue-600 opacity-0 peer-checked:opacity-100 absolute top-4 right-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    <span class="pointer-events-none absolute -inset-px rounded-lg border-2 border-transparent peer-checked:border-blue-500"></span>
                  </label>
                </div>
                <p class="mt-2 text-xs text-gray-600">
                  <strong>Formal:</strong> Text + 3 decorative edge lines |
                  <strong>Infographic:</strong> Text + AI images + data charts
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
                <div class="flex items-center gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <input type="checkbox" id="use-watermark" name="use_watermark" class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500" />
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
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div class="flex items-center mb-4">
                  <svg class="animate-spin h-5 w-5 text-blue-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <h3 class="text-lg font-semibold text-blue-800">Generating Your Document</h3>
                </div>
                <div class="mb-3">
                  <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div id="progress-bar" class="bg-blue-600 h-3 rounded-full transition-all duration-300" style="width: 0%"></div>
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
                <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
                  <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                    class="px-4 py-2 bg-blue-600 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
        </div>
      </div>
    `;try{new P("document-form")}catch(s){console.error("Failed to initialize document form:",s)}this.attachEventListeners(),this.setupGenerationListener(),this.restoreFormData(),this.setupCreditsCheck()}attachEventListeners(){const e=document.getElementById("buy-credits-from-warning-btn");e&&e.addEventListener("click",()=>{window.dispatchEvent(new CustomEvent("open-credits-modal"))});const t=document.getElementById("document-form");t&&t.addEventListener("submit",a=>{if(!l.isAuthenticated)return a.preventDefault(),a.stopPropagation(),a.stopImmediatePropagation(),this.saveFormData(),f.navigate("/login"),!1},!0),t&&(t.addEventListener("input",()=>{l.isAuthenticated||this.saveFormData()}),t.addEventListener("change",()=>{l.isAuthenticated||this.saveFormData()})),document.addEventListener("click",a=>{const d=a.target.closest("[data-route]");if(d){a.preventDefault();const i=d.getAttribute("data-route");i&&f.navigate(i)}});const s=document.getElementById("modal-register-btn"),n=document.getElementById("modal-login-btn"),r=document.getElementById("modal-close-btn");s&&s.addEventListener("click",()=>{f.navigate("/register")}),n&&n.addEventListener("click",()=>{f.navigate("/login")}),r&&r.addEventListener("click",()=>{this.hideAuthModal()})}setupGenerationListener(){window.addEventListener("document-generated",e=>{console.log("Document generated:",e.detail.documentId),l.isAuthenticated||this.showAuthModal()})}showAuthModal(){const e=document.getElementById("auth-required-modal");e&&e.classList.remove("hidden")}hideAuthModal(){const e=document.getElementById("auth-required-modal");e&&e.classList.add("hidden")}saveFormData(){var s,n,r,a;if(!document.getElementById("document-form"))return;const t={description:((s=document.getElementById("description"))==null?void 0:s.value)||"",length:((n=document.getElementById("length"))==null?void 0:n.value)||"2000",documentType:((r=document.querySelector('input[name="document_type"]:checked'))==null?void 0:r.value)||"infographic",useWatermark:((a=document.getElementById("use-watermark"))==null?void 0:a.checked)||!1};sessionStorage.setItem("generate_form_data",JSON.stringify(t)),console.log("Form data saved to sessionStorage")}restoreFormData(){const e=sessionStorage.getItem("generate_form_data");if(e)try{const t=JSON.parse(e);console.log("Restoring form data:",t);const s=document.getElementById("description");s&&t.description&&(s.value=t.description);const n=document.getElementById("length");if(n&&t.length&&(n.value=t.length),t.documentType){const a=document.querySelector(`input[name="document_type"][value="${t.documentType}"]`);a&&(a.checked=!0)}const r=document.getElementById("use-watermark");r&&t.useWatermark!==void 0&&(r.checked=t.useWatermark),l.isAuthenticated&&(sessionStorage.removeItem("generate_form_data"),console.log("Form data restored and cleared from sessionStorage"))}catch(t){console.error("Failed to restore form data:",t),sessionStorage.removeItem("generate_form_data")}}setupCreditsCheck(){if(!l.isAuthenticated)return;const e={formal:34,infographic:52},t=()=>{var p;const n=document.querySelector('input[name="document_type"]:checked'),r=(n==null?void 0:n.value)||"infographic",a=e[r],u=((p=l.user)==null?void 0:p.credits)??0,d=document.getElementById("submit-btn"),i=document.getElementById("insufficient-credits-warning");u<a?(d&&(d.disabled=!0,d.classList.add("opacity-50","cursor-not-allowed"),d.title="Insufficient credits"),i==null||i.classList.remove("hidden")):(d&&(d.disabled=!1,d.classList.remove("opacity-50","cursor-not-allowed"),d.title=""),i==null||i.classList.add("hidden"))};t(),document.querySelectorAll('input[name="document_type"]').forEach(n=>{n.addEventListener("change",t)}),l.subscribe((n,r)=>{n&&r&&t()})}destroy(){window.removeEventListener("document-generated",this.setupGenerationListener)}}export{V as GeneratePage};
