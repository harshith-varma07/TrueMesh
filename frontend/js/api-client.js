/**
 * TrueMesh API Client
 * Centralized API communication layer
 */

const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api/v1',
    TIMEOUT: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000 // 1 second
};

class TrueMeshAPIClient {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
    }

    /**
     * Get authentication headers
     */
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        if (includeAuth && window.TrueMeshAuth) {
            const token = window.TrueMeshAuth.getAuthToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        return headers;
    }

    /**
     * Make API request with retry logic
     */
    async request(endpoint, options = {}, retryCount = 0) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = this.getHeaders(options.includeAuth !== false);

        const config = {
            method: options.method || 'GET',
            headers: { ...headers, ...options.headers },
            ...(options.body && { body: JSON.stringify(options.body) })
        };

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(url, {
                ...config,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            // Handle 401 Unauthorized
            if (response.status === 401 && window.TrueMeshAuth) {
                window.TrueMeshAuth.logout();
                throw new Error('Authentication required');
            }

            // Parse response
            const data = await response.json().catch(() => null);

            if (!response.ok) {
                throw {
                    status: response.status,
                    message: data?.detail || data?.message || 'Request failed',
                    data
                };
            }

            return data;

        } catch (error) {
            // Retry on network errors
            if (retryCount < API_CONFIG.RETRY_ATTEMPTS && 
                (error.name === 'TypeError' || error.name === 'AbortError')) {
                await new Promise(resolve => 
                    setTimeout(resolve, API_CONFIG.RETRY_DELAY * (retryCount + 1))
                );
                return this.request(endpoint, options, retryCount + 1);
            }

            throw error;
        }
    }

    // Provider API methods
    async createProvider(providerData) {
        return this.request('/providers/', {
            method: 'POST',
            body: providerData
        });
    }

    async getProvider(providerId) {
        return this.request(`/providers/${providerId}`);
    }

    async updateProvider(providerId, updates) {
        return this.request(`/providers/${providerId}`, {
            method: 'PUT',
            body: updates
        });
    }

    async deleteProvider(providerId) {
        return this.request(`/providers/${providerId}`, {
            method: 'DELETE'
        });
    }

    async listProviders(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/providers/?${queryString}`);
    }

    async getProviderHistory(providerId) {
        return this.request(`/providers/${providerId}/history`);
    }

    async verifyProvider(providerId) {
        return this.request(`/providers/${providerId}/verify`, {
            method: 'POST'
        });
    }

    async getProviderScores(providerId) {
        return this.request(`/providers/${providerId}/scores`);
    }

    // Verification API methods
    async verifyProviderData(providerId, verificationType = 'full') {
        return this.request('/verification/', {
            method: 'POST',
            body: { provider_id: providerId, verification_type: verificationType }
        });
    }

    async getVerificationStatus(providerId) {
        return this.request(`/verification/${providerId}/status`);
    }

    async runFraudCheck(providerId) {
        return this.request(`/verification/${providerId}/fraud-check`, {
            method: 'POST'
        });
    }

    async calculateConfidenceScore(providerId) {
        return this.request(`/verification/${providerId}/confidence-score`, {
            method: 'POST'
        });
    }

    async checkCompliance(providerId) {
        return this.request(`/verification/${providerId}/compliance-check`, {
            method: 'POST'
        });
    }

    // PITL API methods
    async submitProviderUpdate(providerId, updates) {
        return this.request('/pitl/update', {
            method: 'POST',
            body: { provider_id: providerId, updates }
        });
    }

    async submitChallenge(providerId, challengeData, reason) {
        return this.request('/pitl/challenge', {
            method: 'POST',
            body: {
                provider_id: providerId,
                challenge_data: challengeData,
                challenge_reason: reason
            }
        });
    }

    async getChallengeStatus(challengeId) {
        return this.request(`/pitl/challenges/${challengeId}`);
    }

    async listPendingChallenges() {
        return this.request('/pitl/challenges');
    }

    async resolveChallenge(challengeId, resolution = 'approve') {
        return this.request(`/pitl/challenges/${challengeId}/resolve`, {
            method: 'POST',
            body: { resolution }
        });
    }

    // Federation API methods
    async syncToFederation(providerData, operation = 'update') {
        return this.request('/federation/sync', {
            method: 'POST',
            body: { provider_data: providerData, operation }
        });
    }

    async getFederationStatus() {
        return this.request('/federation/status');
    }

    async checkFederationHealth() {
        return this.request('/federation/health-check', {
            method: 'POST'
        });
    }

    async getFederationUpdates(since = null) {
        const params = since ? `?since=${since}` : '';
        return this.request(`/federation/updates${params}`);
    }

    // Admin API methods
    async getAgentsStatus() {
        return this.request('/admin/agents/status');
    }

    async getOrchestratorStatus() {
        return this.request('/admin/orchestrator/status');
    }

    async getBlockchainInfo() {
        return this.request('/admin/provenance/chain-info');
    }

    async verifyProvenanceRecord(blockHash, dataHash) {
        return this.request('/admin/provenance/verify', {
            method: 'POST',
            body: { block_hash: blockHash, data_hash: dataHash }
        });
    }

    async grantComplianceException(providerId, policyType, reason, durationDays = 30) {
        return this.request('/admin/compliance/exception', {
            method: 'POST',
            body: {
                provider_id: providerId,
                policy_type: policyType,
                reason,
                duration_days: durationDays
            }
        });
    }

    async listComplianceExceptions(providerId = null) {
        const params = providerId ? `?provider_id=${providerId}` : '';
        return this.request(`/admin/compliance/exceptions${params}`);
    }

    async getSystemOverview() {
        return this.request('/admin/stats/overview');
    }

    async adminHealthCheck() {
        return this.request('/admin/health');
    }

    // Health check
    async healthCheck() {
        return this.request('/health', { includeAuth: false });
    }
}

// Create singleton instance
const apiClient = new TrueMeshAPIClient();

// Export for use in other scripts
window.TrueMeshAPI = apiClient;

// Export class for advanced usage
window.TrueMeshAPIClient = TrueMeshAPIClient;
