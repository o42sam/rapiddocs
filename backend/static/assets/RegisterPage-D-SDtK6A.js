var v=Object.defineProperty;var b=(a,e,t)=>e in a?v(a,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):a[e]=t;var f=(a,e,t)=>b(a,typeof e!="symbol"?e+"":e,t);import{r as y,d as x,b as h}from"./index-CqQJt02h.js";import{G as w}from"./GoogleSignInButton-CFFzpfyd.js";class B{constructor(){f(this,"googleButton")}render(){const e=document.getElementById("app");e&&(e.innerHTML=`
      <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-purple-50 pt-32 pb-12 px-4 sm:px-6 lg:px-8">
        <div class="max-w-md w-full space-y-8">
          <!-- Header -->
          <div class="text-center">
            <h2 class="text-4xl font-bold text-gray-900 mb-2">Create Account</h2>
            <p class="text-gray-600">Join RapidDocs and start creating professional documents</p>
          </div>

          <!-- Register Form -->
          <div class="bg-white rounded-xl shadow-lg p-8">
            <form id="register-form" class="space-y-6">
              <!-- Username -->
              <div>
                <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  required
                  autocomplete="username"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition"
                  placeholder="Choose a username"
                />
              </div>

              <!-- Full Name -->
              <div>
                <label for="full_name" class="block text-sm font-medium text-gray-700 mb-2">
                  Full Name (Optional)
                </label>
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  autocomplete="name"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition"
                  placeholder="Your full name"
                />
              </div>

              <!-- Email -->
              <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  autocomplete="email"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition"
                  placeholder="you@example.com"
                />
              </div>

              <!-- Password -->
              <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  required
                  autocomplete="new-password"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition"
                  placeholder="Create a strong password"
                />
                <p class="mt-1 text-xs text-gray-500">At least 8 characters</p>
              </div>

              <!-- Confirm Password -->
              <div>
                <label for="confirm-password" class="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password
                </label>
                <input
                  type="password"
                  id="confirm-password"
                  name="confirm-password"
                  required
                  autocomplete="new-password"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition"
                  placeholder="Confirm your password"
                />
              </div>

              <!-- Terms & Conditions -->
              <div class="flex items-start">
                <input
                  id="terms"
                  name="terms"
                  type="checkbox"
                  required
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded mt-1"
                />
                <label for="terms" class="ml-2 block text-sm text-gray-700">
                  I agree to the <a href="#" class="text-primary-600 hover:text-primary-700 font-medium">Terms and Conditions</a> and <a href="#" class="text-primary-600 hover:text-primary-700 font-medium">Privacy Policy</a>
                </label>
              </div>

              <!-- Error Message -->
              <div id="error-message" class="hidden bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                id="register-btn"
                class="w-full btn-primary flex items-center justify-center"
              >
                <span id="register-btn-text">Create Account</span>
                <svg id="register-spinner" class="hidden animate-spin ml-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </button>
            </form>

            <!-- Divider -->
            <div class="mt-6">
              <div class="relative">
                <div class="absolute inset-0 flex items-center">
                  <div class="w-full border-t border-gray-300"></div>
                </div>
                <div class="relative flex justify-center text-sm">
                  <span class="px-2 bg-white text-gray-500">Or continue with</span>
                </div>
              </div>
            </div>

            <!-- Google Sign In -->
            <div id="google-signin-container" class="mt-6">
              <!-- Google button will be inserted here -->
            </div>

            <!-- Divider -->
            <div class="mt-6">
              <div class="relative">
                <div class="absolute inset-0 flex items-center">
                  <div class="w-full border-t border-gray-300"></div>
                </div>
                <div class="relative flex justify-center text-sm">
                  <span class="px-2 bg-white text-gray-500">Already have an account?</span>
                </div>
              </div>
            </div>

            <!-- Login Link -->
            <div class="mt-6">
              <button
                id="login-link"
                class="w-full btn-secondary"
              >
                Sign In
              </button>
            </div>
          </div>
        </div>
      </div>
    `,this.attachEventListeners())}attachEventListeners(){const e=document.getElementById("register-form"),t=document.getElementById("login-link");e&&e.addEventListener("submit",async s=>{s.preventDefault(),await this.handleRegister(e)}),t&&t.addEventListener("click",s=>{s.preventDefault(),y.navigate("/login")}),this.setupGoogleSignIn()}setupGoogleSignIn(){const e=document.getElementById("google-signin-container");if(!e)return;this.googleButton=new w("Sign up with Google",s=>{const n=document.getElementById("error-message");n&&(n.textContent=s.message||"Failed to sign up with Google",n.classList.remove("hidden"))}),e.innerHTML=this.googleButton.getHTML();const t=e.querySelector(".google-signin-btn");t&&this.googleButton.attachEventListener(t)}async handleRegister(e){var g,p;const t=e.querySelector("#username"),s=e.querySelector("#email"),n=e.querySelector("#full_name"),l=e.querySelector("#password"),m=e.querySelector("#confirm-password"),u=document.getElementById("register-btn"),d=document.getElementById("register-btn-text"),i=document.getElementById("register-spinner"),r=document.getElementById("error-message");if(!(!t||!s||!l||!m)){if(l.value!==m.value){r&&(r.textContent="Passwords do not match.",r.classList.remove("hidden"));return}if(l.value.length<8){r&&(r.textContent="Password must be at least 8 characters long.",r.classList.remove("hidden"));return}u.disabled=!0,d&&(d.textContent="Creating account..."),i==null||i.classList.remove("hidden"),r==null||r.classList.add("hidden");try{const c=await x.register({username:t.value,email:s.value,password:l.value,full_name:n.value||void 0});h.setAuthenticated(c.user),await new Promise(o=>setTimeout(o,50)),y.navigate("/generate")}catch(c){if(r){const o=((p=(g=c.response)==null?void 0:g.data)==null?void 0:p.detail)||"Registration failed. Please try again.";r.textContent=typeof o=="string"?o:JSON.stringify(o),r.classList.remove("hidden")}}finally{u.disabled=!1,d&&(d.textContent="Create Account"),i==null||i.classList.add("hidden")}}}}export{B as RegisterPage};
