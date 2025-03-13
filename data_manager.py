import json
import os
import uuid
import shutil
from datetime import datetime

# Ensure data directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('data/backup', exist_ok=True)

# File paths
CUSTOMERS_FILE = 'data/customers.json'
CONTACTS_FILE = 'data/contacts.json'
DEALS_FILE = 'data/deals.json'

def ensure_file_exists(file_path, default_data=None):
    """Ensure that a JSON file exists, creating it with default data if it doesn't."""
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump(default_data or [], f)

# Initialize files if they don't exist
ensure_file_exists(CUSTOMERS_FILE)
ensure_file_exists(CONTACTS_FILE)
ensure_file_exists(DEALS_FILE)

# Customer functions
def get_all_customers():
    """Get all customers."""
    try:
        with open(CUSTOMERS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def get_customer(customer_id):
    """Get a customer by ID."""
    customers = get_all_customers()
    for customer in customers:
        if customer.get('id') == customer_id:
            return customer
    return None

def create_customer(data):
    """Create a new customer."""
    customers = get_all_customers()
    
    # Create new customer with additional metadata
    new_customer = {
        'id': str(uuid.uuid4()),
        'name': data.get('name'),
        'email': data.get('email'),
        'phone': data.get('phone'),
        'address': data.get('address', ''),
        'website': data.get('website', ''),
        'industry': data.get('industry', ''),
        'notes': data.get('notes', ''),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    customers.append(new_customer)
    
    with open(CUSTOMERS_FILE, 'w') as f:
        json.dump(customers, f, indent=2)
    
    return new_customer

def update_customer(customer_id, data):
    """Update an existing customer."""
    customers = get_all_customers()
    
    for i, customer in enumerate(customers):
        if customer.get('id') == customer_id:
            # Update customer data while preserving id and created_at
            customers[i].update({
                'name': data.get('name', customer['name']),
                'email': data.get('email', customer['email']),
                'phone': data.get('phone', customer['phone']),
                'address': data.get('address', customer.get('address', '')),
                'website': data.get('website', customer.get('website', '')),
                'industry': data.get('industry', customer.get('industry', '')),
                'notes': data.get('notes', customer.get('notes', '')),
                'updated_at': datetime.now().isoformat()
            })
            
            with open(CUSTOMERS_FILE, 'w') as f:
                json.dump(customers, f, indent=2)
            
            return customers[i]
    
    raise ValueError(f"Customer with ID {customer_id} not found")

def delete_customer(customer_id):
    """Delete a customer."""
    customers = get_all_customers()
    
    initial_count = len(customers)
    customers = [c for c in customers if c.get('id') != customer_id]
    
    if len(customers) == initial_count:
        raise ValueError(f"Customer with ID {customer_id} not found")
    
    with open(CUSTOMERS_FILE, 'w') as f:
        json.dump(customers, f, indent=2)
    
    # Also delete associated contacts and deals
    delete_related_contacts(customer_id)
    delete_related_deals(customer_id)
    
    return True

def search_customers(search_term):
    """Search customers by name, email, or phone."""
    customers = get_all_customers()
    search_term = search_term.lower()
    
    results = []
    for customer in customers:
        if (search_term in customer.get('name', '').lower() or
            search_term in customer.get('email', '').lower() or
            search_term in customer.get('phone', '').lower() or
            search_term in customer.get('industry', '').lower()):
            results.append(customer)
    
    return results

# Contact functions
def get_all_contacts():
    """Get all contacts."""
    try:
        with open(CONTACTS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def get_contact(contact_id):
    """Get a contact by ID."""
    contacts = get_all_contacts()
    for contact in contacts:
        if contact.get('id') == contact_id:
            return contact
    return None

def create_contact(data):
    """Create a new contact."""
    contacts = get_all_contacts()
    
    # Verify customer exists
    customer_id = data.get('customer_id')
    if not get_customer(customer_id):
        raise ValueError(f"Customer with ID {customer_id} not found")
    
    # Create new contact with additional metadata
    new_contact = {
        'id': str(uuid.uuid4()),
        'customer_id': customer_id,
        'name': data.get('name'),
        'email': data.get('email'),
        'phone': data.get('phone'),
        'position': data.get('position', ''),
        'notes': data.get('notes', ''),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    contacts.append(new_contact)
    
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=2)
    
    return new_contact

def update_contact(contact_id, data):
    """Update an existing contact."""
    contacts = get_all_contacts()
    
    for i, contact in enumerate(contacts):
        if contact.get('id') == contact_id:
            # Update contact data while preserving id and created_at
            contacts[i].update({
                'name': data.get('name', contact['name']),
                'email': data.get('email', contact['email']),
                'phone': data.get('phone', contact['phone']),
                'position': data.get('position', contact.get('position', '')),
                'notes': data.get('notes', contact.get('notes', '')),
                'updated_at': datetime.now().isoformat()
            })
            
            # Only update customer_id if provided and valid
            if 'customer_id' in data:
                customer_id = data['customer_id']
                if not get_customer(customer_id):
                    raise ValueError(f"Customer with ID {customer_id} not found")
                contacts[i]['customer_id'] = customer_id
            
            with open(CONTACTS_FILE, 'w') as f:
                json.dump(contacts, f, indent=2)
            
            return contacts[i]
    
    raise ValueError(f"Contact with ID {contact_id} not found")

def delete_contact(contact_id):
    """Delete a contact."""
    contacts = get_all_contacts()
    
    initial_count = len(contacts)
    contacts = [c for c in contacts if c.get('id') != contact_id]
    
    if len(contacts) == initial_count:
        raise ValueError(f"Contact with ID {contact_id} not found")
    
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=2)
    
    return True

def delete_related_contacts(customer_id):
    """Delete all contacts related to a customer."""
    contacts = get_all_contacts()
    contacts = [c for c in contacts if c.get('customer_id') != customer_id]
    
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=2)

def search_contacts(search_term):
    """Search contacts by name, email, or phone."""
    contacts = get_all_contacts()
    search_term = search_term.lower()
    
    results = []
    for contact in contacts:
        if (search_term in contact.get('name', '').lower() or
            search_term in contact.get('email', '').lower() or
            search_term in contact.get('phone', '').lower() or
            search_term in contact.get('position', '').lower()):
            results.append(contact)
    
    return results

# Deal functions
def get_all_deals():
    """Get all deals."""
    try:
        with open(DEALS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def get_deal(deal_id):
    """Get a deal by ID."""
    deals = get_all_deals()
    for deal in deals:
        if deal.get('id') == deal_id:
            return deal
    return None

def create_deal(data):
    """Create a new deal."""
    deals = get_all_deals()
    
    # Verify customer exists
    customer_id = data.get('customer_id')
    if not get_customer(customer_id):
        raise ValueError(f"Customer with ID {customer_id} not found")
    
    # Create new deal with additional metadata
    new_deal = {
        'id': str(uuid.uuid4()),
        'customer_id': customer_id,
        'title': data.get('title'),
        'amount': data.get('amount'),
        'status': data.get('status'),
        'expected_close_date': data.get('expected_close_date', ''),
        'description': data.get('description', ''),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    deals.append(new_deal)
    
    with open(DEALS_FILE, 'w') as f:
        json.dump(deals, f, indent=2)
    
    return new_deal

def update_deal(deal_id, data):
    """Update an existing deal."""
    deals = get_all_deals()
    
    for i, deal in enumerate(deals):
        if deal.get('id') == deal_id:
            # Update deal data while preserving id and created_at
            deals[i].update({
                'title': data.get('title', deal['title']),
                'amount': data.get('amount', deal['amount']),
                'status': data.get('status', deal['status']),
                'expected_close_date': data.get('expected_close_date', deal.get('expected_close_date', '')),
                'description': data.get('description', deal.get('description', '')),
                'updated_at': datetime.now().isoformat()
            })
            
            # Only update customer_id if provided and valid
            if 'customer_id' in data:
                customer_id = data['customer_id']
                if not get_customer(customer_id):
                    raise ValueError(f"Customer with ID {customer_id} not found")
                deals[i]['customer_id'] = customer_id
            
            with open(DEALS_FILE, 'w') as f:
                json.dump(deals, f, indent=2)
            
            return deals[i]
    
    raise ValueError(f"Deal with ID {deal_id} not found")

def delete_deal(deal_id):
    """Delete a deal."""
    deals = get_all_deals()
    
    initial_count = len(deals)
    deals = [d for d in deals if d.get('id') != deal_id]
    
    if len(deals) == initial_count:
        raise ValueError(f"Deal with ID {deal_id} not found")
    
    with open(DEALS_FILE, 'w') as f:
        json.dump(deals, f, indent=2)
    
    return True

def delete_related_deals(customer_id):
    """Delete all deals related to a customer."""
    deals = get_all_deals()
    deals = [d for d in deals if d.get('customer_id') != customer_id]
    
    with open(DEALS_FILE, 'w') as f:
        json.dump(deals, f, indent=2)

def search_deals(search_term):
    """Search deals by title, status, or description."""
    deals = get_all_deals()
    search_term = search_term.lower()
    
    results = []
    for deal in deals:
        if (search_term in deal.get('title', '').lower() or
            search_term in deal.get('status', '').lower() or
            search_term in deal.get('description', '').lower() or
            search_term in str(deal.get('amount', '')).lower()):
            results.append(deal)
    
    return results

# Backup function
def backup_data(timestamp):
    """Create a backup of all data files."""
    backup_dir = f'data/backup/{timestamp}'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copy all data files to backup directory
    for file_name in ['customers.json', 'contacts.json', 'deals.json', 'users.json']:
        source_path = f'data/{file_name}'
        if os.path.exists(source_path):
            shutil.copy2(source_path, f'{backup_dir}/{file_name}')
    
    return backup_dir
