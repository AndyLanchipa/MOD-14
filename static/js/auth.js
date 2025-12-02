// API Configuration
const API_BASE_URL = window.location.origin;
const API_ENDPOINTS = {
    register: '/api/users/register',
    login: '/api/users/login',
    getCurrentUser: '/api/users/me',
    calculations: '/api/calculations',
    calculationById: (id) => `/api/calculations/${id}`
};

// Token Management
function setToken(token) {
    localStorage.setItem('access_token', token);
}

function getToken() {
    return localStorage.getItem('access_token');
}

function removeToken() {
    localStorage.removeItem('access_token');
}

function isTokenExpired() {
    const token = getToken();
    if (!token) return true;
    
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expirationTime = payload.exp * 1000;
        return Date.now() >= expirationTime;
    } catch (error) {
        return true;
    }
}

// Validation Functions
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePassword(password) {
    if (password.length < 8) {
        return { valid: false, message: 'Password must be at least 8 characters long' };
    }
    if (!/[A-Z]/.test(password)) {
        return { valid: false, message: 'Password must contain at least one uppercase letter' };
    }
    if (!/[a-z]/.test(password)) {
        return { valid: false, message: 'Password must contain at least one lowercase letter' };
    }
    if (!/[0-9]/.test(password)) {
        return { valid: false, message: 'Password must contain at least one digit' };
    }
    if (password.length > 72) {
        return { valid: false, message: 'Password must not exceed 72 characters' };
    }
    return { valid: true, message: '' };
}

function validateUsername(username) {
    if (username.length < 3 || username.length > 50) {
        return { valid: false, message: 'Username must be between 3 and 50 characters' };
    }
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        return { valid: false, message: 'Username can only contain letters, numbers, and underscores' };
    }
    return { valid: true, message: '' };
}

// UI Helper Functions
function showMessage(message, type = 'error') {
    const messageContainer = document.getElementById('message-container');
    const messageText = document.getElementById('message-text');

    function formatMessage(msg) {
        if (typeof msg === 'string') return msg;
        if (Array.isArray(msg)) {
            // Pydantic/validation errors array
            return msg
                .map((m) => m?.msg || m?.message || (typeof m === 'string' ? m : JSON.stringify(m)))
                .join('; ');
        }
        if (msg && typeof msg === 'object') {
            // FastAPI error shape {detail: ...}
            if (msg.detail) return formatMessage(msg.detail);
            return JSON.stringify(msg);
        }
        return String(msg);
    }

    messageContainer.className = `message-container ${type}`;
    messageText.textContent = formatMessage(message);
    messageContainer.style.display = 'block';

    setTimeout(() => {
        messageContainer.style.display = 'none';
    }, 5000);
}

function showFieldError(fieldId, message) {
    const errorElement = document.getElementById(`${fieldId}-error`);
    const inputElement = document.getElementById(fieldId);
    
    if (errorElement && inputElement) {
        errorElement.textContent = message;
        inputElement.classList.add('error');
        inputElement.classList.remove('success');
    }
}

function clearFieldError(fieldId) {
    const errorElement = document.getElementById(`${fieldId}-error`);
    const inputElement = document.getElementById(fieldId);
    
    if (errorElement && inputElement) {
        errorElement.textContent = '';
        inputElement.classList.remove('error');
    }
}

function setFieldSuccess(fieldId) {
    const inputElement = document.getElementById(fieldId);
    if (inputElement) {
        inputElement.classList.remove('error');
        inputElement.classList.add('success');
    }
}

function clearAllErrors() {
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    document.querySelectorAll('input').forEach(input => {
        input.classList.remove('error');
        input.classList.remove('success');
    });
}

function setButtonLoading(buttonId, isLoading) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = isLoading;
        button.textContent = isLoading ? 'Processing...' : button.getAttribute('data-original-text') || button.textContent;
        if (!isLoading && !button.hasAttribute('data-original-text')) {
            button.setAttribute('data-original-text', button.textContent);
        }
    }
}

