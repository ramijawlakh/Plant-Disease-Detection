// Global state management
const AppState = {
    user: null,
    token: null,
    isAuthenticated: false,
    currentSection: 'dashboard'
};

// API Configuration
const API_BASE = window.location.origin;
const API_ENDPOINTS = {
    auth: {
        register: '/api/auth/register',
        login: '/api/auth/login',
        me: '/api/auth/me'
    },
    predict: '/api/predict',
    chat: '/api/chat',
    history: '/api/history',
    analytics: '/api/analytics',
    predictions: '/api/predictions',
    chatHistory: '/api/chat/history'
};

// Utility Functions
const Utils = {
    showLoading: () => {
        document.getElementById('loadingSpinner').classList.remove('d-none');
    },
    
    hideLoading: () => {
        document.getElementById('loadingSpinner').classList.add('d-none');
    },
    
    showAlert: (message, type = 'success') => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    },
    
    formatDate: (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    },
    
    apiRequest: async (endpoint, options = {}) => {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(AppState.token && { 'Authorization': `Bearer ${AppState.token}` })
            }
        };
        
        const config = { ...defaultOptions, ...options };
        
        // Handle FormData
        if (options.body instanceof FormData) {
            delete config.headers['Content-Type'];
        }
        
        try {
            const response = await fetch(API_BASE + endpoint, config);
            
            if (response.status === 401) {
                Auth.logout();
                Utils.showAlert('Session expired. Please login again.', 'warning');
                return null;
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Request failed: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return response;
        } catch (error) {
            console.error('API Request failed:', error);
            Utils.showAlert(error.message, 'danger');
            throw error;
        }
    }
};

// Authentication Module
const Auth = {
    init: () => {
        const token = localStorage.getItem('authToken');
        const user = localStorage.getItem('user');
        
        if (token && user) {
            AppState.token = token;
            AppState.user = JSON.parse(user);
            AppState.isAuthenticated = true;
            Auth.updateUI();
            Auth.validateToken();
        }
    },
    
    validateToken: async () => {
        try {
            const user = await Utils.apiRequest(API_ENDPOINTS.auth.me);
            if (user) {
                AppState.user = user;
                localStorage.setItem('user', JSON.stringify(user));
                Auth.updateUI();
            }
        } catch (error) {
            Auth.logout();
        }
    },
    
    login: async (username, password) => {
        try {
            Utils.showLoading();
            const response = await Utils.apiRequest(API_ENDPOINTS.auth.login, {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
            
            AppState.token = response.access_token;
            AppState.isAuthenticated = true;
            
            localStorage.setItem('authToken', response.access_token);
            
            // Get user info
            const user = await Utils.apiRequest(API_ENDPOINTS.auth.me);
            AppState.user = user;
            localStorage.setItem('user', JSON.stringify(user));
            
            Auth.updateUI();
            Auth.closeAuthModal();
            Utils.showAlert('Login successful!');
            
            // Load dashboard data
            Dashboard.loadData();
            
        } catch (error) {
            Utils.showAlert('Login failed: ' + error.message, 'danger');
        } finally {
            Utils.hideLoading();
        }
    },
    
    register: async (userData) => {
        try {
            Utils.showLoading();
            await Utils.apiRequest(API_ENDPOINTS.auth.register, {
                method: 'POST',
                body: JSON.stringify(userData)
            });
            
            Utils.showAlert('Registration successful! Please login.');
            Auth.showAuthModal('login');
            
        } catch (error) {
            Utils.showAlert('Registration failed: ' + error.message, 'danger');
        } finally {
            Utils.hideLoading();
        }
    },
    
    logout: () => {
        AppState.token = null;
        AppState.user = null;
        AppState.isAuthenticated = false;
        
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        
        Auth.updateUI();
        Navigation.showSection('dashboard');
        Utils.showAlert('Logged out successfully');
    },
    
    updateUI: () => {
        const authButtons = document.getElementById('authButtons');
        const userInfo = document.getElementById('userInfo');
        const userName = document.getElementById('userName');
        
        if (AppState.isAuthenticated) {
            authButtons.classList.add('d-none');
            userInfo.classList.remove('d-none');
            userName.textContent = AppState.user?.username || 'User';
        } else {
            authButtons.classList.remove('d-none');
            userInfo.classList.add('d-none');
        }
    },
    
    showAuthModal: (mode) => {
        const modal = new bootstrap.Modal(document.getElementById('authModal'));
        const title = document.getElementById('authModalTitle');
        const fields = document.getElementById('authFields');
        const submitBtn = document.getElementById('authSubmitBtn');
        const switchLink = document.getElementById('authSwitchLink');
        
        if (mode === 'login') {
            title.textContent = 'Login';
            submitBtn.textContent = 'Login';
            switchLink.innerHTML = "Don't have an account? <span onclick=\"Auth.showAuthModal('register')\">Sign up</span>";
            fields.innerHTML = `
                <div class="mb-3">
                    <label class="form-label">Username</label>
                    <input type="text" class="form-control" name="username" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-control" name="password" required>
                </div>
            `;
        } else {
            title.textContent = 'Sign Up';
            submitBtn.textContent = 'Sign Up';
            switchLink.innerHTML = "Already have an account? <span onclick=\"Auth.showAuthModal('login')\">Login</span>";
            fields.innerHTML = `
                <div class="mb-3">
                    <label class="form-label">Full Name</label>
                    <input type="text" class="form-control" name="full_name">
                </div>
                <div class="mb-3">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" name="email" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Username</label>
                    <input type="text" class="form-control" name="username" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-control" name="password" required>
                </div>
            `;
        }
        
        modal.show();
    },
    
    closeAuthModal: () => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('authModal'));
        if (modal) modal.hide();
    }
};

