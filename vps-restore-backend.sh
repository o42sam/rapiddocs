#!/bin/bash

# =============================================================================
# RapidDocs VPS Backend Restore Script
# Run this script DIRECTLY on the VPS to restore proper backend with templates
# =============================================================================

set -e

BACKEND_DIR="/home/docgen/backend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "================================================"
echo "RapidDocs Backend Restore Script"
echo "================================================"
echo ""

cd "$BACKEND_DIR"
log_info "Working directory: $(pwd)"

# Stop containers first
log_info "Stopping containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Create templates directory
log_info "Creating templates directory..."
mkdir -p app/templates

# Create login.html template
log_info "Creating login.html template..."
cat > app/templates/login.html << 'LOGINEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - RapidDocs Backend</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 400px;
            padding: 40px;
        }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { color: #333; font-size: 28px; font-weight: 700; }
        .logo .subtitle { color: #666; font-size: 14px; margin-top: 5px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; color: #555; font-size: 14px; font-weight: 600; margin-bottom: 8px; }
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus { outline: none; border-color: #667eea; }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4); }
        .btn:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }
        .error-message { color: #e74c3c; font-size: 14px; margin-top: 10px; padding: 10px; background: #fee; border-radius: 4px; display: none; }
        .success-message { color: #27ae60; font-size: 14px; margin-top: 10px; padding: 10px; background: #efe; border-radius: 4px; display: none; }
        .links { text-align: center; margin-top: 20px; }
        .links a { color: #667eea; text-decoration: none; font-size: 14px; }
        .links a:hover { text-decoration: underline; }
        .spinner { display: none; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>RapidDocs Admin</h1>
            <div class="subtitle">Backend Administration Portal</div>
        </div>
        <form id="loginForm">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autocomplete="username">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="current-password">
            </div>
            <button type="submit" class="btn" id="loginBtn">
                <span id="btnText">Sign In</span>
                <div class="spinner" id="spinner"></div>
            </button>
        </form>
        <div class="error-message" id="errorMessage"></div>
        <div class="success-message" id="successMessage"></div>
        <div class="links">
            <a href="/register">Create Admin Account</a>
        </div>
    </div>
    <script>
        const API_URL = window.location.origin;
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('errorMessage');
            const successDiv = document.getElementById('successMessage');
            const loginBtn = document.getElementById('loginBtn');
            const btnText = document.getElementById('btnText');
            const spinner = document.getElementById('spinner');
            errorDiv.style.display = 'none';
            successDiv.style.display = 'none';
            loginBtn.disabled = true;
            btnText.style.display = 'none';
            spinner.style.display = 'block';
            try {
                const response = await fetch(`${API_URL}/admin/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                });
                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('refresh_token', data.refresh_token);
                    successDiv.textContent = 'Login successful! Redirecting...';
                    successDiv.style.display = 'block';
                    setTimeout(() => { window.location.href = '/admin/dashboard'; }, 1000);
                } else {
                    errorDiv.textContent = data.detail || 'Invalid username or password';
                    errorDiv.style.display = 'block';
                }
            } catch (error) {
                errorDiv.textContent = 'Network error. Please try again.';
                errorDiv.style.display = 'block';
            } finally {
                loginBtn.disabled = false;
                btnText.style.display = 'inline';
                spinner.style.display = 'none';
            }
        });
    </script>
</body>
</html>
LOGINEOF

# Create register.html template
log_info "Creating register.html template..."
cat > app/templates/register.html << 'REGISTEREOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Registration - RapidDocs Backend</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 400px;
            padding: 40px;
        }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { color: #333; font-size: 28px; font-weight: 700; }
        .logo .subtitle { color: #666; font-size: 14px; margin-top: 5px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; color: #555; font-size: 14px; font-weight: 600; margin-bottom: 8px; }
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus { outline: none; border-color: #667eea; }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4); }
        .btn:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }
        .error-message { color: #e74c3c; font-size: 14px; margin-top: 10px; padding: 10px; background: #fee; border-radius: 4px; display: none; }
        .success-message { color: #27ae60; font-size: 14px; margin-top: 10px; padding: 10px; background: #efe; border-radius: 4px; display: none; }
        .links { text-align: center; margin-top: 20px; }
        .links a { color: #667eea; text-decoration: none; font-size: 14px; }
        .links a:hover { text-decoration: underline; }
        .info-box { background: #f0f4ff; border: 1px solid #667eea; border-radius: 6px; padding: 15px; margin-bottom: 20px; font-size: 13px; color: #555; }
        .spinner { display: none; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>RapidDocs Admin</h1>
            <div class="subtitle">Create Admin Account</div>
        </div>
        <div class="info-box">
            A valid referral key is required to create an admin account. Contact your system administrator for a key.
        </div>
        <form id="registerForm">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autocomplete="username">
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required autocomplete="email">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="new-password">
            </div>
            <div class="form-group">
                <label for="confirmPassword">Confirm Password</label>
                <input type="password" id="confirmPassword" name="confirmPassword" required autocomplete="new-password">
            </div>
            <div class="form-group">
                <label for="referralKey">Referral Key</label>
                <input type="text" id="referralKey" name="referralKey" required placeholder="Enter your referral key">
            </div>
            <button type="submit" class="btn" id="registerBtn">
                <span id="btnText">Create Account</span>
                <div class="spinner" id="spinner"></div>
            </button>
        </form>
        <div class="error-message" id="errorMessage"></div>
        <div class="success-message" id="successMessage"></div>
        <div class="links">
            <a href="/login">Already have an account? Sign In</a>
        </div>
    </div>
    <script>
        const API_URL = window.location.origin;
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const referralKey = document.getElementById('referralKey').value;
            const errorDiv = document.getElementById('errorMessage');
            const successDiv = document.getElementById('successMessage');
            const registerBtn = document.getElementById('registerBtn');
            const btnText = document.getElementById('btnText');
            const spinner = document.getElementById('spinner');
            errorDiv.style.display = 'none';
            successDiv.style.display = 'none';
            if (password !== confirmPassword) {
                errorDiv.textContent = 'Passwords do not match';
                errorDiv.style.display = 'block';
                return;
            }
            registerBtn.disabled = true;
            btnText.style.display = 'none';
            spinner.style.display = 'block';
            try {
                const response = await fetch(`${API_URL}/admin/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password, referral_key: referralKey }),
                });
                const data = await response.json();
                if (response.ok) {
                    successDiv.textContent = 'Account created successfully! Redirecting to login...';
                    successDiv.style.display = 'block';
                    setTimeout(() => { window.location.href = '/login'; }, 2000);
                } else {
                    errorDiv.textContent = data.detail || 'Registration failed';
                    errorDiv.style.display = 'block';
                }
            } catch (error) {
                errorDiv.textContent = 'Network error. Please try again.';
                errorDiv.style.display = 'block';
            } finally {
                registerBtn.disabled = false;
                btnText.style.display = 'inline';
                spinner.style.display = 'none';
            }
        });
    </script>
</body>
</html>
REGISTEREOF

# Create dashboard.html template
log_info "Creating dashboard.html template..."
cat > app/templates/dashboard.html << 'DASHEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - RapidDocs</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f6fa;
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }
        .navbar h1 { font-size: 24px; }
        .navbar .logout-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 8px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }
        .navbar .logout-btn:hover { background: rgba(255,255,255,0.3); }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stat-card h3 { color: #666; font-size: 14px; margin-bottom: 10px; }
        .stat-card .value { font-size: 32px; font-weight: 700; color: #333; }
        .section { background: white; border-radius: 12px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .section h2 { color: #333; margin-bottom: 20px; font-size: 20px; }
        .referral-key { background: #f0f4ff; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 16px; word-break: break-all; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; margin-top: 15px; }
        .btn:hover { opacity: 0.9; }
        .loading { text-align: center; padding: 50px; color: #666; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>RapidDocs Admin Dashboard</h1>
        <button class="logout-btn" onclick="logout()">Logout</button>
    </nav>
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Users</h3>
                <div class="value" id="totalUsers">-</div>
            </div>
            <div class="stat-card">
                <h3>Documents Generated</h3>
                <div class="value" id="totalDocs">-</div>
            </div>
            <div class="stat-card">
                <h3>Active Admins</h3>
                <div class="value" id="totalAdmins">-</div>
            </div>
        </div>
        <div class="section">
            <h2>Referral Key Management</h2>
            <p>Use this key to invite new admin users:</p>
            <div class="referral-key" id="referralKey">Loading...</div>
            <button class="btn" onclick="generateNewKey()">Generate New Key</button>
        </div>
    </div>
    <script>
        const API_URL = window.location.origin;
        const token = localStorage.getItem('access_token');
        if (!token) { window.location.href = '/login'; }
        async function fetchDashboard() {
            try {
                const response = await fetch(`${API_URL}/admin/dashboard-data`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.status === 401) { window.location.href = '/login'; return; }
                const data = await response.json();
                document.getElementById('totalUsers').textContent = data.total_users || 0;
                document.getElementById('totalDocs').textContent = data.total_documents || 0;
                document.getElementById('totalAdmins').textContent = data.total_admins || 0;
                document.getElementById('referralKey').textContent = data.referral_key || 'No key available';
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error);
            }
        }
        async function generateNewKey() {
            try {
                const response = await fetch(`${API_URL}/admin/generate-referral-key`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                document.getElementById('referralKey').textContent = data.referral_key || 'Error generating key';
            } catch (error) {
                console.error('Failed to generate key:', error);
            }
        }
        function logout() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
        }
        fetchDashboard();
    </script>
</body>
</html>
DASHEOF

log_success "Templates created"

# Rebuild and restart
log_info "Rebuilding Docker containers..."
docker-compose build --no-cache 2>/dev/null || docker compose build --no-cache

log_info "Starting containers..."
docker-compose up -d 2>/dev/null || docker compose up -d

# Wait and check
sleep 10

log_info "Checking container status..."
docker-compose ps 2>/dev/null || docker compose ps

log_info "Testing endpoints..."
echo ""
echo "Root endpoint:"
curl -s http://localhost:8000/ | head -c 200
echo ""
echo ""
echo "Health endpoint:"
curl -s http://localhost:8000/health
echo ""

log_success "Restore complete!"
echo ""
echo "Test URLs:"
echo "  - https://api.rapiddocs.io/"
echo "  - https://api.rapiddocs.io/login"
echo "  - https://api.rapiddocs.io/register"
echo ""
