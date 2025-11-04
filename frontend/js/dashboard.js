/**
 * TrueMesh Dashboard JavaScript
 * Connects dashboard UI with backend API
 */

let dashboardData = {
    providers: [],
    stats: {},
    recentActivity: []
};

// Initialize dashboard
async function initDashboard() {
    showLoading();
    
    try {
        // Load all dashboard data in parallel
        await Promise.all([
            loadSystemStats(),
            loadRecentProviders(),
            loadAgentStatus(),
            loadBlockchainInfo()
        ]);
        
        hideLoading();
        startAutoRefresh();
    } catch (error) {
        console.error('Dashboard initialization failed:', error);
        hideLoading();
        showError('Failed to load dashboard data. Please refresh the page.');
    }
}

// Load system statistics
async function loadSystemStats() {
    try {
        const overview = await window.TrueMeshAPI.getSystemOverview();
        
        // Update stat cards
        updateStatCard('total-providers', overview.providers?.total || 0);
        updateStatCard('verified-providers', overview.providers?.verified || 0);
        updateStatCard('pending-verifications', overview.providers?.pending || 0);
        updateStatCard('active-agents', overview.agents?.active_count || 0);
        
        // Update trend indicators
        updateTrend('providers-trend', overview.providers?.trend || 0);
        updateTrend('verifications-trend', overview.verifications?.trend || 0);
        
        dashboardData.stats = overview;
    } catch (error) {
        console.error('Failed to load system stats:', error);
        // Use demo data
        loadDemoStats();
    }
}

// Load recent providers
async function loadRecentProviders() {
    try {
        const response = await window.TrueMeshAPI.listProviders({ 
            limit: 10, 
            skip: 0 
        });
        
        dashboardData.providers = response.providers || [];
        updateProvidersList(dashboardData.providers);
    } catch (error) {
        console.error('Failed to load providers:', error);
        loadDemoProviders();
    }
}

// Load agent status
async function loadAgentStatus() {
    try {
        const status = await window.TrueMeshAPI.getAgentsStatus();
        updateAgentStatusDisplay(status);
    } catch (error) {
        console.error('Failed to load agent status:', error);
    }
}

// Load blockchain info
async function loadBlockchainInfo() {
    try {
        const info = await window.TrueMeshAPI.getBlockchainInfo();
        updateBlockchainDisplay(info);
    } catch (error) {
        console.error('Failed to load blockchain info:', error);
    }
}

// Update stat card
function updateStatCard(cardId, value) {
    const card = document.querySelector(`[data-stat="${cardId}"]`);
    if (card) {
        const valueElement = card.querySelector('.stat-value');
        if (valueElement) {
            animateNumber(valueElement, value);
        }
    }
}

// Animate number counter
function animateNumber(element, targetValue) {
    const currentValue = parseInt(element.textContent) || 0;
    const increment = (targetValue - currentValue) / 20;
    let current = currentValue;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= targetValue) || 
            (increment < 0 && current <= targetValue)) {
            element.textContent = targetValue.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current).toLocaleString();
        }
    }, 50);
}

// Update trend indicator
function updateTrend(trendId, percentage) {
    const trend = document.querySelector(`[data-trend="${trendId}"]`);
    if (trend) {
        const icon = percentage >= 0 ? '↑' : '↓';
        const className = percentage >= 0 ? 'trend-up' : 'trend-down';
        trend.textContent = `${icon} ${Math.abs(percentage)}%`;
        trend.className = `trend ${className}`;
    }
}