// Navigation Module
const Navigation = {
    showSection: (sectionName) => {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('d-none');
        });
        
        // Show selected section
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.classList.remove('d-none');
            AppState.currentSection = sectionName;
            
            // Update nav links
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            
            // Load section-specific data
            switch (sectionName) {
                case 'dashboard':
                    Dashboard.loadData();
                    break;
                case 'history':
                    History.loadHistory();
                    break;
                case 'chat':
                    Chat.init();
                    break;
            }
        }
    }
};

// Dashboard Module
const Dashboard = {
    loadData: async () => {
        if (!AppState.isAuthenticated) {
            Dashboard.showGuestView();
            return;
        }
        
        try {
            const [analytics] = await Promise.all([
                Utils.apiRequest(API_ENDPOINTS.analytics).catch(() => null)
            ]);
            
            Dashboard.renderStats(analytics);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    },
    
    showGuestView: () => {
        const statsCards = document.getElementById('statsCards');
        statsCards.innerHTML = `
            <div class="col-12 text-center">
                <div class="card">
                    <div class="card-body">
                        <h5>Welcome to PlantCare AI</h5>
                        <p>Please login or register to access all features and track your plant health journey.</p>
                        <button class="btn btn-success me-2" onclick="Auth.showAuthModal('login')">Login</button>
                        <button class="btn btn-outline-success" onclick="Auth.showAuthModal('register')">Sign Up</button>
                    </div>
                </div>
            </div>
        `;
    },
    
    renderStats: (analytics) => {
        const statsCards = document.getElementById('statsCards');
        
        if (!analytics) {
            statsCards.innerHTML = `
                <div class="col-12 text-center">
                    <div class="card">
                        <div class="card-body">
                            <h5>Welcome back, ${AppState.user?.username}!</h5>
                            <p>Start using PlantCare AI to detect diseases and get care advice for your plants.</p>
                        </div>
                    </div>
                </div>
            `;
            return;
        }
        
        statsCards.innerHTML = `
            <div class="col-md-3 mb-4">
                <div class="stats-card">
                    <div class="stats-number">${analytics.total_predictions || 0}</div>
                    <div class="stats-label">Disease Detections</div>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="stats-card">
                    <div class="stats-number">${analytics.total_chats || 0}</div>
                    <div class="stats-label">Chat Conversations</div>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="stats-card">
                    <div class="stats-number">${analytics.total_users || 0}</div>
                    <div class="stats-label">Total Users</div>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="stats-card">
                    <div class="stats-number">${analytics.most_common_diseases?.length || 0}</div>
                    <div class="stats-label">Diseases Tracked</div>
                </div>
            </div>
        `;
    }
};

// Prediction Module
const Prediction = {
    init: () => {
        const form = document.getElementById('predictForm');
        const imageInput = document.getElementById('imageInput');
        const uploadBox = document.getElementById('uploadBox');
        const confidenceInput = document.getElementById('confidenceInput');
        const confidenceValue = document.getElementById('confidenceValue');
        
        // Confidence slider update
        confidenceInput.addEventListener('input', (e) => {
            confidenceValue.textContent = e.target.value;
        });
        
        // Drag and drop functionality
        uploadBox.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadBox.style.backgroundColor = '#e8f5e8';
        });
        
        uploadBox.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadBox.style.backgroundColor = '';
        });
        
        uploadBox.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadBox.style.backgroundColor = '';
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                imageInput.files = files;
                Prediction.previewImage(files[0]);
            }
        });
        
        // File input change
        imageInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                Prediction.previewImage(e.target.files[0]);
            }
        });
        
        // Form submission
        form.addEventListener('submit', Prediction.handlePrediction);
    },
    
    previewImage: (file) => {
        const uploadBox = document.getElementById('uploadBox');
        const reader = new FileReader();
        
        reader.onload = (e) => {
            uploadBox.innerHTML = `
                <img src="${e.target.result}" style="max-width: 100%; max-height: 200px; border-radius: 10px;">
                <p class="mt-2">Click to change image</p>
            `;
        };
        
        reader.readAsDataURL(file);
    },
    
    handlePrediction: async (e) => {
        e.preventDefault();
        
        if (!AppState.isAuthenticated) {
            Utils.showAlert('Please login to use disease detection', 'warning');
            Auth.showAuthModal('login');
            return;
        }
        
        const formData = new FormData();
        const fileInput = document.getElementById('imageInput');
        const confidence = document.getElementById('confidenceInput').value;
        
        if (!fileInput.files[0]) {
            Utils.showAlert('Please select an image', 'warning');
            return;
        }
        
        formData.append('file', fileInput.files[0]);
        formData.append('confidence_threshold', confidence);
        
        try {
            Utils.showLoading();
            const result = await Utils.apiRequest(API_ENDPOINTS.predict, {
                method: 'POST',
                body: formData
            });
            
            Prediction.displayResults(result);
            Utils.showAlert('Disease detection completed!');
            
        } catch (error) {
            Utils.showAlert('Prediction failed: ' + error.message, 'danger');
        } finally {
            Utils.hideLoading();
        }
    },
    
    displayResults: (result) => {
        const resultsDiv = document.getElementById('predictionResults');
        const resultImage = document.getElementById('resultImage');
        const detectionInfo = document.getElementById('detectionInfo');
        
        // Show results section
        resultsDiv.classList.remove('d-none');
        
        // Set image
        resultImage.src = result.image_url;
        
        // Display detection information
        let detectionHTML = `
            <h6>Detection Summary</h6>
            <p><strong>Total Detections:</strong> ${result.total_detections}</p>
            <p><strong>Average Confidence:</strong> ${(result.avg_confidence * 100).toFixed(1)}%</p>
        `;
        
        if (result.detected_diseases && result.detected_diseases.length > 0) {
            detectionHTML += `
                <h6 class="mt-3">Detected Diseases</h6>
                <div class="list-group">
            `;
            
            result.detected_diseases.forEach(disease => {
                detectionHTML += `
                    <div class="list-group-item">
                        <i class="fas fa-bug text-warning"></i> ${disease}
                    </div>
                `;
            });
            
            detectionHTML += '</div>';
        }
        
        if (result.predictions && result.predictions.length > 0) {
            detectionHTML += `
                <h6 class="mt-3">Detailed Predictions</h6>
            `;
            
            result.predictions.forEach((pred, index) => {
                detectionHTML += `
                    <div class="detection-card">
                        <strong>${pred.disease}</strong>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${pred.confidence * 100}%"></div>
                        </div>
                        <small>Confidence: ${(pred.confidence * 100).toFixed(1)}%</small>
                    </div>
                `;
            });
        }
        
        detectionInfo.innerHTML = detectionHTML;
        
        // Scroll to results
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }
};

