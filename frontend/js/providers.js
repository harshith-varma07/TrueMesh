/**
 * TrueMesh Providers Page JavaScript
 * Provider management and search functionality
 */

let providersData = {
    providers: [],
    currentPage: 1,
    pageSize: 20,
    total: 0,
    filters: {
        status: '',
        provider_type: '',
        city: '',
        state: '',
        search: ''
    }
};

// Initialize providers page
async function initProvidersPage() {
    setupEventListeners();
    await loadProviders();
}

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    const searchInput = document.getElementById('providerSearch');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                providersData.filters.search = e.target.value;
                providersData.currentPage = 1;
                loadProviders();
            }, 500);
        });
    }

    // Filter dropdowns
    ['status', 'provider_type', 'city', 'state'].forEach(filterId => {
        const filter = document.getElementById(`filter_${filterId}`);
        if (filter) {
            filter.addEventListener('change', (e) => {
                providersData.filters[filterId] = e.target.value;
                providersData.currentPage = 1;
                loadProviders();
            });
        }
    });

    // Create provider button
    const createBtn = document.getElementById('createProviderBtn');
    if (createBtn) {
        createBtn.addEventListener('click', showCreateProviderModal);
    }
}

// Load providers from API
async function loadProviders() {
    showLoading();
    
    try {
        const params = {
            skip: (providersData.currentPage - 1) * providersData.pageSize,
            limit: providersData.pageSize,
            ...providersData.filters
        };

        // Remove empty filters
        Object.keys(params).forEach(key => {
            if (params[key] === '') delete params[key];
        });

        const response = await window.TrueMeshAPI.listProviders(params);
        
        providersData.providers = response.providers || [];
        providersData.total = response.total || 0;
        
        renderProvidersTable();
        renderPagination();
        
        hideLoading();
    } catch (error) {
        console.error('Failed to load providers:', error);
        hideLoading();
        showError('Failed to load providers. Showing demo data.');
        loadDemoProviders();
    }
}

// Render providers table
function renderProvidersTable() {
    const tbody = document.getElementById('providersTableBody');
    if (!tbody) return;

    if (providersData.providers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center">
                    <p class="empty-state">No providers found</p>
                </td>
            </tr>
        `;
        return;
    }

    const html = providersData.providers.map(provider => `
        <tr data-provider-id="${provider.id}">
            <td>
                <div class="provider-name">
                    <strong>${escapeHtml(provider.name)}</strong>
                    <small>${escapeHtml(provider.registration_number)}</small>
                </div>
            </td>
            <td>
                <span class="badge badge-${getTypeColor(provider.provider_type)}">
                    ${escapeHtml(provider.provider_type)}
                </span>
            </td>
            <td>${escapeHtml(provider.specialization || 'N/A')}</td>
            <td>${escapeHtml(provider.city || 'N/A')}, ${escapeHtml(provider.state || 'N/A')}</td>
            <td>
                <span class="status-badge status-${provider.status}">
                    ${escapeHtml(provider.status)}
                </span>
            </td>
            <td>${formatDate(provider.created_at)}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-icon" onclick="viewProviderDetails('${provider.id}')" title="View">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-icon" onclick="editProvider('${provider.id}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-icon" onclick="verifyProviderAction('${provider.id}')" title="Verify">
                        <i class="fas fa-check-circle"></i>
                    </button>
                    <button class="btn btn-sm btn-icon btn-danger" onclick="deleteProvider('${provider.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');

    tbody.innerHTML = html;
}

// Render pagination
function renderPagination() {
    const pagination = document.getElementById('pagination');
    if (!pagination) return;

    const totalPages = Math.ceil(providersData.total / providersData.pageSize);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let html = '';
    
    // Previous button
    html += `
        <button class="btn btn-sm ${providersData.currentPage === 1 ? 'disabled' : ''}" 
                onclick="changePage(${providersData.currentPage - 1})"
                ${providersData.currentPage === 1 ? 'disabled' : ''}>
            <i class="fas fa-chevron-left"></i> Previous
        </button>
    `;

    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= providersData.currentPage - 2 && i <= providersData.currentPage + 2)) {
            html += `
                <button class="btn btn-sm ${i === providersData.currentPage ? 'btn-primary' : ''}" 
                        onclick="changePage(${i})">
                    ${i}
                </button>
            `;
        } else if (i === providersData.currentPage - 3 || i === providersData.currentPage + 3) {
            html += '<span class="pagination-ellipsis">...</span>';
        }
    }

    // Next button
    html += `
        <button class="btn btn-sm ${providersData.currentPage === totalPages ? 'disabled' : ''}" 
                onclick="changePage(${providersData.currentPage + 1})"
                ${providersData.currentPage === totalPages ? 'disabled' : ''}>
            Next <i class="fas fa-chevron-right"></i>
        </button>
    `;

    pagination.innerHTML = html;
}

// Change page
function changePage(page) {
    if (page < 1 || page > Math.ceil(providersData.total / providersData.pageSize)) return;
    providersData.currentPage = page;
    loadProviders();
}

// Show create provider modal
function showCreateProviderModal() {
    const modal = document.getElementById('providerModal');
    if (!modal) {
        // Redirect to create page or show inline form
        window.TrueMeshAuth.showToast('Opening create provider form...', 'info');
        return;
    }
    modal.classList.add('active');
}

// Create provider
async function createProvider(formData) {
    try {
        showLoading();
        const result = await window.TrueMeshAPI.createProvider(formData);
        
        window.TrueMeshAuth.showToast(
            `Provider created successfully! Workflow ID: ${result.workflow_id}`,
            'success'
        );
        
        // Refresh list
        await loadProviders();
        
        // Close modal
        closeModal('providerModal');
        
    } catch (error) {
        console.error('Failed to create provider:', error);
        window.TrueMeshAuth.showToast(
            error.message || 'Failed to create provider',
            'error'
        );
    } finally {
        hideLoading();
    }
}

