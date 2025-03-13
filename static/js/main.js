'use strict';

// Global state
const globalState = {
    customers: [],
    contacts: [],
    deals: []
};

// API utility functions
const api = {
    async request(url, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin'
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, options);
            
            // Handle API errors
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'API request failed');
            }
            
            return await response.json();
        } catch (error) {
            showAlert(error.message, 'danger');
            throw error;
        }
    },
    
    // Customers
    async getCustomers(searchTerm = '') {
        const url = searchTerm ? `/api/customers?search=${encodeURIComponent(searchTerm)}` : '/api/customers';
        return await this.request(url);
    },
    
    async getCustomer(id) {
        return await this.request(`/api/customers/${id}`);
    },
    
    async createCustomer(data) {
        return await this.request('/api/customers', 'POST', data);
    },
    
    async updateCustomer(id, data) {
        return await this.request(`/api/customers/${id}`, 'PUT', data);
    },
    
    async deleteCustomer(id) {
        return await this.request(`/api/customers/${id}`, 'DELETE');
    },
    
    // Contacts
    async getContacts(searchTerm = '', customerId = '') {
        let url = '/api/contacts';
        const params = [];
        
        if (searchTerm) params.push(`search=${encodeURIComponent(searchTerm)}`);
        if (customerId) params.push(`customer_id=${encodeURIComponent(customerId)}`);
        
        if (params.length > 0) {
            url += `?${params.join('&')}`;
        }
        
        return await this.request(url);
    },
    
    async getContact(id) {
        return await this.request(`/api/contacts/${id}`);
    },
    
    async createContact(data) {
        return await this.request('/api/contacts', 'POST', data);
    },
    
    async updateContact(id, data) {
        return await this.request(`/api/contacts/${id}`, 'PUT', data);
    },
    
    async deleteContact(id) {
        return await this.request(`/api/contacts/${id}`, 'DELETE');
    },
    
    // Deals
    async getDeals(searchTerm = '', customerId = '', status = '') {
        let url = '/api/deals';
        const params = [];
        
        if (searchTerm) params.push(`search=${encodeURIComponent(searchTerm)}`);
        if (customerId) params.push(`customer_id=${encodeURIComponent(customerId)}`);
        
        if (params.length > 0) {
            url += `?${params.join('&')}`;
        }
        
        const deals = await this.request(url);
        
        // Filter by status if provided (client-side since API doesn't support it)
        if (status && deals.length > 0) {
            return deals.filter(deal => deal.status === status);
        }
        
        return deals;
    },
    
    async getDeal(id) {
        return await this.request(`/api/deals/${id}`);
    },
    
    async createDeal(data) {
        return await this.request('/api/deals', 'POST', data);
    },
    
    async updateDeal(id, data) {
        return await this.request(`/api/deals/${id}`, 'PUT', data);
    },
    
    async deleteDeal(id) {
        return await this.request(`/api/deals/${id}`, 'DELETE');
    },
    
    // Backup
    async createBackup() {
        return await this.request('/api/backup', 'POST');
    },
    
    // Genesys Cloud Integration
    async checkGenesysStatus() {
        return await this.request('/api/genesys/status');
    },
    
    async getGenesysUsers(limit = 25, page = 1) {
        return await this.request(`/api/genesys/users?limit=${limit}&page=${page}`);
    },
    
    async getGenesysUser(userId) {
        return await this.request(`/api/genesys/users/${userId}`);
    },
    
    async getGenesysContacts(limit = 25, page = 1) {
        return await this.request(`/api/genesys/contacts?limit=${limit}&page=${page}`);
    },
    
    async getGenesysContact(contactId) {
        return await this.request(`/api/genesys/contacts/${contactId}`);
    },
    
    async createGenesysContact(data) {
        return await this.request('/api/genesys/contacts', 'POST', data);
    },
    
    async updateGenesysContact(contactId, data) {
        return await this.request(`/api/genesys/contacts/${contactId}`, 'PUT', data);
    },
    
    async importGenesysContact(contactId) {
        return await this.request(`/api/genesys/import/contact/${contactId}`, 'POST');
    },
    
    async importAllGenesysContacts(limit = 100) {
        return await this.request(`/api/genesys/import/contacts?limit=${limit}`, 'POST');
    },
    
    async syncContactsToGenesys() {
        return await this.request('/api/genesys/sync/contacts', 'POST');
    },
    
    async getGenesysInteractions(limit = 25, page = 1) {
        return await this.request(`/api/genesys/interactions?limit=${limit}&page=${page}`);
    },
    
    async getGenesysInteraction(interactionId) {
        return await this.request(`/api/genesys/interactions/${interactionId}`);
    },
    
    async recordGenesysInteraction(interactionId, customerId) {
        return await this.request(`/api/genesys/interactions/${interactionId}/record`, 'POST', {
            customer_id: customerId
        });
    },
    
    async getGenesysQueues(limit = 25, page = 1) {
        return await this.request(`/api/genesys/queues?limit=${limit}&page=${page}`);
    }
};

