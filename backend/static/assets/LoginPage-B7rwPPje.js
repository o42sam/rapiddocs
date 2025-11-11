import{r as c,d as u,b as g}from"./index-CLOizYH_.js";class v{render(){const e=document.getElementById("app");e&&(e.innerHTML=`
      <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 pt-32 pb-12 px-4 sm:px-6 lg:px-8">
        <div class="max-w-md w-full space-y-8">
          <!-- Header -->
          <div class="text-center">
            <h2 class="text-4xl font-bold text-gray-900 mb-2">Welcome Back</h2>
            <p class="text-gray-600">Sign in to continue to RapidDocs</p>
          </div>

          <!-- Login Form -->
          <div class="bg-white rounded-xl shadow-lg p-8">
            <form id="login-form" class="space-y-6">
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
                  autocomplete="current-password"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  placeholder="Enter your password"
                />
              </div>

              <!-- Remember Me & Forgot Password -->
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label for="remember-me" class="ml-2 block text-sm text-gray-700">
                    Remember me
                  </label>
                </div>
                <a href="#" class="text-sm text-blue-600 hover:text-blue-700 font-medium">
                  Forgot password?
                </a>
              </div>

              <!-- Error Message -->
              <div id="error-message" class="hidden bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                id="login-btn"
                class="w-full btn-primary flex items-center justify-center"
              >
                <span id="login-btn-text">Sign In</span>
                <svg id="login-spinner" class="hidden animate-spin ml-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
                  <span class="px-2 bg-white text-gray-500">Don't have an account?</span>
                </div>
              </div>
            </div>

            <!-- Register Link -->
            <div class="mt-6">
              <button
                id="register-link"
                class="w-full btn-secondary"
              >
                Create Account
              </button>
            </div>
          </div>
        </div>
      </div>
    `,this.attachEventListeners())}attachEventListeners(){const e=document.getElementById("login-form"),i=document.getElementById("register-link");e&&e.addEventListener("submit",async t=>{t.preventDefault(),await this.handleLogin(e)}),i&&i.addEventListener("click",t=>{t.preventDefault(),c.navigate("/register")})}async handleLogin(e){var o,d;const i=e.querySelector("#email"),t=e.querySelector("#password"),l=document.getElementById("login-btn"),a=document.getElementById("login-btn-text"),s=document.getElementById("login-spinner"),r=document.getElementById("error-message");if(!(!i||!t)){l.disabled=!0,a&&(a.textContent="Signing in..."),s==null||s.classList.remove("hidden"),r==null||r.classList.add("hidden");try{const n=await u.login({email:i.value,password:t.value});g.setAuthenticated(n.user),await new Promise(m=>setTimeout(m,50)),c.navigate("/generate")}catch(n){r&&(r.textContent=((d=(o=n.response)==null?void 0:o.data)==null?void 0:d.detail)||"Invalid email or password. Please try again.",r.classList.remove("hidden"))}finally{l.disabled=!1,a&&(a.textContent="Sign In"),s==null||s.classList.add("hidden")}}}}export{v as LoginPage};
