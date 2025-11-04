/**
 * TrueMesh Verification Page JavaScript
 * Provider verification and compliance checking
 */

let verificationData = {
    currentProviderId: null,
    verificationResults: null,
    confidenceScore: null,
    fraudCheck: null,
    complianceCheck: null
};

// Initialize verification page
async function initVerificationPage() {
    setupEventListeners();
    
    // Check if provider ID in URL
    const urlParams = new URLSearchParams(window.location.search);
    const providerId = urlParams.get('provider_id');
    
    if (providerId) {
        verificationData.currentProviderId = providerId;
        await loadProviderForVerification(providerId);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Provider search
    const searchBtn = document.getElementById('searchProviderBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', searchProvider);
    }

    // Verification buttons
    const runFullVerificationBtn = document.getElementById('runFullVerificationBtn');
    if (runFullVerificationBtn) {
        runFullVerificationBtn.addEventListener('click', runFullVerification);
    }

    const runFraudCheckBtn = document.getElementById('runFraudCheckBtn');
    if (runFraudCheckBtn) {
        runFraudCheckBtn.addEventListener('click', runFraudCheck);
    }

    const runConfidenceScoreBtn = document.getElementById('runConfidenceScoreBtn');
    if (runConfidenceScoreBtn) {
        runConfidenceScoreBtn.addEventListener('click', runConfidenceScore);
    }

    const runComplianceCheckBtn = document.getElementById('runComplianceCheckBtn');
    if (runComplianceCheckBtn) {
        runComplianceCheckBtn.addEventListener('click', runComplianceCheck);
    }
}

// Search for provider
async function searchProvider() {
    const input = document.getElementById('providerSearchInput');
    if (!input || !input.value.trim()) {
        window.TrueMeshAuth.showToast('Please enter provider ID or registration number', 'warning');
        return;
    }

    const searchTerm = input.value.trim();
    showLoading('Searching for provider...');

    try {
        // Try as provider ID first
        const provider = await window.TrueMeshAPI.getProvider(searchTerm);
        verificationData.currentProviderId = provider.id;
        await loadProviderForVerification(provider.id);
    } catch (error) {
        // Try searching by registration number
        try {
            const response = await window.TrueMeshAPI.listProviders({
                search: searchTerm,
                limit: 1
            });
            
            if (response.providers && response.providers.length > 0) {
                const provider = response.providers[0];
                verificationData.currentProviderId = provider.id;
                await loadProviderForVerification(provider.id);
            } else {
                throw new Error('Provider not found');
            }
        } catch (innerError) {
            console.error('Provider search failed:', innerError);
            window.TrueMeshAuth.showToast('Provider not found', 'error');
            hideLoading();
        }
    }
}

// Load provider for verification
async function loadProviderForVerification(providerId) {
    showLoading('Loading provider information...');

    try {
        // Load provider details
        const provider = await window.TrueMeshAPI.getProvider(providerId);
        displayProviderInfo(provider);

        // Load existing verification status
        try {
            const status = await window.TrueMeshAPI.getVerificationStatus(providerId);
            displayVerificationStatus(status);
        } catch (e) {
            console.log('No verification status available');
        }

        // Load existing scores
        try {
            const scores = await window.TrueMeshAPI.getProviderScores(providerId);
            displayExistingScores(scores);
        } catch (e) {
            console.log('No existing scores');
        }

        hideLoading();
    } catch (error) {
        console.error('Failed to load provider:', error);
        window.TrueMeshAuth.showToast('Failed to load provider information', 'error');
        hideLoading();
    }
}

// Display provider information
function displayProviderInfo(provider) {
    const container = document.getElementById('providerInfo');
    if (!container) return;

    container.innerHTML = `
        <div class="provider-card">
            <div class="provider-header">
                <h3>${escapeHtml(provider.name)}</h3>
                <span class="status-badge status-${provider.status}">
                    ${escapeHtml(provider.status)}
                </span>
            </div>
            <div class="provider-details-grid">
                <div class="detail-item">
                    <label>Registration Number:</label>
                    <value>${escapeHtml(provider.registration_number)}</value>
                </div>
                <div class="detail-item">
                    <label>Type:</label>
                    <value>${escapeHtml(provider.provider_type)}</value>
                </div>
                <div class="detail-item">
                    <label>Specialization:</label>
                    <value>${escapeHtml(provider.specialization || 'N/A')}</value>
                </div>
                <div class="detail-item">
                    <label>Location:</label>
                    <value>${escapeHtml(provider.city || 'N/A')}, ${escapeHtml(provider.state || 'N/A')}</value>
                </div>
                <div class="detail-item">
                    <label>Email:</label>
                    <value>${escapeHtml(provider.email || 'N/A')}</value>
                </div>
                <div class="detail-item">
                    <label>Phone:</label>
                    <value>${escapeHtml(provider.phone || 'N/A')}</value>
                </div>
            </div>
        </div>
    `;

    // Enable verification buttons
    document.querySelectorAll('.verification-btn').forEach(btn => {
        btn.disabled = false;
    });
}