// Chat Module
const Chat = {
    init: () => {
        const form = document.getElementById('chatForm');
        form.addEventListener('submit', Chat.handleMessage);
        
        // Load chat history if authenticated
        if (AppState.isAuthenticated) {
            Chat.loadChatHistory();
        }
    },
    
    loadChatHistory: async () => {
        try {
            const history = await Utils.apiRequest(API_ENDPOINTS.chatHistory);
            const container = document.getElementById('chatContainer');
            
            // Clear existing messages except welcome
            const welcomeMsg = container.querySelector('.welcome-message');
            container.innerHTML = '';
            if (welcomeMsg) {
                container.appendChild(welcomeMsg);
            }
            
            // Add history messages (reverse to show oldest first)
            if (history && history.length > 0) {
                history.reverse().forEach(item => {
                    Chat.addMessage(item.message, 'user', false);
                    Chat.addMessage(item.response, 'bot', false);
                });
            }
            
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    },
    
    handleMessage: async (e) => {
        e.preventDefault();
        
        if (!AppState.isAuthenticated) {
            Utils.showAlert('Please login to use the chat feature', 'warning');
            Auth.showAuthModal('login');
            return;
        }
        
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        Chat.addMessage(message, 'user');
        input.value = '';
        
        try {
            const response = await Utils.apiRequest(API_ENDPOINTS.chat, {
                method: 'POST',
                body: JSON.stringify({ user_input: message })
            });
            
            // Add bot response
            Chat.addMessage(response.response, 'bot');
            
        } catch (error) {
            Chat.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    },
    
    addMessage: (message, sender, animate = true) => {
        const container = document.getElementById('chatContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        if (animate) {
            messageDiv.style.opacity = '0';
            messageDiv.style.transform = 'translateX(-20px)';
        }
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${sender === 'bot' ? '<i class="fas fa-leaf me-2"></i>' : ''}
                ${message}
            </div>
        `;
        
        container.appendChild(messageDiv);
        
        if (animate) {
            setTimeout(() => {
                messageDiv.style.transition = 'all 0.3s ease';
                messageDiv.style.opacity = '1';
                messageDiv.style.transform = 'translateX(0)';
            }, 50);
        }
        
        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }
};

// History Module
const History = {
    loadHistory: async () => {
        if (!AppState.isAuthenticated) {
            document.getElementById('predictionsHistoryContainer').innerHTML = `
                <div class="text-center">
                    <p>Please login to view your history</p>
                    <button class="btn btn-success" onclick="Auth.showAuthModal('login')">Login</button>
                </div>
            `;
            document.getElementById('chatHistoryContainer').innerHTML = `
                <div class="text-center">
                    <p>Please login to view your history</p>
                    <button class="btn btn-success" onclick="Auth.showAuthModal('login')">Login</button>
                </div>
            `;
            return;
        }
        
        try {
            const [predictions, chatHistory] = await Promise.all([
                Utils.apiRequest(API_ENDPOINTS.predictions).catch(() => []),
                Utils.apiRequest(API_ENDPOINTS.chatHistory).catch(() => [])
            ]);
            
            History.renderPredictionsHistory(predictions);
            History.renderChatHistory(chatHistory);
            
        } catch (error) {
            console.error('Failed to load history:', error);
        }
    },
    
    renderPredictionsHistory: (predictions) => {
        const container = document.getElementById('predictionsHistoryContainer');
        
        if (!predictions || predictions.length === 0) {
            container.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-camera fa-3x text-muted mb-3"></i>
                    <p>No disease detections yet. Start by uploading a plant image!</p>
                    <button class="btn btn-success" onclick="Navigation.showSection('predict')">
                        Detect Disease
                    </button>
                </div>
            `;
            return;
        }
        
        let historyHTML = '';
        predictions.forEach(pred => {
            const diseases = pred.detected_diseases ? JSON.parse(pred.detected_diseases) : [];
            historyHTML += `
                <div class="history-item">
                    <div class="history-date">${Utils.formatDate(pred.created_at)}</div>
                    <div class="row">
                        <div class="col-md-8">
                            <h6>${pred.image_filename}</h6>
                            <p><strong>Confidence Threshold:</strong> ${pred.confidence_threshold}</p>
                            ${diseases.length > 0 ? `
                                <p><strong>Detected Diseases:</strong></p>
                                <ul class="list-unstyled">
                                    ${diseases.map(d => `<li><i class="fas fa-bug text-warning"></i> ${d}</li>`).join('')}
                                </ul>
                            ` : '<p class="text-muted">No diseases detected</p>'}
                        </div>
                        <div class="col-md-4 text-end">
                            <span class="badge bg-success">Completed</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = historyHTML;
    },
    
    renderChatHistory: (chatHistory) => {
        const container = document.getElementById('chatHistoryContainer');
        
        if (!chatHistory || chatHistory.length === 0) {
            container.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-comments fa-3x text-muted mb-3"></i>
                    <p>No chat history yet. Start a conversation with our plant care assistant!</p>
                    <button class="btn btn-success" onclick="Navigation.showSection('chat')">
                        Start Chat
                    </button>
                </div>
            `;
            return;
        }
        
        let historyHTML = '';
        chatHistory.forEach(chat => {
            historyHTML += `
                <div class="history-item">
                    <div class="history-date">${Utils.formatDate(chat.created_at)}</div>
                    <div class="mb-2">
                        <strong>You:</strong> ${chat.message}
                    </div>
                    <div>
                        <strong>Assistant:</strong> ${chat.response}
                    </div>
                    ${chat.disease_context ? `
                        <div class="mt-2">
                            <span class="badge bg-info">Context: ${chat.disease_context}</span>
                        </div>
                    ` : ''}
                </div>
            `;
        });
        
        container.innerHTML = historyHTML;
    }
};

// Global functions for HTML onclick events
window.showSection = Navigation.showSection;
window.showAuthModal = Auth.showAuthModal;
window.logout = Auth.logout;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all modules
    Auth.init();
    Prediction.init();
    Chat.init();
    
    // Set up auth form handler
    document.getElementById('authForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        
        const mode = document.getElementById('authModalTitle').textContent.toLowerCase();
        
        if (mode === 'login') {
            await Auth.login(data.username, data.password);
        } else {
            await Auth.register(data);
        }
    });
    
    // Show dashboard by default
    Navigation.showSection('dashboard');
});