// API Call Functions
async function registerUser(userData) {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.register}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw { status: response.status, data };
    }
    
    return data;
}

async function loginUser(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.login}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw { status: response.status, data };
    }
    
    return data;
}

async function getCurrentUser() {
    const token = getToken();
    
    if (!token) {
        throw new Error('No authentication token found');
    }
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.getCurrentUser}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw { status: response.status, data };
    }
    
    return data;
}

// Registration Page Functions
function initRegisterPage() {
    const form = document.getElementById('register-form');
    const submitBtn = document.getElementById('submit-btn');
    
    submitBtn.setAttribute('data-original-text', 'Register');
    
    // Real-time validation
    document.getElementById('username').addEventListener('blur', function() {
        const validation = validateUsername(this.value);
        if (this.value && !validation.valid) {
            showFieldError('username', validation.message);
        } else if (this.value) {
            setFieldSuccess('username');
            clearFieldError('username');
        }
    });
    
    document.getElementById('email').addEventListener('blur', function() {
        if (this.value && !validateEmail(this.value)) {
            showFieldError('email', 'Please enter a valid email address');
        } else if (this.value) {
            setFieldSuccess('email');
            clearFieldError('email');
        }
    });
    
    document.getElementById('password').addEventListener('blur', function() {
        const validation = validatePassword(this.value);
        if (this.value && !validation.valid) {
            showFieldError('password', validation.message);
        } else if (this.value) {
            setFieldSuccess('password');
            clearFieldError('password');
        }
    });
    
    document.getElementById('confirm-password').addEventListener('blur', function() {
        const password = document.getElementById('password').value;
        if (this.value && this.value !== password) {
            showFieldError('confirm-password', 'Passwords do not match');
        } else if (this.value) {
            setFieldSuccess('confirm-password');
            clearFieldError('confirm-password');
        }
    });
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        clearAllErrors();
        
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        
        let hasError = false;
        
        // Validate username
        const usernameValidation = validateUsername(username);
        if (!usernameValidation.valid) {
            showFieldError('username', usernameValidation.message);
            hasError = true;
        }
        
        // Validate email
        if (!validateEmail(email)) {
            showFieldError('email', 'Please enter a valid email address');
            hasError = true;
        }
        
        // Validate password
        const passwordValidation = validatePassword(password);
        if (!passwordValidation.valid) {
            showFieldError('password', passwordValidation.message);
            hasError = true;
        }
        
        // Validate confirm password
        if (password !== confirmPassword) {
            showFieldError('confirm-password', 'Passwords do not match');
            hasError = true;
        }
        
        if (hasError) {
            return;
        }
        
        setButtonLoading('submit-btn', true);
        
        try {
            const userData = {
                username: username,
                email: email,
                password: password
            };
            
            const response = await registerUser(userData);
            
            showMessage('Registration successful! Redirecting to login...', 'success');
            
            setTimeout(() => {
                window.location.href = '/static/login.html';
            }, 1500);
            
        } catch (error) {
            console.error('Registration error:', error);
            
            if (error.status === 400 && error.data.detail) {
                if (typeof error.data.detail === 'string') {
                    showMessage(error.data.detail, 'error');
                } else if (Array.isArray(error.data.detail)) {
                    const errorMessages = error.data.detail.map(err => err.msg).join(', ');
                    showMessage(errorMessages, 'error');
                } else {
                    showMessage('Registration failed. Please check your input.', 'error');
                }
            } else {
                showMessage('Registration failed. Please try again.', 'error');
            }
            
            setButtonLoading('submit-btn', false);
        }
    });
}

