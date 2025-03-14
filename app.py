import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from auth import get_user_by_username, register_user, authenticate_user
from data_manager import (
    get_all_customers, get_customer, create_customer, update_customer, delete_customer,
    get_all_contacts, get_contact, create_contact, update_contact, delete_contact,
    get_all_deals, get_deal, create_deal, update_deal, delete_deal,
    search_customers, search_contacts, search_deals, backup_data
)
from genesys_integration import GenesysCloudIntegration

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-secret-key")

# API authentication
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user.get('password'), password):
        return username
    return None

# Web Routes
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if authenticate_user(username, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match', 'danger')
        elif get_user_by_username(username):
            flash('Username already exists', 'danger')
        else:
            register_user(username, password)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/api-docs')
def api_docs():
    return render_template('api_docs.html')

# API Routes for Customers
@app.route('/api/customers', methods=['GET'])
@auth.login_required
def api_get_customers():
    search_term = request.args.get('search', '')
    if search_term:
        customers = search_customers(search_term)
    else:
        customers = get_all_customers()
    return jsonify(customers)

@app.route('/api/customers/<customer_id>', methods=['GET'])
@auth.login_required
def api_get_customer(customer_id):
    customer = get_customer(customer_id)
    if customer:
        return jsonify(customer)
    return jsonify({"error": "Customer not found"}), 404

@app.route('/api/customers', methods=['POST'])
@auth.login_required
def api_add_customer():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    required_fields = ['name', 'email', 'phone']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400
    
    try:
        customer = create_customer(data)
        return jsonify(customer), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/customers/<customer_id>', methods=['PUT'])
@auth.login_required
def api_update_customer(customer_id):
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    customer = get_customer(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    try:
        updated_customer = update_customer(customer_id, data)
        return jsonify(updated_customer)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/customers/<customer_id>', methods=['DELETE'])
@auth.login_required
def api_delete_customer(customer_id):
    customer = get_customer(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    try:
        delete_customer(customer_id)
        return jsonify({"message": "Customer deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API Routes for Contacts
@app.route('/api/contacts', methods=['GET'])
@auth.login_required
def api_get_contacts():
    search_term = request.args.get('search', '')
    customer_id = request.args.get('customer_id', '')
    
    if search_term:
        contacts = search_contacts(search_term)
    else:
        contacts = get_all_contacts()
    
    if customer_id:
        contacts = [c for c in contacts if c.get('customer_id') == customer_id]
        
    return jsonify(contacts)

@app.route('/api/contacts/<contact_id>', methods=['GET'])
@auth.login_required
def api_get_contact(contact_id):
    contact = get_contact(contact_id)
    if contact:
        return jsonify(contact)
    return jsonify({"error": "Contact not found"}), 404

@app.route('/api/contacts', methods=['POST'])
@auth.login_required
def api_add_contact():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    required_fields = ['name', 'email', 'phone', 'customer_id']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400
    
    try:
        contact = create_contact(data)
        return jsonify(contact), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/contacts/<contact_id>', methods=['PUT'])
@auth.login_required
def api_update_contact(contact_id):
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    contact = get_contact(contact_id)
    if not contact:
        return jsonify({"error": "Contact not found"}), 404
    
    try:
        updated_contact = update_contact(contact_id, data)
        return jsonify(updated_contact)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/contacts/<contact_id>', methods=['DELETE'])
@auth.login_required
def api_delete_contact(contact_id):
    contact = get_contact(contact_id)
    if not contact:
        return jsonify({"error": "Contact not found"}), 404
    
    try:
        delete_contact(contact_id)
        return jsonify({"message": "Contact deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API Routes for Deals
@app.route('/api/deals', methods=['GET'])
@auth.login_required
def api_get_deals():
    search_term = request.args.get('search', '')
    customer_id = request.args.get('customer_id', '')
    
    if search_term:
        deals = search_deals(search_term)
    else:
        deals = get_all_deals()
    
    if customer_id:
        deals = [d for d in deals if d.get('customer_id') == customer_id]
        
    return jsonify(deals)

@app.route('/api/deals/<deal_id>', methods=['GET'])
@auth.login_required
def api_get_deal(deal_id):
    deal = get_deal(deal_id)
    if deal:
        return jsonify(deal)
    return jsonify({"error": "Deal not found"}), 404

@app.route('/api/deals', methods=['POST'])
@auth.login_required
def api_add_deal():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    required_fields = ['title', 'amount', 'status', 'customer_id']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400
    
    try:
        deal = create_deal(data)
        return jsonify(deal), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/deals/<deal_id>', methods=['PUT'])
@auth.login_required
def api_update_deal(deal_id):
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    deal = get_deal(deal_id)
    if not deal:
        return jsonify({"error": "Deal not found"}), 404
    
    try:
        updated_deal = update_deal(deal_id, data)
        return jsonify(updated_deal)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/deals/<deal_id>', methods=['DELETE'])
@auth.login_required
def api_delete_deal(deal_id):
    deal = get_deal(deal_id)
    if not deal:
        return jsonify({"error": "Deal not found"}), 404
    
    try:
        delete_deal(deal_id)
        return jsonify({"message": "Deal deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Backup Route
@app.route('/api/backup', methods=['POST'])
@auth.login_required
def api_backup():
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_data(timestamp)
        return jsonify({"message": f"Backup created successfully with timestamp {timestamp}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Genesys Cloud Integration Routes
@app.route('/api/genesys/status', methods=['GET'])
@auth.login_required
def api_genesys_status():
    """Check if Genesys Cloud integration is configured"""
    genesys = GenesysCloudIntegration()
    if genesys.is_configured():
        return jsonify({"status": "configured"})
    else:
        return jsonify({"status": "not_configured", 
                       "message": "Genesys Cloud credentials are not set. Please configure the GENESYS_CLIENT_ID, GENESYS_CLIENT_SECRET, and GENESYS_REGION environment variables."})

@app.route('/api/genesys/users', methods=['GET'])
@auth.login_required
def api_genesys_users():
    """Get Genesys Cloud users"""
    genesys = GenesysCloudIntegration()
    limit = request.args.get('limit', 25, type=int)
    page = request.args.get('page', 1, type=int)
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        result = genesys.get_users(limit=limit, page_number=page)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/genesys/users/<user_id>', methods=['GET'])
@auth.login_required
def api_genesys_user(user_id):
    """Get a specific Genesys Cloud user"""
    genesys = GenesysCloudIntegration()
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        result = genesys.get_user(user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/genesys/contacts', methods=['GET'])
@auth.login_required
def api_genesys_contacts():
    """Get Genesys Cloud contacts"""
    genesys = GenesysCloudIntegration()
    limit = request.args.get('limit', 25, type=int)
    page = request.args.get('page', 1, type=int)
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        result = genesys.get_contacts(limit=limit, page_number=page)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/genesys/contacts/<contact_id>', methods=['GET'])
@auth.login_required
def api_genesys_contact(contact_id):
    """Get a specific Genesys Cloud contact"""
    genesys = GenesysCloudIntegration()
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        result = genesys.get_contact(contact_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/genesys/contacts', methods=['POST'])
@auth.login_required
def api_genesys_add_contact():
    """Create a new contact in Genesys Cloud"""
    genesys = GenesysCloudIntegration()
    data = request.json
    
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        result = genesys.create_contact(data)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/genesys/interactions', methods=['GET'])
@auth.login_required
def api_genesys_interactions():
    """Get Genesys Cloud interactions"""
    genesys = GenesysCloudIntegration()
    limit = request.args.get('limit', 25, type=int)
    page = request.args.get('page', 1, type=int)
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        result = genesys.get_interactions(limit=limit, page_number=page)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/genesys/interactions/<interaction_id>', methods=['GET'])
@auth.login_required
def api_genesys_interaction(interaction_id):
    """Get a specific Genesys Cloud interaction"""
    genesys = GenesysCloudIntegration()
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        result = genesys.get_interaction(interaction_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/genesys/queues', methods=['GET'])
@auth.login_required
def api_genesys_queues():
    """Get Genesys Cloud queues"""
    genesys = GenesysCloudIntegration()
    limit = request.args.get('limit', 25, type=int)
    page = request.args.get('page', 1, type=int)
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        result = genesys.get_queues(limit=limit, page_number=page)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Sync contacts between CRM and Genesys
@app.route('/api/genesys/sync/contacts', methods=['POST'])
@auth.login_required
def api_genesys_sync_contacts():
    """Sync contacts between CRM and Genesys Cloud"""
    genesys = GenesysCloudIntegration()
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        # Get all CRM contacts
        crm_contacts = get_all_contacts()
        
        # Convert CRM contacts to Genesys format
        genesys_contacts = []
        for contact in crm_contacts:
            genesys_contact = {
                "firstName": contact.get("name", "").split()[0] if contact.get("name") else "",
                "lastName": " ".join(contact.get("name", "").split()[1:]) if contact.get("name") and len(contact.get("name", "").split()) > 1 else "",
                "emails": [{"address": contact.get("email")}] if contact.get("email") else [],
                "phoneNumbers": [{"number": contact.get("phone")}] if contact.get("phone") else [],
                "externalIds": [{"id": contact.get("id")}]
            }
            genesys_contacts.append(genesys_contact)
        
        # Create contacts in Genesys Cloud
        results = []
        for contact in genesys_contacts:
            result = genesys.create_contact(contact)
            results.append(result)
        
        return jsonify({"message": f"Synced {len(results)} contacts to Genesys Cloud", "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update a contact in Genesys Cloud
@app.route('/api/genesys/contacts/<contact_id>', methods=['PUT'])
@auth.login_required
def api_genesys_update_contact(contact_id):
    """Update a contact in Genesys Cloud"""
    genesys = GenesysCloudIntegration()
    data = request.json
    
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        result = genesys.update_contact(contact_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Import a contact from Genesys to CRM
@app.route('/api/genesys/import/contact/<contact_id>', methods=['POST'])
@auth.login_required
def api_genesys_import_contact(contact_id):
    """Import a specific contact from Genesys Cloud to CRM"""
    genesys = GenesysCloudIntegration()
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        # Get contact from Genesys
        genesys_contact = genesys.get_contact(contact_id)
        
        if 'error' in genesys_contact:
            return jsonify({"error": f"Failed to retrieve contact from Genesys: {genesys_contact['error']}"}), 400
        
        # Convert to CRM format
        crm_contact = {
            "name": f"{genesys_contact.get('firstName', '')} {genesys_contact.get('lastName', '')}".strip(),
            "email": next((email.get('address') for email in genesys_contact.get('emails', []) if 'address' in email), ""),
            "phone": next((phone.get('number') for phone in genesys_contact.get('phoneNumbers', []) if 'number' in phone), ""),
            "notes": f"Imported from Genesys Cloud. Contact ID: {contact_id}",
            "genesys_id": contact_id
        }
        
        # Add to CRM
        new_contact = create_contact(crm_contact)
        return jsonify({"message": "Contact imported successfully", "contact": new_contact}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Import all contacts from Genesys to CRM
@app.route('/api/genesys/import/contacts', methods=['POST'])
@auth.login_required
def api_genesys_import_all_contacts():
    """Import all contacts from Genesys Cloud to CRM"""
    genesys = GenesysCloudIntegration()
    limit = request.args.get('limit', 100, type=int)
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        # Get contacts from Genesys
        genesys_contacts = genesys.get_contacts(limit=limit)
        
        if 'error' in genesys_contacts:
            return jsonify({"error": f"Failed to retrieve contacts from Genesys: {genesys_contacts['error']}"}), 400
        
        imported_contacts = []
        
        # Loop through each contact
        for genesys_contact in genesys_contacts.get('entities', []):
            # Convert to CRM format
            crm_contact = {
                "name": f"{genesys_contact.get('firstName', '')} {genesys_contact.get('lastName', '')}".strip(),
                "email": next((email.get('address') for email in genesys_contact.get('emails', []) if 'address' in email), ""),
                "phone": next((phone.get('number') for phone in genesys_contact.get('phoneNumbers', []) if 'number' in phone), ""),
                "notes": f"Imported from Genesys Cloud. Contact ID: {genesys_contact.get('id')}",
                "genesys_id": genesys_contact.get('id')
            }
            
            # Add to CRM
            new_contact = create_contact(crm_contact)
            imported_contacts.append(new_contact)
        
        return jsonify({
            "message": f"Successfully imported {len(imported_contacts)} contacts",
            "contacts": imported_contacts
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Create/update interaction record in CRM based on Genesys interaction
@app.route('/api/genesys/interactions/<interaction_id>/record', methods=['POST'])
@auth.login_required
def api_genesys_record_interaction(interaction_id):
    """Record a Genesys interaction in the CRM as a deal or note"""
    genesys = GenesysCloudIntegration()
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        # Get interaction details from Genesys
        interaction = genesys.get_interaction(interaction_id)
        
        if 'error' in interaction:
            return jsonify({"error": f"Failed to retrieve interaction: {interaction['error']}"}), 400
        
        # Get customer info if available
        customer_id = request.json.get('customer_id')
        
        # Create a deal record from this interaction
        deal_data = {
            "title": f"Interaction {interaction_id}",
            "description": f"Call recorded on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "status": "New",
            "value": 0,
            "customer_id": customer_id,
            "genesys_interaction_id": interaction_id
        }
        
        new_deal = create_deal(deal_data)
        return jsonify({"message": "Interaction recorded as deal", "deal": new_deal}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Screen Pop functionality for Genesys Cloud integration
@app.route('/api/genesys/screen-pop/lookup', methods=['POST'])
@auth.login_required
def api_genesys_screen_pop_lookup():
    """
    Screen Pop lookup endpoint - searches for a customer by phone number
    
    This endpoint is called when an inbound call is received in Genesys Cloud.
    It searches for a customer by phone number and returns the customer details
    if found. If no customer is found, it returns a 404 response.
    """
    genesys = GenesysCloudIntegration()
    data = request.json
    
    if not data or 'phone_number' not in data:
        return jsonify({"error": "Phone number is required"}), 400
    
    phone_number = data.get('phone_number')
    
    try:
        # Import the find_customer_by_phone function
        from data_manager import find_customer_by_phone
        
        # Look up customer by phone number
        customer = find_customer_by_phone(phone_number)
        
        if customer:
            # If customer found, return customer details
            return jsonify({
                "found": True,
                "customer": customer,
                "message": "Customer found"
            })
        else:
            # If no customer found, return not found status
            return jsonify({
                "found": False,
                "message": "No customer found with this phone number"
            }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/genesys/screen-pop/create-script', methods=['POST'])
@auth.login_required
def api_genesys_create_screen_pop_script():
    """
    Create a screen pop script for Genesys Cloud
    
    This endpoint creates an agent script in Genesys Cloud that can be used
    to display customer information or collect new customer information.
    """
    genesys = GenesysCloudIntegration()
    data = request.json
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        customer_id = data.get('customer_id')
        result = genesys.create_customer_screen_pop_script(customer_id)
        
        return jsonify({
            "message": "Screen pop script created successfully",
            "script": result
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/genesys/screen-pop/setup', methods=['POST'])
@auth.login_required
def api_genesys_setup_screen_pop():
    """
    Set up screen pop functionality in Genesys Cloud
    
    This endpoint configures the notification subscription for
    real-time call events in Genesys Cloud.
    """
    genesys = GenesysCloudIntegration()
    
    if not genesys.is_configured():
        return jsonify({"error": "Genesys Cloud integration not configured"}), 400
    
    try:
        # Set up notification channel for screen pop
        result = genesys.setup_screen_pop()
        
        return jsonify({
            "message": "Screen pop functionality configured successfully",
            "status": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/genesys/quick-add-customer', methods=['POST'])
@auth.login_required
def api_genesys_quick_add_customer():
    """
    Quickly add a new customer from Genesys Cloud
    
    This endpoint is designed to be called from a Genesys Cloud
    agent script to add a new customer to the CRM during a call.
    """
    data = request.json
    
    if not data:
        return jsonify({"error": "Customer data is required"}), 400
    
    # Ensure minimum required fields
    required_fields = ['name', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Field '{field}' is required"}), 400
    
    try:
        # Create the customer in the CRM
        new_customer = create_customer(data)
        
        # Return success response with the new customer data
        return jsonify({
            "message": "Customer created successfully",
            "customer": new_customer
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error"}), 500