// Display verification status
function displayVerificationStatus(status) {
    const container = document.getElementById('verificationStatus');
    if (!container) return;

    container.innerHTML = `
        <div class="status-card">
            <h4><i class="fas fa-info-circle"></i> Current Verification Status</h4>
            <div class="status-details">
                <p><strong>Status:</strong> ${escapeHtml(status.verification_status)}</p>
                <p><strong>Last Verified:</strong> ${formatDate(status.last_verified)}</p>
                <p><strong>Next Verification:</strong> ${formatDate(status.next_verification_due)}</p>
                <p><strong>Sources:</strong> ${status.verification_sources.join(', ')}</p>
            </div>
        </div>
    `;
}

// Display existing scores
function displayExistingScores(scores) {
    const container = document.getElementById('existingScores');
    if (!container) return;

    const confidencePercent = (scores.confidence_scores.overall_score * 100).toFixed(1);
    const fraudPercent = (scores.fraud_score * 100).toFixed(1);

    container.innerHTML = `
        <div class="scores-grid">
            <div class="score-card">
                <div class="score-header">
                    <i class="fas fa-shield-alt"></i>
                    <h4>Confidence Score</h4>
                </div>
                <div class="score-value ${getScoreClass(scores.confidence_scores.overall_score)}">
                    ${confidencePercent}%
                </div>
                <div class="score-breakdown">
                    <small>Verification: ${(scores.confidence_scores.verification_score * 100).toFixed(1)}%</small>
                    <small>Consistency: ${(scores.confidence_scores.consistency_score * 100).toFixed(1)}%</small>
                    <small>Historical: ${(scores.confidence_scores.historical_score * 100).toFixed(1)}%</small>
                </div>
            </div>
            <div class="score-card">
                <div class="score-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h4>Fraud Risk</h4>
                </div>
                <div class="score-value ${getFraudClass(scores.fraud_score)}">
                    ${fraudPercent}%
                </div>
                <div class="score-breakdown">
                    <small>Risk Level: ${scores.risk_level.toUpperCase()}</small>
                </div>
            </div>
        </div>
    `;
}