// Login Page Functions
function initLoginPage() {
    const form = document.getElementById('login-form');
    const submitBtn = document.getElementById('submit-btn');
    
    submitBtn.setAttribute('data-original-text', 'Login');
    
    // Check if already logged in
    if (getToken() && !isTokenExpired()) {
        window.location.href = '/static/dashboard.html';
        return;
    }
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        clearAllErrors();
        
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        
        let hasError = false;
        
        if (!username) {
            showFieldError('username', 'Username or email is required');
            hasError = true;
        }
        
        if (!password) {
            showFieldError('password', 'Password is required');
            hasError = true;
        }
        
        if (hasError) {
            return;
        }
        
        setButtonLoading('submit-btn', true);
        
        try {
            const response = await loginUser(username, password);
            
            setToken(response.access_token);
            
            showMessage('Login successful! Redirecting to dashboard...', 'success');
            
            setTimeout(() => {
                window.location.href = '/static/dashboard.html';
            }, 1000);
            
        } catch (error) {
            console.error('Login error:', error);
            
            if (error.status === 401) {
                showMessage('Invalid username or password. Please try again.', 'error');
            } else if (error.status === 400 && error.data.detail) {
                showMessage(error.data.detail, 'error');
            } else {
                showMessage('Login failed. Please try again.', 'error');
            }
            
            setButtonLoading('submit-btn', false);
        }
    });
}

// Dashboard Page Functions
function initDashboardPage() {
    // Check authentication
    if (!getToken() || isTokenExpired()) {
        window.location.href = '/static/login.html';
        return;
    }
    
    // Load user information
    loadUserInfo();
    
    // Initialize calculations functionality
    initCalculationsPage();
    
    // Setup logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            removeToken();
            showMessage('Logged out successfully', 'success');
            setTimeout(() => {
                window.location.href = '/static/login.html';
            }, 1000);
        });
    }
}

async function loadUserInfo() {
    const userInfoDiv = document.getElementById('user-info');
    
    try {
        const user = await getCurrentUser();
        
        userInfoDiv.innerHTML = `
            <p><strong>Username:</strong> ${user.username}</p>
            <p><strong>Email:</strong> ${user.email}</p>
            <p><strong>User ID:</strong> ${user.id}</p>
            <p><strong>Account Created:</strong> ${new Date(user.created_at).toLocaleDateString()}</p>
            <p><strong>Status:</strong> ${user.is_active ? 'Active' : 'Inactive'}</p>
        `;
        
    } catch (error) {
        console.error('Error loading user info:', error);
        
        if (error.status === 401) {
            showMessage('Session expired. Please login again.', 'error');
            setTimeout(() => {
                removeToken();
                window.location.href = '/static/login.html';
            }, 2000);
        } else {
            userInfoDiv.innerHTML = '<p class="error-message">Failed to load user information</p>';
        }
    }
}

// Calculation API Functions
async function createCalculation(a, b, type) {
    const token = getToken();
    if (!token) throw new Error('No authentication token found');
    
   console.log("Creating calculation with a:", a, "b:", b, "type:", type);
    
    // Normalize legacy operation values from UI or cached DOM
    const normalizedType = (function(t){
        if (t === 'SUBTRACT') return 'SUB';
        return t;
    })(type);

    console.log("Normalized type:", normalizedType);
    const requestBody = { a: parseFloat(a), b: parseFloat(b), type: normalizedType };
    console.log("Request body:", JSON.stringify(requestBody));
    console.log("================================");
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.calculations}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
    });
    
    const data = await response.json();
    console.log("API Response:", data);
    if (!response.ok) throw { status: response.status, data };
    return data;
}

async function getCalculations(skip = 0, limit = 20) {
    const token = getToken();
    if (!token) throw new Error('No authentication token found');
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.calculations}?skip=${skip}&limit=${limit}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    const data = await response.json();
    if (!response.ok) throw { status: response.status, data };
    return data;
}

async function updateCalculation(id, updates) {
    const token = getToken();
    if (!token) throw new Error('No authentication token found');
    
    const body = {};
    if (updates.a !== undefined) body.a = parseFloat(updates.a);
    if (updates.b !== undefined) body.b = parseFloat(updates.b);
    if (updates.type !== undefined) body.type = updates.type;
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.calculationById(id)}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(body)
    });
    
    const data = await response.json();
    if (!response.ok) throw { status: response.status, data };
    return data;
}

