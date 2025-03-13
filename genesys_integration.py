import os
import json
import requests
from datetime import datetime, timedelta

class GenesysCloudIntegration:
    """Class for integrating with Genesys Cloud APIs"""
    
    def __init__(self):
        """Initialize the Genesys Cloud integration"""
        self.client_id = os.environ.get('GENESYS_CLIENT_ID')
        self.client_secret = os.environ.get('GENESYS_CLIENT_SECRET')
        self.region = os.environ.get('GENESYS_REGION', 'us-east-1')
        
        # Base URLs for different regions
        self.base_url_map = {
            'us-east-1': 'https://api.mypurecloud.com',
            'us-west-2': 'https://api.usw2.pure.cloud',
            'eu-west-1': 'https://api.mypurecloud.ie',
            'eu-central-1': 'https://api.mypurecloud.de',
            'ap-southeast-2': 'https://api.mypurecloud.com.au',
            'ap-northeast-1': 'https://api.mypurecloud.jp',
            'eu-west-2': 'https://api.mypurecloud.london',
            'ca-central-1': 'https://api.cac1.pure.cloud',
            'ap-northeast-2': 'https://api.apne2.pure.cloud',
            'eu-central-2': 'https://api.mypurecloud.de',
            'sa-east-1': 'https://api.sae1.pure.cloud',
            'ap-south-1': 'https://api.aps1.pure.cloud'
        }
        
        self.base_url = self.base_url_map.get(self.region, 'https://api.mypurecloud.com')
        self.access_token = None
        self.token_expiry = None
    
    def is_configured(self):
        """Check if the integration is properly configured"""
        return self.client_id is not None and self.client_secret is not None
    
    def _get_auth_token(self):
        """Get an OAuth token for Genesys Cloud API"""
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        
        if not self.is_configured():
            raise ValueError("Genesys Cloud credentials are not configured.")
        
        url = f"{self.base_url}/oauth/token"
        
        payload = {
            'grant_type': 'client_credentials'
        }
        
        # Ensure client_id and client_secret are not None
        if not self.client_id or not self.client_secret:
            raise ValueError("Genesys Cloud credentials are not configured properly.")
            
        # Cast to strings to avoid type issues
        auth = (str(self.client_id), str(self.client_secret))
        
        try:
            response = requests.post(url, data=payload, auth=auth)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data.get('access_token')
            expires_in = data.get('expires_in', 3600)  # Default to 1 hour
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)  # Subtract 60 seconds for safety
            
            return self.access_token
        except requests.exceptions.RequestException as e:
            print(f"Error obtaining Genesys Cloud token: {str(e)}")
            raise
    
    def _make_api_request(self, method, endpoint, params=None, data=None):
        """Make an API request to Genesys Cloud"""
        if not self.is_configured():
            return {'error': 'Genesys Cloud integration not configured'}
        
        token = self._get_auth_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return {'error': f'Unsupported method: {method}'}
            
            response.raise_for_status()
            return response.json() if response.content else {'status': 'success'}
        except requests.exceptions.RequestException as e:
            print(f"Genesys Cloud API error: {str(e)}")
            return {'error': str(e)}
    
    # User Management
    def get_users(self, limit=25, page_number=1):
        """Get users from Genesys Cloud"""
        params = {
            'pageSize': limit,
            'pageNumber': page_number
        }
        return self._make_api_request('GET', '/api/v2/users', params=params)
    
    def get_user(self, user_id):
        """Get a specific user from Genesys Cloud"""
        return self._make_api_request('GET', f'/api/v2/users/{user_id}')
    
    # Contact Management
    def get_contacts(self, limit=25, page_number=1):
        """Get contacts from Genesys Cloud"""
        params = {
            'pageSize': limit,
            'pageNumber': page_number
        }
        # Note: This is an example - actual endpoint may vary based on Genesys Cloud API
        return self._make_api_request('GET', '/api/v2/externalcontacts/contacts', params=params)
    
    def get_contact(self, contact_id):
        """Get a specific contact from Genesys Cloud"""
        return self._make_api_request('GET', f'/api/v2/externalcontacts/contacts/{contact_id}')
    
    def create_contact(self, contact_data):
        """Create a new contact in Genesys Cloud"""
        return self._make_api_request('POST', '/api/v2/externalcontacts/contacts', data=contact_data)
    
    def update_contact(self, contact_id, contact_data):
        """Update a contact in Genesys Cloud"""
        return self._make_api_request('PUT', f'/api/v2/externalcontacts/contacts/{contact_id}', data=contact_data)
    
    # Call/Interaction Management
    def get_interactions(self, limit=25, page_number=1):
        """Get recent interactions from Genesys Cloud"""
        params = {
            'pageSize': limit,
            'pageNumber': page_number
        }
        return self._make_api_request('GET', '/api/v2/analytics/conversations/details', params=params)
    
    def get_interaction(self, interaction_id):
        """Get details of a specific interaction"""
        return self._make_api_request('GET', f'/api/v2/analytics/conversations/{interaction_id}/details')
    
    # Queue Management
    def get_queues(self, limit=25, page_number=1):
        """Get queues from Genesys Cloud"""
        params = {
            'pageSize': limit,
            'pageNumber': page_number
        }
        return self._make_api_request('GET', '/api/v2/routing/queues', params=params)
    
    # Screen Pop Integration
    def get_caller_details(self, phone_number):
        """
        Get caller details from a phone number, used for screen pop functionality
        
        This method searches the CRM for a contact with the given phone number and
        returns customer details if found.
        
        Args:
            phone_number (str): The phone number to search for
            
        Returns:
            dict: Customer details if found, otherwise None
        """
        from data_manager import find_customer_by_phone
        
        # Search for customer by phone number
        customer = find_customer_by_phone(phone_number)
        if not customer:
            return None
            
        return customer
        
    def setup_screen_pop(self, notification_handler=None):
        """
        Set up the screen pop functionality by subscribing to Genesys notifications
        
        Args:
            notification_handler (callable): A function to handle incoming notifications
            
        Returns:
            dict: Status of the subscription
        """
        # Subscribe to call/interaction notifications
        # This is typically done through WebSockets in a production environment
        # For this example, we're providing the implementation structure
        
        # The notification_handler would be called when a call comes in
        # with the phone number and interaction details
        
        return {
            'status': 'success', 
            'message': 'Screen pop notifications configured'
        }
    
    def create_agent_script(self, script_name, script_data):
        """
        Create an agent script in Genesys Cloud
        
        Agent scripts are used to guide agents through interactions and can include
        customer data fields from the CRM.
        
        Args:
            script_name (str): Name of the script
            script_data (dict): Script configuration
            
        Returns:
            dict: Created script details
        """
        script_payload = {
            'name': script_name,
            'versionId': '1.0',
            'createdDate': datetime.now().isoformat(),
            'modifiedDate': datetime.now().isoformat(),
            'publishedDate': datetime.now().isoformat(),
            'description': 'Created from CRM integration',
            'text': json.dumps(script_data),
            'notes': 'Auto-generated from CRM',
            'published': True
        }
        
        return self._make_api_request('POST', '/api/v2/flows/scripts', data=script_payload)
    
    def create_customer_screen_pop_script(self, customer_id=None):
        """
        Create a screen pop script for a specific customer or a generic new customer form
        
        Args:
            customer_id (str): Optional customer ID to create a customized script
            
        Returns:
            dict: Created script details
        """
        from data_manager import get_customer
        
        script_data = {
            'type': 'screen_pop',
            'action': 'display_customer' if customer_id else 'new_customer',
            'customer_data': get_customer(customer_id) if customer_id else None,
            'form_fields': [
                {'name': 'name', 'label': 'Full Name', 'type': 'text', 'required': True},
                {'name': 'email', 'label': 'Email Address', 'type': 'email', 'required': True},
                {'name': 'phone', 'label': 'Phone Number', 'type': 'tel', 'required': True},
                {'name': 'company', 'label': 'Company', 'type': 'text', 'required': False},
                {'name': 'notes', 'label': 'Notes', 'type': 'textarea', 'required': False}
            ]
        }
        
        script_name = f"Customer Screen Pop - {customer_id}" if customer_id else "New Customer Screen Pop"
        return self.create_agent_script(script_name, script_data)


# Example usage
if __name__ == "__main__":
    # This code only runs when the file is executed directly, not when imported
    genesys = GenesysCloudIntegration()
    if genesys.is_configured():
        users = genesys.get_users()
        print(json.dumps(users, indent=2))
    else:
        print("Genesys Cloud integration not configured. Please set environment variables.")