// View provider details
async function viewProviderDetails(providerId) {
    try {
        showLoading();
        
        const [provider, scores, history] = await Promise.all([
            window.TrueMeshAPI.getProvider(providerId),
            window.TrueMeshAPI.getProviderScores(providerId).catch(() => null),
            window.TrueMeshAPI.getProviderHistory(providerId).catch(() => null)
        ]);
        
        showProviderDetailsModal(provider, scores, history);
        
    } catch (error) {
        console.error('Failed to load provider details:', error);
        window.TrueMeshAuth.showToast('Failed to load provider details', 'error');
    } finally {
        hideLoading();
    }
}

// Show provider details modal
function showProviderDetailsModal(provider, scores, history) {
    // Create modal HTML
    const modalHTML = `
        <div class="modal-overlay" id="detailsModal" onclick="closeModal('detailsModal')">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h2>${escapeHtml(provider.name)}</h2>
                    <button class="btn-close" onclick="closeModal('detailsModal')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="detail-section">
                            <h3>Provider Information</h3>
                            <p><strong>Registration:</strong> ${escapeHtml(provider.registration_number)}</p>
                            <p><strong>Type:</strong> ${escapeHtml(provider.provider_type)}</p>
                            <p><strong>Specialization:</strong> ${escapeHtml(provider.specialization || 'N/A')}</p>
                            <p><strong>Status:</strong> <span class="status-badge status-${provider.status}">${provider.status}</span></p>
                        </div>
                        
                        ${scores ? `
                        <div class="detail-section">
                            <h3>Scores</h3>
                            <p><strong>Confidence:</strong> ${(scores.confidence_scores.overall_score * 100).toFixed(1)}%</p>
                            <p><strong>Fraud Risk:</strong> ${(scores.fraud_score * 100).toFixed(1)}%</p>
                            <p><strong>Risk Level:</strong> <span class="badge badge-${scores.risk_level}">${scores.risk_level}</span></p>
                        </div>
                        ` : ''}
                        
                        ${history ? `
                        <div class="detail-section">
                            <h3>Provenance History</h3>
                            <p><strong>Records:</strong> ${history.history_count}</p>
                            <p><strong>Last Update:</strong> ${formatDate(history.history[0]?.timestamp)}</p>
                        </div>
                        ` : ''}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeModal('detailsModal')">Close</button>
                    <button class="btn btn-primary" onclick="verifyProviderAction('${provider.id}'); closeModal('detailsModal')">
                        <i class="fas fa-check-circle"></i> Verify
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    const existingModal = document.getElementById('detailsModal');
    if (existingModal) existingModal.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// Edit provider
async function editProvider(providerId) {
    try {
        const provider = await window.TrueMeshAPI.getProvider(providerId);
        showEditProviderModal(provider);
    } catch (error) {
        console.error('Failed to load provider for editing:', error);
        window.TrueMeshAuth.showToast('Failed to load provider', 'error');
    }
}

// Verify provider action
async function verifyProviderAction(providerId) {
    if (!confirm('Start verification workflow for this provider?')) return;
    
    try {
        showLoading();
        const result = await window.TrueMeshAPI.verifyProvider(providerId);
        
        window.TrueMeshAuth.showToast(
            `Verification started: ${result.workflow_id}`,
            'success'
        );
        
        // Refresh list after 2 seconds
        setTimeout(loadProviders, 2000);
        
    } catch (error) {
        console.error('Verification failed:', error);
        window.TrueMeshAuth.showToast('Failed to start verification', 'error');
    } finally {
        hideLoading();
    }
}

// Delete provider
async function deleteProvider(providerId) {
    if (!confirm('Are you sure you want to delete this provider? This action cannot be undone.')) return;
    
    try {
        showLoading();
        await window.TrueMeshAPI.deleteProvider(providerId);
        
        window.TrueMeshAuth.showToast('Provider deleted successfully', 'success');
        await loadProviders();
        
    } catch (error) {
        console.error('Failed to delete provider:', error);
        window.TrueMeshAuth.showToast('Failed to delete provider', 'error');
    } finally {
        hideLoading();
    }
}

// Utility functions
function getTypeColor(type) {
    const colors = {
        'doctor': 'primary',
        'hospital': 'success',
        'clinic': 'info',
        'pharmacy': 'warning'
    };
    return colors[type] || 'secondary';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.remove();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        return new Date(dateString).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return 'N/A';
    }
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

// Demo data
function loadDemoProviders() {
    providersData.providers = [
        {
            id: 'demo-1',
            name: 'Dr. Amit Sharma',
            registration_number: 'MCI123456',
            provider_type: 'doctor',
            specialization: 'Cardiology',
            city: 'Mumbai',
            state: 'Maharashtra',
            status: 'verified',
            created_at: new Date().toISOString()
        },
        {
            id: 'demo-2',
            name: 'Apollo Hospital',
            registration_number: 'HOSP789012',
            provider_type: 'hospital',
            specialization: 'Multi-Specialty',
            city: 'Delhi',
            state: 'Delhi',
            status: 'pending',
            created_at: new Date().toISOString()
        }
    ];
    providersData.total = 2;
    renderProvidersTable();
    renderPagination();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('providers.html')) {
        initProvidersPage();
    }
});

// Export functions
window.TrueMeshProviders = {
    initProvidersPage,
    createProvider,
    viewProviderDetails,
    editProvider,
    verifyProviderAction,
    deleteProvider
};
