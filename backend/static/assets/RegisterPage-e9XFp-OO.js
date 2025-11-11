import{r as p,d as f,b as g}from"./index-CLOizYH_.js";class x{render(){const e=document.getElementById("app");e&&(e.innerHTML=`
      <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 pt-32 pb-12 px-4 sm:px-6 lg:px-8">
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
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
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
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
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
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
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
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
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
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
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
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
                />
                <label for="terms" class="ml-2 block text-sm text-gray-700">
                  I agree to the <a href="#" class="text-blue-600 hover:text-blue-700 font-medium">Terms and Conditions</a> and <a href="#" class="text-blue-600 hover:text-blue-700 font-medium">Privacy Policy</a>
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
    `,this.attachEventListeners())}attachEventListeners(){const e=document.getElementById("register-form"),a=document.getElementById("login-link");e&&e.addEventListener("submit",async s=>{s.preventDefault(),await this.handleRegister(e)}),a&&a.addEventListener("click",s=>{s.preventDefault(),p.navigate("/login")})}async handleRegister(e){var u,m;const a=e.querySelector("#username"),s=e.querySelector("#email"),b=e.querySelector("#full_name"),n=e.querySelector("#password"),d=e.querySelector("#confirm-password"),c=document.getElementById("register-btn"),i=document.getElementById("register-btn-text"),r=document.getElementById("register-spinner"),t=document.getElementById("error-message");if(!(!a||!s||!n||!d)){if(n.value!==d.value){t&&(t.textContent="Passwords do not match.",t.classList.remove("hidden"));return}if(n.value.length<8){t&&(t.textContent="Password must be at least 8 characters long.",t.classList.remove("hidden"));return}c.disabled=!0,i&&(i.textContent="Creating account..."),r==null||r.classList.remove("hidden"),t==null||t.classList.add("hidden");try{const o=await f.register({username:a.value,email:s.value,password:n.value,full_name:b.value||void 0});g.setAuthenticated(o.user),await new Promise(l=>setTimeout(l,50)),p.navigate("/generate")}catch(o){if(t){const l=((m=(u=o.response)==null?void 0:u.data)==null?void 0:m.detail)||"Registration failed. Please try again.";t.textContent=typeof l=="string"?l:JSON.stringify(l),t.classList.remove("hidden")}}finally{c.disabled=!1,i&&(i.textContent="Create Account"),r==null||r.classList.add("hidden")}}}}export{x as RegisterPage};