async function deleteCalculation(id) {
    const token = getToken();
    if (!token) throw new Error('No authentication token found');
    
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.calculationById(id)}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (!response.ok) {
        const data = await response.json();
        throw { status: response.status, data };
    }
    return true;
}

// Calculation UI Functions
let currentPage = 0;
const itemsPerPage = 20;
let currentDeleteId = null;

function getOperationSymbol(type) {
    const symbols = {
        'ADD': '+',
        'SUB': '-',
        'MULTIPLY': '×',
        'DIVIDE': '÷'
    };
    return symbols[type] || type;
}

function getOperationName(type) {
    const names = {
        'ADD': 'Addition',
        'SUB': 'Subtraction',
        'MULTIPLY': 'Multiplication',
        'DIVIDE': 'Division'
    };
    return names[type] || type;
}

function calculatePreview(a, b, type) {
    const numA = parseFloat(a);
    const numB = parseFloat(b);
    
    if (isNaN(numA) || isNaN(numB)) return null;
    
    let result;
    switch (type) {
        case 'ADD':
            result = numA + numB;
            break;
        case 'SUB':
            result = numA - numB;
            break;
        case 'MULTIPLY':
            result = numA * numB;
            break;
        case 'DIVIDE':
            if (numB === 0) return { error: 'Cannot divide by zero' };
            result = numA / numB;
            break;
        default:
            return null;
    }
    
    return { result, expression: `${numA} ${getOperationSymbol(type)} ${numB} = ${result}` };
}

