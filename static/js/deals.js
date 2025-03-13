'use strict';

// Initialize deals functionality
function initDeals() {
    loadDeals();
    setupDealEvents();
}

// Load and render deals
async function loadDeals(searchTerm = '', customerId = '', status = '') {
    try {
        const deals = await api.getDeals(searchTerm, customerId, status);
        globalState.deals = deals;
        renderDeals(deals);
    } catch (error) {
        console.error('Error loading deals:', error);
    }
}

// Render deals in the table
function renderDeals(deals) {
    const tableBody = document.getElementById('deals-table-body');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (deals.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = `
            <td colspan="6" class="text-center py-4">
                <div class="text-muted">No deals found</div>
            </td>
        `;
        tableBody.appendChild(emptyRow);
        return;
    }
    
    // Create a map of customer IDs to names for quick lookup
    const customerMap = {};
    globalState.customers.forEach(customer => {
        customerMap[customer.id] = customer.name;
    });
    
    deals.forEach(deal => {
        const row = document.createElement('tr');
        row.classList.add('clickable-row');
        row.dataset.id = deal.id;
        
        const customerName = customerMap[deal.customer_id] || 'Unknown';
        const statusClass = getStatusClass(deal.status);
        
        row.innerHTML = `
            <td>${deal.title}</td>
            <td>${formatCurrency(deal.amount)}</td>
            <td><span class="badge ${statusClass}">${deal.status}</span></td>
            <td>${deal.expected_close_date ? formatDate(deal.expected_close_date) : '-'}</td>
            <td>${customerName}</td>
            <td>
                <button class="btn btn-sm btn-primary btn-edit-deal" data-id="${deal.id}">Edit</button>
                <button class="btn btn-sm btn-danger btn-delete-deal" data-id="${deal.id}">Delete</button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Get the appropriate CSS class for a deal status
function getStatusClass(status) {
    const statusMap = {
        'New': 'badge-new',
        'Qualified': 'badge-qualified',
        'Proposal': 'badge-proposal',
        'Negotiation': 'badge-negotiation',
        'Closed Won': 'badge-closed-won',
        'Closed Lost': 'badge-closed-lost'
    };
    
    return statusMap[status] || 'badge-secondary';
}

// Set up deal-related event listeners
function setupDealEvents() {
    // Search
    const searchInput = document.getElementById('deal-search');
    if (searchInput) {
        let debounceTimeout;
        
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                const customerId = document.getElementById('deal-customer-filter').value;
                const status = document.getElementById('deal-status-filter').value;
                loadDeals(searchInput.value, customerId, status);
            }, 300);
        });
    }
    
    // Customer filter
    const customerFilter = document.getElementById('deal-customer-filter');
    if (customerFilter) {
        customerFilter.addEventListener('change', () => {
            const searchTerm = document.getElementById('deal-search').value;
            const status = document.getElementById('deal-status-filter').value;
            loadDeals(searchTerm, customerFilter.value, status);
        });
    }
    
    // Status filter
    const statusFilter = document.getElementById('deal-status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', () => {
            const searchTerm = document.getElementById('deal-search').value;
            const customerId = document.getElementById('deal-customer-filter').value;
            loadDeals(searchTerm, customerId, statusFilter.value);
        });
    }
    
    // Add deal button
    const addButton = document.getElementById('btn-add-deal');
    if (addButton) {
        addButton.addEventListener('click', () => {
            openDealModal();
        });
    }
    
    // Table row and action button clicks
    const tableBody = document.getElementById('deals-table-body');
    if (tableBody) {
        tableBody.addEventListener('click', async (e) => {
            const id = e.target.dataset.id || e.target.closest('tr')?.dataset.id;
            if (!id) return;
            
            if (e.target.classList.contains('btn-edit-deal') || e.target.closest('tr.clickable-row')) {
                openDealModal(id);
            } else if (e.target.classList.contains('btn-delete-deal')) {
                showConfirmation('Are you sure you want to delete this deal?', async () => {
                    try {
                        await api.deleteDeal(id);
                        showAlert('Deal deleted successfully', 'success');
                        loadDeals();
                    } catch (error) {
                        console.error('Error deleting deal:', error);
                    }
                });
            }
        });
    }
    
    // Save deal button
    const saveButton = document.getElementById('btn-save-deal');
    if (saveButton) {
        saveButton.addEventListener('click', saveDeal);
    }
    
    // Delete deal button in modal
    const deleteButton = document.getElementById('btn-delete-deal');
    if (deleteButton) {
        deleteButton.addEventListener('click', () => {
            const dealId = document.getElementById('deal-id').value;
            if (!dealId) return;
            
            showConfirmation('Are you sure you want to delete this deal?', async () => {
                try {
                    await api.deleteDeal(dealId);
                    showAlert('Deal deleted successfully', 'success');
                    
                    // Close modal and refresh list
                    const modal = bootstrap.Modal.getInstance(document.getElementById('deal-modal'));
                    modal.hide();
                    loadDeals();
                } catch (error) {
                    console.error('Error deleting deal:', error);
                }
            });
        });
    }
}

// Open deal modal for add or edit
async function openDealModal(dealId = null) {
    // Get modal elements
    const modal = new bootstrap.Modal(document.getElementById('deal-modal'));
    const modalTitle = document.getElementById('dealModalLabel');
    const form = document.getElementById('deal-form');
    const idInput = document.getElementById('deal-id');
    const deleteButton = document.getElementById('btn-delete-deal');
    
    // Reset form
    form.reset();
    idInput.value = '';
    
    if (dealId) {
        // Edit mode
        modalTitle.textContent = 'Edit Deal';
        deleteButton.classList.remove('d-none');
        
        try {
            const deal = await api.getDeal(dealId);
            
            // Populate form fields
            idInput.value = deal.id;
            document.getElementById('deal-customer').value = deal.customer_id;
            document.getElementById('deal-title').value = deal.title;
            document.getElementById('deal-amount').value = deal.amount;
            document.getElementById('deal-status').value = deal.status;
            document.getElementById('deal-close-date').value = deal.expected_close_date || '';
            document.getElementById('deal-description').value = deal.description || '';
            
        } catch (error) {
            console.error('Error loading deal:', error);
            showAlert('Error loading deal details', 'danger');
            return;
        }
    } else {
        // Add mode
        modalTitle.textContent = 'Add Deal';
        deleteButton.classList.add('d-none');
        
        // Pre-select customer if filter is active
        const customerFilter = document.getElementById('deal-customer-filter');
        if (customerFilter && customerFilter.value) {
            document.getElementById('deal-customer').value = customerFilter.value;
        }
        
        // Pre-select status if filter is active
        const statusFilter = document.getElementById('deal-status-filter');
        if (statusFilter && statusFilter.value) {
            document.getElementById('deal-status').value = statusFilter.value;
        } else {
            // Default to 'New' status
            document.getElementById('deal-status').value = 'New';
        }
    }
    
    modal.show();
}

// Save deal data
async function saveDeal() {
    const form = document.getElementById('deal-form');
    
    // Basic validation
    const customerInput = document.getElementById('deal-customer');
    const titleInput = document.getElementById('deal-title');
    const amountInput = document.getElementById('deal-amount');
    const statusInput = document.getElementById('deal-status');
    
    if (!customerInput.value || !titleInput.value || !amountInput.value || !statusInput.value) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }
    
    // Get form data
    const dealId = document.getElementById('deal-id').value;
    const dealData = {
        customer_id: customerInput.value,
        title: titleInput.value,
        amount: parseFloat(amountInput.value),
        status: statusInput.value,
        expected_close_date: document.getElementById('deal-close-date').value,
        description: document.getElementById('deal-description').value
    };
    
    try {
        let result;
        
        if (dealId) {
            // Update existing deal
            result = await api.updateDeal(dealId, dealData);
            showAlert('Deal updated successfully', 'success');
        } else {
            // Create new deal
            result = await api.createDeal(dealData);
            showAlert('Deal created successfully', 'success');
        }
        
        // Close modal and refresh list
        const modal = bootstrap.Modal.getInstance(document.getElementById('deal-modal'));
        modal.hide();
        
        // Keep the current filters when reloading
        const customerFilter = document.getElementById('deal-customer-filter');
        const statusFilter = document.getElementById('deal-status-filter');
        const searchInput = document.getElementById('deal-search');
        loadDeals(searchInput.value, customerFilter.value, statusFilter.value);
        
    } catch (error) {
        console.error('Error saving deal:', error);
    }
}
