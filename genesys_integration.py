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


# Example usage
if __name__ == "__main__":
    # This code only runs when the file is executed directly, not when imported
    genesys = GenesysCloudIntegration()
    if genesys.is_configured():
        users = genesys.get_users()
        print(json.dumps(users, indent=2))
    else:
        print("Genesys Cloud integration not configured. Please set environment variables.")