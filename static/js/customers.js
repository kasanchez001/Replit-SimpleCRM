'use strict';

// Initialize customers functionality
function initCustomers() {
    loadCustomers();
    setupCustomerEvents();
}

// Load and render customers
async function loadCustomers(searchTerm = '') {
    try {
        const customers = await api.getCustomers(searchTerm);
        globalState.customers = customers;
        renderCustomers(customers);
        populateCustomerDropdowns();
    } catch (error) {
        console.error('Error loading customers:', error);
    }
}

// Render customers in the table
function renderCustomers(customers) {
    const tableBody = document.getElementById('customers-table-body');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (customers.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = `
            <td colspan="5" class="text-center py-4">
                <div class="text-muted">No customers found</div>
            </td>
        `;
        tableBody.appendChild(emptyRow);
        return;
    }
    
    customers.forEach(customer => {
        const row = document.createElement('tr');
        row.classList.add('clickable-row');
        row.dataset.id = customer.id;
        
        row.innerHTML = `
            <td>${customer.name}</td>
            <td>${customer.email}</td>
            <td>${customer.phone}</td>
            <td>${customer.industry || '-'}</td>
            <td>
                <button class="btn btn-sm btn-primary btn-edit-customer" data-id="${customer.id}">Edit</button>
                <button class="btn btn-sm btn-danger btn-delete-customer" data-id="${customer.id}">Delete</button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Set up customer-related event listeners
function setupCustomerEvents() {
    // Search
    const searchInput = document.getElementById('customer-search');
    if (searchInput) {
        let debounceTimeout;
        
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                loadCustomers(searchInput.value);
            }, 300);
        });
    }
    
    // Add customer button
    const addButton = document.getElementById('btn-add-customer');
    if (addButton) {
        addButton.addEventListener('click', () => {
            openCustomerModal();
        });
    }
    
    // Table row and action button clicks
    const tableBody = document.getElementById('customers-table-body');
    if (tableBody) {
        tableBody.addEventListener('click', async (e) => {
            const id = e.target.dataset.id || e.target.closest('tr')?.dataset.id;
            if (!id) return;
            
            if (e.target.classList.contains('btn-edit-customer') || e.target.closest('tr.clickable-row')) {
                openCustomerModal(id);
            } else if (e.target.classList.contains('btn-delete-customer')) {
                showConfirmation('Are you sure you want to delete this customer? This will also delete all associated contacts and deals.', async () => {
                    try {
                        await api.deleteCustomer(id);
                        showAlert('Customer deleted successfully', 'success');
                        loadCustomers();
                    } catch (error) {
                        console.error('Error deleting customer:', error);
                    }
                });
            }
        });
    }
    
    // Save customer button
    const saveButton = document.getElementById('btn-save-customer');
    if (saveButton) {
        saveButton.addEventListener('click', saveCustomer);
    }
    
    // Delete customer button in modal
    const deleteButton = document.getElementById('btn-delete-customer');
    if (deleteButton) {
        deleteButton.addEventListener('click', () => {
            const customerId = document.getElementById('customer-id').value;
            if (!customerId) return;
            
            showConfirmation('Are you sure you want to delete this customer? This will also delete all associated contacts and deals.', async () => {
                try {
                    await api.deleteCustomer(customerId);
                    showAlert('Customer deleted successfully', 'success');
                    
                    // Close modal and refresh list
                    const modal = bootstrap.Modal.getInstance(document.getElementById('customer-modal'));
                    modal.hide();
                    loadCustomers();
                } catch (error) {
                    console.error('Error deleting customer:', error);
                }
            });
        });
    }
}

// Open customer modal for add or edit
async function openCustomerModal(customerId = null) {
    // Get modal elements
    const modal = new bootstrap.Modal(document.getElementById('customer-modal'));
    const modalTitle = document.getElementById('customerModalLabel');
    const form = document.getElementById('customer-form');
    const idInput = document.getElementById('customer-id');
    const deleteButton = document.getElementById('btn-delete-customer');
    
    // Reset form
    form.reset();
    idInput.value = '';
    
    if (customerId) {
        // Edit mode
        modalTitle.textContent = 'Edit Customer';
        deleteButton.classList.remove('d-none');
        
        try {
            const customer = await api.getCustomer(customerId);
            
            // Populate form fields
            idInput.value = customer.id;
            document.getElementById('customer-name').value = customer.name;
            document.getElementById('customer-email').value = customer.email;
            document.getElementById('customer-phone').value = customer.phone;
            document.getElementById('customer-address').value = customer.address || '';
            document.getElementById('customer-website').value = customer.website || '';
            document.getElementById('customer-industry').value = customer.industry || '';
            document.getElementById('customer-notes').value = customer.notes || '';
            
        } catch (error) {
            console.error('Error loading customer:', error);
            showAlert('Error loading customer details', 'danger');
            return;
        }
    } else {
        // Add mode
        modalTitle.textContent = 'Add Customer';
        deleteButton.classList.add('d-none');
    }
    
    modal.show();
}

// Save customer data
async function saveCustomer() {
    const form = document.getElementById('customer-form');
    
    // Basic validation
    const nameInput = document.getElementById('customer-name');
    const emailInput = document.getElementById('customer-email');
    const phoneInput = document.getElementById('customer-phone');
    
    if (!nameInput.value || !emailInput.value || !phoneInput.value) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }
    
    // Get form data
    const customerId = document.getElementById('customer-id').value;
    const customerData = {
        name: nameInput.value,
        email: emailInput.value,
        phone: phoneInput.value,
        address: document.getElementById('customer-address').value,
        website: document.getElementById('customer-website').value,
        industry: document.getElementById('customer-industry').value,
        notes: document.getElementById('customer-notes').value
    };
    
    try {
        let result;
        
        if (customerId) {
            // Update existing customer
            result = await api.updateCustomer(customerId, customerData);
            showAlert('Customer updated successfully', 'success');
        } else {
            // Create new customer
            result = await api.createCustomer(customerData);
            showAlert('Customer created successfully', 'success');
        }
        
        // Close modal and refresh list
        const modal = bootstrap.Modal.getInstance(document.getElementById('customer-modal'));
        modal.hide();
        loadCustomers();
        
    } catch (error) {
        console.error('Error saving customer:', error);
    }
}