// Run full verification
async function runFullVerification() {
    if (!verificationData.currentProviderId) {
        window.TrueMeshAuth.showToast('Please search for a provider first', 'warning');
        return;
    }

    showLoading('Running full verification...');

    try {
        const result = await window.TrueMeshAPI.verifyProviderData(
            verificationData.currentProviderId,
            'full'
        );

        verificationData.verificationResults = result;
        displayVerificationResults(result);
        
        window.TrueMeshAuth.showToast('Verification completed successfully', 'success');

        // Run related checks
        await Promise.all([
            runConfidenceScore(true),
            runFraudCheck(true),
            runComplianceCheck(true)
        ]);

    } catch (error) {
        console.error('Verification failed:', error);
        window.TrueMeshAuth.showToast('Verification failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display verification results
function displayVerificationResults(result) {
    const container = document.getElementById('verificationResults');
    if (!container) return;

    const sources = Object.entries(result.verification_results || {});

    container.innerHTML = `
        <div class="results-card">
            <h4><i class="fas fa-check-circle"></i> Verification Results</h4>
            <div class="result-summary">
                <p><strong>Status:</strong> 
                    <span class="badge badge-${result.is_verified ? 'success' : 'danger'}">
                        ${result.is_verified ? 'VERIFIED' : 'NOT VERIFIED'}
                    </span>
                </p>
                <p><strong>Confidence:</strong> ${(result.confidence_score * 100).toFixed(1)}%</p>
                <p><strong>Timestamp:</strong> ${formatDate(result.timestamp)}</p>
            </div>
            
            ${sources.length > 0 ? `
                <div class="source-results">
                    <h5>Source Verification:</h5>
                    ${sources.map(([source, data]) => `
                        <div class="source-item">
                            <i class="fas ${data.verified ? 'fa-check-circle text-success' : 'fa-times-circle text-danger'}"></i>
                            <span><strong>${source}:</strong> ${data.message || (data.verified ? 'Verified' : 'Failed')}</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

// Run fraud check
async function runFraudCheck(silent = false) {
    if (!verificationData.currentProviderId) {
        if (!silent) window.TrueMeshAuth.showToast('Please search for a provider first', 'warning');
        return;
    }

    if (!silent) showLoading('Running fraud detection...');

    try {
        const result = await window.TrueMeshAPI.runFraudCheck(verificationData.currentProviderId);
        verificationData.fraudCheck = result;
        displayFraudCheckResults(result);
        
        if (!silent) window.TrueMeshAuth.showToast('Fraud check completed', 'success');

    } catch (error) {
        console.error('Fraud check failed:', error);
        if (!silent) window.TrueMeshAuth.showToast('Fraud check failed', 'error');
    } finally {
        if (!silent) hideLoading();
    }
}

// Display fraud check results
function displayFraudCheckResults(result) {
    const container = document.getElementById('fraudCheckResults');
    if (!container) return;

    const fraudPercent = (result.fraud_score * 100).toFixed(1);

    container.innerHTML = `
        <div class="results-card fraud-results">
            <h4><i class="fas fa-exclamation-triangle"></i> Fraud Detection Results</h4>
            <div class="fraud-summary">
                <div class="fraud-score ${getFraudClass(result.fraud_score)}">
                    <span class="score-label">Fraud Risk Score</span>
                    <span class="score-value">${fraudPercent}%</span>
                    <span class="risk-level badge badge-${getRiskBadgeClass(result.risk_level)}">
                        ${result.risk_level.toUpperCase()}
                    </span>
                </div>
                <div class="fraud-status">
                    <p><strong>Fraudulent:</strong> 
                        <span class="badge badge-${result.is_fraudulent ? 'danger' : 'success'}">
                            ${result.is_fraudulent ? 'YES' : 'NO'}
                        </span>
                    </p>
                    <p><strong>Checked At:</strong> ${formatDate(result.checked_at)}</p>
                </div>
            </div>
            
            ${result.fraud_checks ? `
                <div class="fraud-checks">
                    <h5>Detection Checks:</h5>
                    ${Object.entries(result.fraud_checks).map(([check, passed]) => `
                        <div class="check-item">
                            <i class="fas ${passed ? 'fa-check-circle text-success' : 'fa-exclamation-circle text-warning'}"></i>
                            <span>${formatCheckName(check)}</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

// Run confidence score
async function runConfidenceScore(silent = false) {
    if (!verificationData.currentProviderId) {
        if (!silent) window.TrueMeshAuth.showToast('Please search for a provider first', 'warning');
        return;
    }

    if (!silent) showLoading('Calculating confidence score...');

    try {
        const result = await window.TrueMeshAPI.calculateConfidenceScore(verificationData.currentProviderId);
        verificationData.confidenceScore = result;
        displayConfidenceScoreResults(result);
        
        if (!silent) window.TrueMeshAuth.showToast('Confidence score calculated', 'success');

    } catch (error) {
        console.error('Confidence score calculation failed:', error);
        if (!silent) window.TrueMeshAuth.showToast('Confidence score calculation failed', 'error');
    } finally {
        if (!silent) hideLoading();
    }
}

// Display confidence score results
function displayConfidenceScoreResults(result) {
    const container = document.getElementById('confidenceScoreResults');
    if (!container) return;

    const scores = result.confidence_scores;
    const overallPercent = (scores.overall_score * 100).toFixed(1);

    container.innerHTML = `
        <div class="results-card confidence-results">
            <h4><i class="fas fa-shield-alt"></i> Confidence Score Results</h4>
            <div class="confidence-summary">
                <div class="overall-score ${getScoreClass(scores.overall_score)}">
                    <span class="score-label">Overall Confidence</span>
                    <span class="score-value">${overallPercent}%</span>
                </div>
            </div>
            
            <div class="score-breakdown-detailed">
                <h5>Score Breakdown:</h5>
                <div class="breakdown-grid">
                    <div class="breakdown-item">
                        <label>Verification Score</label>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${scores.verification_score * 100}%"></div>
                        </div>
                        <span>${(scores.verification_score * 100).toFixed(1)}%</span>
                    </div>
                    <div class="breakdown-item">
                        <label>Consistency Score</label>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${scores.consistency_score * 100}%"></div>
                        </div>
                        <span>${(scores.consistency_score * 100).toFixed(1)}%</span>
                    </div>
                    <div class="breakdown-item">
                        <label>Historical Score</label>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${scores.historical_score * 100}%"></div>
                        </div>
                        <span>${(scores.historical_score * 100).toFixed(1)}%</span>
                    </div>
                    <div class="breakdown-item">
                        <label>External Score</label>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${scores.external_score * 100}%"></div>
                        </div>
                        <span>${(scores.external_score * 100).toFixed(1)}%</span>
                    </div>
                </div>
            </div>
            
            <p class="calculation-time"><small>Calculated at: ${formatDate(result.calculated_at)}</small></p>
        </div>
    `;
}

// Run compliance check
async function runComplianceCheck(silent = false) {
    if (!verificationData.currentProviderId) {
        if (!silent) window.TrueMeshAuth.showToast('Please search for a provider first', 'warning');
        return;
    }

    if (!silent) showLoading('Running compliance check...');

    try {
        const result = await window.TrueMeshAPI.checkCompliance(verificationData.currentProviderId);
        verificationData.complianceCheck = result;
        displayComplianceCheckResults(result);
        
        if (!silent) window.TrueMeshAuth.showToast('Compliance check completed', 'success');

    } catch (error) {
        console.error('Compliance check failed:', error);
        if (!silent) window.TrueMeshAuth.showToast('Compliance check failed', 'error');
    } finally {
        if (!silent) hideLoading();
    }
}

// Display compliance check results
function displayComplianceCheckResults(result) {
    const container = document.getElementById('complianceCheckResults');
    if (!container) return;

    container.innerHTML = `
        <div class="results-card compliance-results">
            <h4><i class="fas fa-clipboard-check"></i> Compliance Check Results</h4>
            <div class="compliance-summary">
                <p><strong>Status:</strong> 
                    <span class="badge badge-${result.is_compliant ? 'success' : 'danger'}">
                        ${result.compliance_status.toUpperCase()}
                    </span>
                </p>
                <p><strong>Checked At:</strong> ${formatDate(result.checked_at)}</p>
                <p><strong>Auto-Resolved:</strong> ${result.auto_resolved} issue(s)</p>
            </div>
            
            ${result.violations && result.violations.length > 0 ? `
                <div class="violations-list">
                    <h5><i class="fas fa-exclamation-circle"></i> Violations Found:</h5>
                    ${result.violations.map(violation => `
                        <div class="violation-item">
                            <p><strong>${violation.policy}</strong></p>
                            <p>${violation.description}</p>
                        </div>
                    `).join('')}
                </div>
            ` : '<p class="text-success"><i class="fas fa-check-circle"></i> No violations found</p>'}
        </div>
    `;
}

// Utility functions
function getScoreClass(score) {
    if (score >= 0.8) return 'score-excellent';
    if (score >= 0.6) return 'score-good';
    if (score >= 0.4) return 'score-fair';
    return 'score-poor';
}

function getFraudClass(score) {
    if (score >= 0.8) return 'fraud-critical';
    if (score >= 0.6) return 'fraud-high';
    if (score >= 0.4) return 'fraud-medium';
    return 'fraud-low';
}

function getRiskBadgeClass(level) {
    const classes = {
        'low': 'success',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'danger'
    };
    return classes[level] || 'secondary';
}

function formatCheckName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
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

function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.querySelector('.loading-text')?.textContent = message;
        overlay.classList.add('active');
    }
}

function hideLoading() {
    document.getElementById('loadingOverlay')?.classList.remove('active');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('verification.html')) {
        initVerificationPage();
    }
});

// Export functions
window.TrueMeshVerification = {
    initVerificationPage,
    searchProvider,
    runFullVerification,
    runFraudCheck,
    runConfidenceScore,
    runComplianceCheck
};
