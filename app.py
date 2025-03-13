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

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error"}), 500