// Update providers list
function updateProvidersList(providers) {
    const container = document.getElementById('recentProviders');
    if (!container) return;
    
    if (providers.length === 0) {
        container.innerHTML = '<p class="empty-state">No providers found</p>';
        return;
    }
    
    const html = providers.map(provider => `
        <div class="provider-card" data-provider-id="${provider.id}">
            <div class="provider-header">
                <div class="provider-info">
                    <h4>${escapeHtml(provider.name)}</h4>
                    <p class="provider-type">${escapeHtml(provider.provider_type)}</p>
                </div>
                <span class="status-badge status-${provider.status}">
                    ${provider.status}
                </span>
            </div>
            <div class="provider-details">
                <div class="detail-item">
                    <i class="fas fa-id-card"></i>
                    <span>${escapeHtml(provider.registration_number)}</span>
                </div>
                <div class="detail-item">
                    <i class="fas fa-calendar"></i>
                    <span>${formatDate(provider.created_at)}</span>
                </div>
            </div>
            <div class="provider-actions">
                <button class="btn btn-sm btn-secondary" onclick="viewProvider('${provider.id}')">
                    <i class="fas fa-eye"></i> View
                </button>
                <button class="btn btn-sm btn-primary" onclick="verifyProvider('${provider.id}')">
                    <i class="fas fa-check-circle"></i> Verify
                </button>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// Update agent status display
function updateAgentStatusDisplay(status) {
    const container = document.getElementById('agentStatus');
    if (!container) return;
    
    const agents = status.agents || {};
    const html = Object.entries(agents).map(([type, info]) => `
        <div class="agent-item">
            <div class="agent-icon ${info.status}">
                <i class="fas fa-robot"></i>
            </div>
            <div class="agent-details">
                <h5>${formatAgentName(type)}</h5>
                <p class="agent-status">${info.status}</p>
                <p class="agent-tasks">Tasks: ${info.tasks_completed || 0}</p>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html || '<p class="empty-state">No agent data available</p>';
}

// Update blockchain display
function updateBlockchainDisplay(info) {
    const container = document.getElementById('blockchainInfo');
    if (!container) return;
    
    container.innerHTML = `
        <div class="blockchain-stat">
            <i class="fas fa-cube"></i>
            <div>
                <h5>Chain Length</h5>
                <p>${info.chain_length || 0}</p>
            </div>
        </div>
        <div class="blockchain-stat">
            <i class="fas fa-exchange-alt"></i>
            <div>
                <h5>Transactions</h5>
                <p>${info.total_transactions || 0}</p>
            </div>
        </div>
        <div class="blockchain-stat">
            <i class="fas fa-check-circle"></i>
            <div>
                <h5>Status</h5>
                <p>${info.is_valid ? 'Valid' : 'Invalid'}</p>
            </div>
        </div>
    `;
}

// View provider details
async function viewProvider(providerId) {
    try {
        const provider = await window.TrueMeshAPI.getProvider(providerId);
        showProviderModal(provider);
    } catch (error) {
        console.error('Failed to load provider:', error);
        window.TrueMeshAuth.showToast('Failed to load provider details', 'error');
    }
}

// Verify provider
async function verifyProvider(providerId) {
    if (!confirm('Start verification workflow for this provider?')) return;
    
    try {
        window.TrueMeshAuth.showToast('Starting verification...', 'info');
        const result = await window.TrueMeshAPI.verifyProvider(providerId);
        window.TrueMeshAuth.showToast(
            `Verification started: ${result.workflow_id}`, 
            'success'
        );
        
        // Refresh dashboard after 2 seconds
        setTimeout(loadRecentProviders, 2000);
    } catch (error) {
        console.error('Verification failed:', error);
        window.TrueMeshAuth.showToast('Failed to start verification', 'error');
    }
}

// Show provider modal
function showProviderModal(provider) {
    // Implementation for provider details modal
    console.log('Show provider modal:', provider);
    window.TrueMeshAuth.showToast('Provider details modal coming soon', 'info');
}

// Auto refresh dashboard
function startAutoRefresh() {
    // Refresh every 30 seconds
    setInterval(() => {
        loadSystemStats();
        loadRecentProviders();
    }, 30000);
}

// Demo data fallbacks
function loadDemoStats() {
    updateStatCard('total-providers', 248);
    updateStatCard('verified-providers', 195);
    updateStatCard('pending-verifications', 28);
    updateStatCard('active-agents', 9);
}

function loadDemoProviders() {
    const demoProviders = [
        {
            id: 'demo-1',
            name: 'Dr. Sample Provider',
            provider_type: 'doctor',
            registration_number: 'MCI123456',
            status: 'verified',
            created_at: new Date().toISOString()
        }
    ];
    updateProvidersList(demoProviders);
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    try {
        return new Date(dateString).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch {
        return 'N/A';
    }
}

function formatAgentName(type) {
    return type.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function showLoading() {
    document.getElementById('loadingOverlay')?.classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay')?.classList.remove('active');
}

function showError(message) {
    window.TrueMeshAuth?.showToast(message, 'error');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('dashboard.html')) {
        initDashboard();
    }
});

// Export functions
window.TrueMeshDashboard = {
    initDashboard,
    loadSystemStats,
    viewProvider,
    verifyProvider
};
