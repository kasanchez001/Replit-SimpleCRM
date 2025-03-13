# Simple CRM

A lightweight Customer Relationship Management (CRM) tool with a Flask backend and Vanilla JavaScript frontend that runs locally without requiring a traditional database.

## Features

- **User Authentication**: Secure login and registration system
- **Customer Management**: Create, view, edit, and delete customer records
- **Contact Tracking**: Manage contacts associated with customers
- **Deal Monitoring**: Track deals with status, amount, and expected close dates
- **Local Data Storage**: JSON-based file storage for easy portability
- **Data Backup**: Built-in functionality to create backups of all data
- **API Documentation**: Comprehensive API documentation for integration

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: Vanilla JavaScript, Bootstrap 5 (Dark Theme)
- **Database**: File-based JSON storage
- **Authentication**: Flask-HTTPAuth with secure password hashing

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/kasanchez001/Replit-SimpleCRM.git
   cd Replit-SimpleCRM
   ```

2. Set up a virtual environment (recommended):
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python main.py
   ```

5. Access the application in your web browser:
   ```
   http://localhost:5000
   ```

## Project Structure

```
project/
├── data/               # Data storage directory
│   ├── backup/         # Backup storage
│   ├── contacts.json   # Contact data
│   ├── customers.json  # Customer data
│   ├── deals.json      # Deal data
│   └── users.json      # User account data
├── static/             # Static assets
│   ├── css/            # CSS styles
│   └── js/             # JavaScript files
├── templates/          # HTML templates
├── app.py              # Main application routes
├── auth.py             # Authentication system
├── data_manager.py     # Data access layer
└── main.py             # Application entry point
```

## Usage

1. Register a new account or log in with existing credentials
2. Navigate between Customers, Contacts, and Deals sections
3. Use the search and filter functionality to find specific records
4. Create, edit, or delete records as needed
5. Access the API documentation for integration options
6. Use the backup button to create data snapshots

## Security

- Passwords are securely hashed using scrypt
- Authentication is handled via HTTP Basic Auth for API access
- All data is stored locally on your machine for privacy

## License

This project is open source and available under the [MIT License](LICENSE).