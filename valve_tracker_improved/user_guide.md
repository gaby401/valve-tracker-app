# Heart Valve Tracker - User Guide

## Introduction

The Heart Valve Tracker is a web application designed for Edwards Lifesciences lab to track and manage heart valve specimens throughout the testing lifecycle. This upgraded version includes user authentication, advanced search capabilities, visual indicators, result previews, reporting features, and more.

## Getting Started

### Installation

1. Extract the `valve_tracker_improved.zip` file to your desired location
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```
   python models.py
   ```
4. Start the application:
   ```
   python app.py
   ```
5. Access the application in your web browser at `http://localhost:5000`

### Default Login Credentials

- **Admin User**: 
  - Username: admin
  - Password: admin123
  
- **Technician User**:
  - Username: technician
  - Password: tech123

*Note: Please change these default passwords after first login for security purposes.*

## Features Overview

### User Management

- **User Roles**: The system supports two user roles:
  - **Admin**: Full access to all features, including user management and deletion capabilities
  - **Technician**: Access to specimen management, testing, and reporting features

- **User Profile**: View your activity history and change your password

### Specimen Management

- **Add Specimens**: Create new valve specimens with unique IDs, types, and statuses
- **Edit Specimens**: Update specimen information and status
- **Delete Specimens**: Remove specimens from the system (admin only)
- **Search & Filter**: Find specimens by ID, name, type, or status
- **Sort**: Sort specimens by any column to organize your data

### Test Management

- **Assign Tests**: Add different test types to specimens
- **Track Progress**: Update test status (Pending, In Progress, Completed, Cancelled)
- **Due Dates**: Set and track test due dates

### Result Management

- **Upload Results**: Attach PDF documents, images, or data files to specimens
- **Preview Results**: View uploaded files directly in the application
- **Download Results**: Access original files when needed

### Reporting

- **Generate Reports**: Create various report types:
  - Status Summary: Count of specimens by status
  - Type Summary: Count of specimens by valve type
  - Detailed Report: Comprehensive specimen information
  
- **Export Formats**: Download reports in CSV or PDF format
- **Data Visualization**: View charts and graphs of specimen data

### Security Features

- **Secure Authentication**: Password hashing and protected routes
- **Action Logging**: Track all user actions for audit purposes
- **File Upload Protection**: Validation of file types and sizes

## User Interface Guide

### Dashboard

The dashboard provides an overview of your specimen data, including:
- Total specimens count
- Specimens by status (In Testing, Passed, Failed)
- Recent specimens
- Recent activity log

### Specimen List

The specimen list shows all valve specimens with:
- Color-coded status indicators
- Quick access to details, edit, and delete functions
- Search and filter capabilities

### Specimen Details

The specimen details page includes:
- Comprehensive specimen information
- Test assignment and status tracking
- Result file uploads and previews
- Edit and delete options

### Reports

The reports page allows you to:
- Select report type and parameters
- Choose export format (CSV or PDF)
- View data visualizations

## Best Practices

1. **Regular Backups**: Export important data regularly using the reporting features
2. **Consistent Naming**: Use consistent naming conventions for valve IDs and types
3. **Complete Documentation**: Add detailed notes to specimens and test results
4. **Regular Updates**: Keep the application updated with the latest features and security patches

## Troubleshooting

- **Login Issues**: If you cannot log in, contact your administrator to reset your password
- **Missing Files**: Ensure the uploads directory has proper write permissions
- **Database Errors**: If database errors occur, try reinitializing the database with `python models.py`

## Support

For additional support or feature requests, please contact your system administrator or the development team.

---

© 2025 Edwards Lifesciences Lab - Heart Valve Tracker v2.0
