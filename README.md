# Service Management Portal

A Flask-based web application for connecting customers with service professionals, featuring role-based access control, service management, and analytics.

## Features

- **Multi-role System**:
  - Admin: User management and system analytics
  - Professionals: Service portfolio management and performance metrics
  - Customers: Service discovery and booking system

- **Core Functionality**:
  - Service request management system
  - Professional rating and review system
  - Interactive data visualizations
  - Payment system integration
  - Search functionality with filters

- **Security**:
  - Secure authentication system
  - Role-based access control
  - Session management

## Key Achievements

- Implemented role-based access control with Flask-Login
- Developed RESTful API endpoints for data interactions
- Created dynamic data visualizations using Chart.js
- Integrated WTForms for secure form handling
- Designed responsive UI with Bootstrap 5

## Technologies Used

**Backend**:
- Python 3.9
- Flask 2.0
- SQLAlchemy (ORM)
- WTForms
- Flask-Login
- Flask-SQLAlchemy

**Frontend**:
- HTML5
- CSS3
- Chart.js (Data visualization)
- Bootstrap 5

**Database**:
- SQLite (Development)
- PostgreSQL-ready architecture

## Project Structure

```
service-portal/
├── instance/               # Database instance
├── static/                 # Static assets
│   ├── charts/             # Generated data visualizations
│   └── *.css               # Style sheets
├── templates/              # Jinja2 templates
│   ├── admin_*.html        # Admin interface views
│   ├── professional_*.html # Professional user views
│   ├── customer_*.html     # Customer user views
│   └── base*.html          # Template inheritance base
├── app.py                  # Flask application factory
├── models.py               # SQLAlchemy models
├── routes.py               # Application routes
└── requirements.txt        # Python dependencies
```

## Installation

1. Clone repository:
   ```bash
   git clone https://github.com/yourusername/service-portal.git
   cd service-portal
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   set FLASK_APP=run.py
   set FLASK_ENV=development
   ```

5. Initialize database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run application:
   ```bash
   python run.py
   ```

## Configuration

Create `.env` file with:
```ini
SECRET_KEY=your-secret-key-here
DATABASE_URI=sqlite:///instance/database.sqlite3
```

## Screenshots

![Admin Dashboard](/static/charts/service_requests.png "Admin Analytics")
![Professional Profile](/static/charts/professional_ratings.png "Professional Dashboard")
![Service Search](/templates/professional_search.html "Search Interface")

## License
MIT License