function renderCalculationsList(calculations) {
    const listContainer = document.getElementById('calculations-list');
    
    if (!calculations || calculations.length === 0) {
        listContainer.innerHTML = '<p class="empty-state">No calculations yet. Create your first calculation above.</p>';
        return;
    }
    
    const table = document.createElement('table');
    table.className = 'calculations-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Expression</th>
                <th>Result</th>
                <th>Created</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            ${calculations.map(calc => `
                <tr data-calc-id="${calc.id}">
                    <td class="calculation-expression">${calc.a} ${getOperationSymbol(calc.type)} ${calc.b}</td>
                    <td class="calculation-result">${calc.result !== null ? calc.result : 'N/A'}</td>
                    <td class="calculation-date">${new Date(calc.created_at).toLocaleString()}</td>
                    <td class="calculation-actions">
                        <button class="btn btn-small btn-edit" data-calc-id="${calc.id}">Edit</button>
                        <button class="btn btn-small btn-danger" data-calc-id="${calc.id}">Delete</button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;
    
    listContainer.innerHTML = '';
    listContainer.appendChild(table);
    
    attachCalculationEventListeners();
}

function attachCalculationEventListeners() {
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', handleEditClick);
    });
    
    document.querySelectorAll('.btn-danger').forEach(btn => {
        btn.addEventListener('click', handleDeleteClick);
    });
}

async function loadCalculations(page = 0) {
    const loadingDiv = document.getElementById('calculations-list-loading');
    const listContainer = document.getElementById('calculations-list');
    
    try {
        loadingDiv.style.display = 'block';
        listContainer.innerHTML = '';
        
        const calculations = await getCalculations(page * itemsPerPage, itemsPerPage);
        
        loadingDiv.style.display = 'none';
        renderCalculationsList(calculations);
        
        updatePaginationControls(calculations.length);
        
    } catch (error) {
        console.error('Error loading calculations:', error);
        loadingDiv.style.display = 'none';
        
        if (error.status === 401) {
            showMessage('Session expired. Please login again.', 'error');
            setTimeout(() => {
                removeToken();
                window.location.href = '/static/login.html';
            }, 2000);
        } else {
            listContainer.innerHTML = '<p class="error-message">Failed to load calculations</p>';
        }
    }
}

function updatePaginationControls(resultCount) {
    const paginationDiv = document.getElementById('pagination-controls');
    
    if (currentPage === 0 && resultCount < itemsPerPage) {
        paginationDiv.style.display = 'none';
        return;
    }
    
    paginationDiv.style.display = 'flex';
    paginationDiv.innerHTML = `
        <button id="prev-page" class="btn btn-secondary" ${currentPage === 0 ? 'disabled' : ''}>Previous</button>
        <span class="page-info">Page ${currentPage + 1}</span>
        <button id="next-page" class="btn btn-secondary" ${resultCount < itemsPerPage ? 'disabled' : ''}>Next</button>
    `;
    
    document.getElementById('prev-page')?.addEventListener('click', () => {
        if (currentPage > 0) {
            currentPage--;
            loadCalculations(currentPage);
        }
    });
    
    document.getElementById('next-page')?.addEventListener('click', () => {
        if (resultCount >= itemsPerPage) {
            currentPage++;
            loadCalculations(currentPage);
        }
    });
}

function handleEditClick(event) {
    const calcId = event.target.dataset.calcId;
    const row = document.querySelector(`tr[data-calc-id="${calcId}"]`);
    
    if (!row) return;
    
    const cells = row.querySelectorAll('td');
    const expression = cells[0].textContent.trim();
    const parts = expression.split(' ');
    
    const a = parts[0];
    const symbol = parts[1];
    const b = parts[2];
    
    let type = 'ADD';
    switch (symbol) {
        case '+': type = 'ADD'; break;
        case '-': type = 'SUB'; break;
        case '×': type = 'MULTIPLY'; break;
        case '÷': type = 'DIVIDE'; break;
    }
    
    document.getElementById('edit-calc-id').value = calcId;
    document.getElementById('edit-operand-a').value = a;
    document.getElementById('edit-operand-b').value = b;
    document.getElementById('edit-operation-type').value = type;
    
    showModal('edit-modal');
}

function handleDeleteClick(event) {
    const calcId = event.target.dataset.calcId;
    const row = document.querySelector(`tr[data-calc-id="${calcId}"]`);
    
    if (!row) return;
    
    const expression = row.querySelector('.calculation-expression').textContent;
    const result = row.querySelector('.calculation-result').textContent;
    
    currentDeleteId = calcId;
    document.getElementById('delete-calc-info').innerHTML = `
        <p><strong>Expression:</strong> ${expression}</p>
        <p><strong>Result:</strong> ${result}</p>
    `;
    
    showModal('delete-modal');
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

function initCalculationForm() {
    const form = document.getElementById('calculation-form');
    const previewDiv = document.getElementById('calculation-preview');
    const operandA = document.getElementById('operand-a');
    const operandB = document.getElementById('operand-b');
    const operationType = document.getElementById('operation-type');
    
    function updatePreview() {
        const a = operandA.value;
        const b = operandB.value;
        const type = operationType.value;
        
        if (a && b && type) {
            const preview = calculatePreview(a, b, type);
            if (preview) {
                if (preview.error) {
                    previewDiv.innerHTML = `<span class="preview-error">${preview.error}</span>`;
                    previewDiv.style.display = 'block';
                } else {
                    previewDiv.innerHTML = `<span class="preview-result">Preview: ${preview.expression}</span>`;
                    previewDiv.style.display = 'block';
                }
            } else {
                previewDiv.style.display = 'none';
            }
        } else {
            previewDiv.style.display = 'none';
        }
    }
    
    operandA.addEventListener('input', updatePreview);
    operandB.addEventListener('input', updatePreview);
    operationType.addEventListener('change', updatePreview);
    
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const submitBtn = document.getElementById('create-calc-btn');
        const originalText = submitBtn.textContent;
        
        const a = operandA.value;
        const b = operandB.value;
        let type = operationType.value;
        
        console.log("Form submission - original type:", type);
        
        // Normalize type early in case of cached/old values
        if (type === 'SUBTRACT') {
            type = 'SUB';
            console.log("Form normalized SUBTRACT to SUB");
        }
        
        if (type === 'DIVIDE' && parseFloat(b) === 0) {
            showMessage('Cannot divide by zero', 'error');
            return;
        }
        
        try {
            submitBtn.textContent = 'Creating...';
            submitBtn.disabled = true;
            
            await createCalculation(a, b, type);
            
            form.reset();
            previewDiv.style.display = 'none';
            
            await loadCalculations(currentPage);
            
            showMessage('Calculation created successfully', 'success');
            
        } catch (error) {
            console.error('Error creating calculation:', error);
            
            if (error.status === 401) {
                showMessage('Session expired. Please login again.', 'error');
                setTimeout(() => {
                    removeToken();
                    window.location.href = '/static/login.html';
                }, 2000);
            } else {
                const message = error.data?.detail || error.data || 'Failed to create calculation';
                showMessage(message, 'error');
            }
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
}

function initEditForm() {
    const form = document.getElementById('edit-calculation-form');
    const previewDiv = document.getElementById('edit-calculation-preview');
    const operandA = document.getElementById('edit-operand-a');
    const operandB = document.getElementById('edit-operand-b');
    const operationType = document.getElementById('edit-operation-type');
    
    function updateEditPreview() {
        const a = operandA.value;
        const b = operandB.value;
        const type = operationType.value;
        
        if (a && b && type) {
            const preview = calculatePreview(a, b, type);
            if (preview) {
                if (preview.error) {
                    previewDiv.innerHTML = `<span class="preview-error">${preview.error}</span>`;
                    previewDiv.style.display = 'block';
                } else {
                    previewDiv.innerHTML = `<span class="preview-result">Preview: ${preview.expression}</span>`;
                    previewDiv.style.display = 'block';
                }
            } else {
                previewDiv.style.display = 'none';
            }
        } else {
            previewDiv.style.display = 'none';
        }
    }
    
    operandA.addEventListener('input', updateEditPreview);
    operandB.addEventListener('input', updateEditPreview);
    operationType.addEventListener('change', updateEditPreview);
    
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const calcId = document.getElementById('edit-calc-id').value;
        const a = operandA.value;
        const b = operandB.value;
        const type = operationType.value;
        
        if (type === 'DIVIDE' && parseFloat(b) === 0) {
            showMessage('Cannot divide by zero', 'error');
            return;
        }
        
        try {
            await updateCalculation(calcId, { a, b, type });
            
            showMessage('Calculation updated successfully', 'success');
            hideModal('edit-modal');
            
            await loadCalculations(currentPage);
            
        } catch (error) {
            console.error('Error updating calculation:', error);
            
            if (error.status === 401) {
                showMessage('Session expired. Please login again.', 'error');
                setTimeout(() => {
                    removeToken();
                    window.location.href = '/static/login.html';
                }, 2000);
            } else {
                const message = error.data?.detail || 'Failed to update calculation';
                showMessage(message, 'error');
            }
        }
    });
}

function initDeleteModal() {
    const confirmBtn = document.getElementById('confirm-delete-btn');
    
    confirmBtn.addEventListener('click', async function() {
        if (!currentDeleteId) return;
        
        try {
            await deleteCalculation(currentDeleteId);
            
            showMessage('Calculation deleted successfully', 'success');
            hideModal('delete-modal');
            currentDeleteId = null;
            
            await loadCalculations(currentPage);
            
        } catch (error) {
            console.error('Error deleting calculation:', error);
            
            if (error.status === 401) {
                showMessage('Session expired. Please login again.', 'error');
                setTimeout(() => {
                    removeToken();
                    window.location.href = '/static/login.html';
                }, 2000);
            } else {
                const message = error.data?.detail || 'Failed to delete calculation';
                showMessage(message, 'error');
            }
        }
    });
}

function initModalControls() {
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(element => {
        element.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                hideModal(modal.id);
            }
        });
    });
    
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                hideModal(modal.id);
            }
        });
    });
}

function initCalculationsPage() {
    initCalculationForm();
    initEditForm();
    initDeleteModal();
    initModalControls();
    loadCalculations(0);
}

