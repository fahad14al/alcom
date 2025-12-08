Alcom - E-commerce API
Alcom is a robust E-commerce REST API built with Python and the Django framework. It provides a complete backend solution for managing an online store, including user authentication, product catalogs, shopping carts, order processing, and analytics.

🚀 Features
User Accounts: Registration, login, and profile management.

Product Management: Create, update, and categorize products.

Shopping Cart: Add/remove items and calculate totals.

Order System: Process customer orders and track history.

Payments: Integration for handling secure transactions.

Reviews & Ratings: Customer feedback system for products.

Analytics: Data tracking for sales and user behavior.

🛠️ Tech Stack
Backend: Python, Django, Django REST Framework (DRF)

Database: SQLite (default) or PostgreSQL/MySQL

Authentication: JWT or Token-based authentication

📁 Project Structure
Plaintext

alcom/
├── accounts/         # User management & authentication
├── products/         # Product catalog and categories
├── cart/             # Shopping cart logic
├── orders/           # Order placement and tracking
├── payments/         # Payment gateway integration
├── reviews/          # Product reviews and ratings
├── analytics/        # Business intelligence and tracking
├── alcom_project/    # Main project settings and configuration
└── manage.py         # Django CLI tool
⚙️ Installation & Setup
1. Clone the Repository
Bash

git clone https://github.com/fahad14al/alcom.git
cd alcom
2. Create a Virtual Environment
Bash

python -m venv venv
# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate
3. Install Dependencies
Bash

pip install -r requirements.txt
4. Database Migrations
Bash

python manage.py makemigrations
python manage.py migrate
5. Create a Superuser (Admin)
Bash

python manage.py createsuperuser
6. Run the Server
Bash

python manage.py runserver
The API will be available at http://127.0.0.1:8000/.

🧪 Running Tests
To run the automated tests, use:

Bash

python manage.py test
