# Workplace Absence Detection System

## Description
This project is an absence management system developed as part of a Final Year Project (PFA) to digitize absence management within companies. The system aims to simplify attendance tracking, strengthen employee autonomy, and optimize human resources management.

## Development Team
- **IKTACHE CHOUAIB**

## Problem Statement
*"How to digitize absence management within a company to simplify attendance tracking, strengthen employee autonomy, and optimize human resources management?"*

## Key Features

### Functional Requirements
- **Absence Management**: Recording and tracking employee absences
- **Authentication and Role System**: Secure access management based on user profiles
- **Adaptive Dashboards**: Customized interfaces according to user roles
- **Report Generation**: Automatic creation of attendance and absence reports

### Non-Functional Requirements
- **Security**: Protection of sensitive data
- **Performance**: Optimized system for smooth usage
- **Traceability**: Complete history of actions and modifications
- **Scalability**: Architecture allowing future extensions

## Technologies Used

### Backend
- **Django**: Python web framework
- **MySQL**: Database (via XAMPP)
- **REST API**: Communication between frontend and backend

### Frontend
- **HTML5**: Web page structure
- **CSS3**: Styling and formatting
- **JavaScript**: Client-side interactions

### Development Tools
- **XAMPP**: Local development environment
- **MySQL**: Database management system

## Architecture
The project follows Django's **MVT (Model-View-Template)** architecture:
- **Model**: Data management and business logic
- **View**: Request processing and control logic
- **Template**: Presentation and user interface

## Installation

### Prerequisites
- Python 3.x
- XAMPP (for MySQL)
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/absence-detector.git
   cd absence-detector
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**
   - Start XAMPP and activate MySQL
   - Create a database named `absence_detector`
   - Configure connection settings in `settings.py`

5. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

## Usage

1. Access the application via `http://localhost:8000`
2. Log in with the created credentials
3. Navigate according to your role (Administrator, Manager, Employee)
4. Manage absences through the dedicated interface
5. View reports and dashboards

## Project Structure
```
absence-detector/
├── manage.py
├── requirements.txt
├── absence_detector/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── authentication/
│   ├── absences/
│   ├── reports/
│   └── dashboard/
├── templates/
├── static/
└── media/
```

## System Design

The project includes:
- **Use Case Diagrams**: Definition of user-system interactions
- **Sequence Diagrams**: Business process flows
- **Class Diagram**: Data structure and relationships

## Features Overview

### For Employees
- Submit absence requests
- View personal absence history
- Check absence balance
- Receive notifications

### For Managers
- Approve/reject absence requests
- View team absence reports
- Monitor attendance patterns
- Generate departmental reports

### For Administrators
- Manage user accounts and roles
- Configure absence policies
- Access system-wide reports
- Monitor system performance

## API Endpoints

The system provides REST API endpoints for:
- User authentication
- Absence CRUD operations
- Report generation
- Dashboard data

## Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## Testing

Run tests using:
```bash
python manage.py test
```

## Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure production database
3. Set up static file serving
4. Configure web server (Apache/Nginx)

## Screenshots

*Add screenshots of your application here*

## License

This project is developed in an academic context for the 2024-2025 academic year.

## Acknowledgments

- Mrs. ATIGUI for project supervision
- The academic institution for providing the framework
- Django community for excellent documentation

## Contact

- **IKTACHE CHOUAIB** - [email@example.com]
- **ZAKI RIM** - [email@example.com]

## Project Status

✅ **Completed Features:**
- User authentication system
- Absence request management
- Dashboard interfaces
- Report generation

🔄 **Future Enhancements:**
- Mobile application
- Email notifications
- Advanced analytics
- Integration with HR systems

---
*Final Year Project - Workplace Absence Detection System*
