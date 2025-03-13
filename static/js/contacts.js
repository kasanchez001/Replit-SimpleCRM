'use strict';

// Initialize contacts functionality
function initContacts() {
    loadContacts();
    setupContactEvents();
}

// Load and render contacts
async function loadContacts(searchTerm = '', customerId = '') {
    try {
        const contacts = await api.getContacts(searchTerm, customerId);
        globalState.contacts = contacts;
        renderContacts(contacts);
    } catch (error) {
        console.error('Error loading contacts:', error);
    }
}

// Render contacts in the table
function renderContacts(contacts) {
    const tableBody = document.getElementById('contacts-table-body');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (contacts.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = `
            <td colspan="6" class="text-center py-4">
                <div class="text-muted">No contacts found</div>
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
    
    contacts.forEach(contact => {
        const row = document.createElement('tr');
        row.classList.add('clickable-row');
        row.dataset.id = contact.id;
        
        const customerName = customerMap[contact.customer_id] || 'Unknown';
        
        row.innerHTML = `
            <td>${contact.name}</td>
            <td>${contact.email}</td>
            <td>${contact.phone}</td>
            <td>${contact.position || '-'}</td>
            <td>${customerName}</td>
            <td>
                <button class="btn btn-sm btn-primary btn-edit-contact" data-id="${contact.id}">Edit</button>
                <button class="btn btn-sm btn-danger btn-delete-contact" data-id="${contact.id}">Delete</button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Set up contact-related event listeners
function setupContactEvents() {
    // Search
    const searchInput = document.getElementById('contact-search');
    if (searchInput) {
        let debounceTimeout;
        
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                const customerId = document.getElementById('contact-customer-filter').value;
                loadContacts(searchInput.value, customerId);
            }, 300);
        });
    }
    
    // Customer filter
    const customerFilter = document.getElementById('contact-customer-filter');
    if (customerFilter) {
        customerFilter.addEventListener('change', () => {
            const searchTerm = document.getElementById('contact-search').value;
            loadContacts(searchTerm, customerFilter.value);
        });
    }
    
    // Add contact button
    const addButton = document.getElementById('btn-add-contact');
    if (addButton) {
        addButton.addEventListener('click', () => {
            openContactModal();
        });
    }
    
    // Table row and action button clicks
    const tableBody = document.getElementById('contacts-table-body');
    if (tableBody) {
        tableBody.addEventListener('click', async (e) => {
            const id = e.target.dataset.id || e.target.closest('tr')?.dataset.id;
            if (!id) return;
            
            if (e.target.classList.contains('btn-edit-contact') || e.target.closest('tr.clickable-row')) {
                openContactModal(id);
            } else if (e.target.classList.contains('btn-delete-contact')) {
                showConfirmation('Are you sure you want to delete this contact?', async () => {
                    try {
                        await api.deleteContact(id);
                        showAlert('Contact deleted successfully', 'success');
                        loadContacts();
                    } catch (error) {
                        console.error('Error deleting contact:', error);
                    }
                });
            }
        });
    }
    
    // Save contact button
    const saveButton = document.getElementById('btn-save-contact');
    if (saveButton) {
        saveButton.addEventListener('click', saveContact);
    }
    
    // Delete contact button in modal
    const deleteButton = document.getElementById('btn-delete-contact');
    if (deleteButton) {
        deleteButton.addEventListener('click', () => {
            const contactId = document.getElementById('contact-id').value;
            if (!contactId) return;
            
            showConfirmation('Are you sure you want to delete this contact?', async () => {
                try {
                    await api.deleteContact(contactId);
                    showAlert('Contact deleted successfully', 'success');
                    
                    // Close modal and refresh list
                    const modal = bootstrap.Modal.getInstance(document.getElementById('contact-modal'));
                    modal.hide();
                    loadContacts();
                } catch (error) {
                    console.error('Error deleting contact:', error);
                }
            });
        });
    }
}

// Open contact modal for add or edit
async function openContactModal(contactId = null) {
    // Get modal elements
    const modal = new bootstrap.Modal(document.getElementById('contact-modal'));
    const modalTitle = document.getElementById('contactModalLabel');
    const form = document.getElementById('contact-form');
    const idInput = document.getElementById('contact-id');
    const deleteButton = document.getElementById('btn-delete-contact');
    
    // Reset form
    form.reset();
    idInput.value = '';
    
    if (contactId) {
        // Edit mode
        modalTitle.textContent = 'Edit Contact';
        deleteButton.classList.remove('d-none');
        
        try {
            const contact = await api.getContact(contactId);
            
            // Populate form fields
            idInput.value = contact.id;
            document.getElementById('contact-customer').value = contact.customer_id;
            document.getElementById('contact-name').value = contact.name;
            document.getElementById('contact-email').value = contact.email;
            document.getElementById('contact-phone').value = contact.phone;
            document.getElementById('contact-position').value = contact.position || '';
            document.getElementById('contact-notes').value = contact.notes || '';
            
        } catch (error) {
            console.error('Error loading contact:', error);
            showAlert('Error loading contact details', 'danger');
            return;
        }
    } else {
        // Add mode
        modalTitle.textContent = 'Add Contact';
        deleteButton.classList.add('d-none');
        
        // Pre-select customer if filter is active
        const customerFilter = document.getElementById('contact-customer-filter');
        if (customerFilter && customerFilter.value) {
            document.getElementById('contact-customer').value = customerFilter.value;
        }
    }
    
    modal.show();
}

// Save contact data
async function saveContact() {
    const form = document.getElementById('contact-form');
    
    // Basic validation
    const customerInput = document.getElementById('contact-customer');
    const nameInput = document.getElementById('contact-name');
    const emailInput = document.getElementById('contact-email');
    const phoneInput = document.getElementById('contact-phone');
    
    if (!customerInput.value || !nameInput.value || !emailInput.value || !phoneInput.value) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }
    
    // Get form data
    const contactId = document.getElementById('contact-id').value;
    const contactData = {
        customer_id: customerInput.value,
        name: nameInput.value,
        email: emailInput.value,
        phone: phoneInput.value,
        position: document.getElementById('contact-position').value,
        notes: document.getElementById('contact-notes').value
    };
    
    try {
        let result;
        
        if (contactId) {
            // Update existing contact
            result = await api.updateContact(contactId, contactData);
            showAlert('Contact updated successfully', 'success');
        } else {
            // Create new contact
            result = await api.createContact(contactData);
            showAlert('Contact created successfully', 'success');
        }
        
        // Close modal and refresh list
        const modal = bootstrap.Modal.getInstance(document.getElementById('contact-modal'));
        modal.hide();
        
        // Keep the current customer filter when reloading
        const customerFilter = document.getElementById('contact-customer-filter');
        const searchInput = document.getElementById('contact-search');
        loadContacts(searchInput.value, customerFilter.value);
        
    } catch (error) {
        console.error('Error saving contact:', error);
    }
}