// UI utility functions
function showAlert(message, type = 'success', timeout = 5000) {
    const alertId = `alert-${Date.now()}`;
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    const alertContainer = document.getElementById('alert-container');
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    if (timeout > 0) {
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                alertElement.remove();
            }
        }, timeout);
    }
}

function showConfirmation(message, confirmCallback) {
    const confirmModal = new bootstrap.Modal(document.getElementById('confirm-modal'));
    const confirmMessage = document.getElementById('confirm-message');
    const confirmButton = document.getElementById('btn-confirm-action');
    
    confirmMessage.textContent = message;
    
    // Remove any existing event listeners
    const newConfirmButton = confirmButton.cloneNode(true);
    confirmButton.parentNode.replaceChild(newConfirmButton, confirmButton);
    
    // Add new event listener
    newConfirmButton.addEventListener('click', () => {
        confirmModal.hide();
        confirmCallback();
    });
    
    confirmModal.show();
}

function formatDate(isoString) {
    if (!isoString) return '';
    
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return isoString;
    
    return date.toLocaleDateString();
}

function formatCurrency(amount) {
    if (amount === undefined || amount === null) return '';
    
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function populateCustomerDropdowns() {
    const customerSelects = [
        document.getElementById('contact-customer'),
        document.getElementById('deal-customer'),
        document.getElementById('contact-customer-filter'),
        document.getElementById('deal-customer-filter')
    ];
    
    customerSelects.forEach(select => {
        if (!select) return;
        
        // Clear existing options except the first one
        while (select.options.length > 1) {
            select.remove(1);
        }
        
        // Add options for each customer
        globalState.customers.forEach(customer => {
            const option = document.createElement('option');
            option.value = customer.id;
            option.textContent = customer.name;
            select.appendChild(option);
        });
    });
}

// Navigation
function setupNavigation() {
    const navLinks = {
        'nav-customers': 'customers-section',
        'nav-contacts': 'contacts-section',
        'nav-deals': 'deals-section'
    };
    
    Object.entries(navLinks).forEach(([navId, sectionId]) => {
        const navLink = document.getElementById(navId);
        if (navLink) {
            navLink.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Update active state
                document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
                navLink.classList.add('active');
                
                // Show selected section, hide others
                document.querySelectorAll('.content-section').forEach(section => {
                    section.classList.add('d-none');
                });
                
                const section = document.getElementById(sectionId);
                if (section) {
                    section.classList.remove('d-none');
                }
            });
        }
    });
}

// Backup functionality
function setupBackup() {
    const backupButton = document.getElementById('btn-backup');
    if (backupButton) {
        backupButton.addEventListener('click', async () => {
            try {
                backupButton.disabled = true;
                backupButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Backing up...';
                
                const result = await api.createBackup();
                showAlert(result.message, 'success');
            } catch (error) {
                console.error('Backup failed:', error);
            } finally {
                backupButton.disabled = false;
                backupButton.textContent = 'Backup Data';
            }
        });
    }
}

// Initialize the application
async function initApp() {
    setupNavigation();
    setupBackup();
    
    try {
        // Load initial data
        const [customers, contacts, deals] = await Promise.all([
            api.getCustomers(),
            api.getContacts(),
            api.getDeals()
        ]);
        
        globalState.customers = customers;
        globalState.contacts = contacts;
        globalState.deals = deals;
        
        // Initialize UI components
        populateCustomerDropdowns();
        
        // Initialize each section
        if (typeof initCustomers === 'function') initCustomers();
        if (typeof initContacts === 'function') initContacts();
        if (typeof initDeals === 'function') initDeals();
        
    } catch (error) {
        console.error('Error initializing app:', error);
        showAlert('Failed to load data. Please try refreshing the page.', 'danger');
    }
}

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', initApp);
