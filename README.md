# SplitEase

SplitEase is a modern, Django-based web application designed to simplify expense sharing and settlement management among groups of people. Whether it's roommates sharing bills, friends traveling together, or colleagues managing group expenses, SplitEase offers an intuitive and real-time solution to keep track of who owes what.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

- User registration and authentication
- Group creation and management with role-based access.
- Expense logging with flexible splitting methods (equal, itemized, percentage).
- Automatic balance and settlement calculation to minimize transactions.
- Real-time group chat powered by WebSockets.
- Budget tracking with alerts to keep spending in check.
- User profile management with optional information and photo.
- Secure password reset workflow via email.
- Responsive design including light and dark mode themes.
---

## 🛠 Technology Stack

### Backend
- **Django 5.2** - [Download](https://www.djangoproject.com/download/)
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Django Channels 4.0.0** - [Documentation](https://channels.readthedocs.io/)
- **Daphne 4.0.0** - ASGI server for WebSocket support
- **Pillow 10.0.0** - Image processing

### Frontend
- **Bootstrap 5** - [Download](https://getbootstrap.com/docs/5.0/getting-started/download/)
- **Bootstrap Icons** - [Browse Icons](https://icons.getbootstrap.com/)
- **HTML5 & CSS3**
- **Vanilla JavaScript with AJAX**

### Database
- **SQLite** - Development (included)
- **PostgreSQL** - [Download](https://www.postgresql.org/download/) - Production ready

### Additional Libraries
- **Channels-Redis 4.1.0** - Redis backend for channels
- **python-dotenv 1.0.0** - Environment variables management
- **django-cors-headers 4.0.0** - CORS support
- **django-filter 23.2** - Query filtering
---

## [View all project images]
![Alt text](media/images)
(media/images/Screenshot(98))
---
(media/images/Screenshot(97))

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
   - Verify installation: `python --version`

2. **Git** - [Download Git](https://git-scm.com/downloads)
   - Verify installation: `git --version`

3. **pip** (Python package manager) - Usually comes with Python
   - Verify installation: `pip --version`

4. **(Optional) PostgreSQL** - [Download PostgreSQL](https://www.postgresql.org/download/)
   - For production use only
   - Development uses SQLite by default

5. **(Optional) Visual Studio Code** - [Download VS Code](https://code.visualstudio.com/download)
   - Recommended code editor

---

## 💻 Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/nitinlingwal91/SplitEase.git
cd SplitEase
```

### Step 2: Create a Virtual Environment

Create an isolated Python environment for the project:

```bash
# On Windows
python -m venv .venv
.venv\Scripts\activate

# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

**Note:** After activation, your terminal will show `(.venv)` prefix.

### Step 3: Install Dependencies

Install all required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Expected packages:**
- Django 5.2.7
- Channels 4.0.0
- Pillow 10.0.0
- python-dotenv 1.0.0
- And more (see requirements.txt)

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example
cp .env.example .env

# Or manually create and add:
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 5: Run Database Migrations

Set up the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser Account

Create an admin account to access Django admin panel:

```bash
python manage.py createsuperuser
```

Follow prompts to enter username, email, and password.

### Step 7: Run the Development Server

Start the local development server:

```bash
python manage.py runserver
```

**Access the application:**
- Main app: `http://127.0.0.1:8000/`
- Admin panel: `http://127.0.0.1:8000/admin/`
- Login with superuser credentials created in Step 6

---

## 📁 Project Structure

```
SplitEase/
├── spliteaseproject/        # Django project settings
│   ├── settings.py          # Configuration
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI config
│   └── asgi.py              # ASGI config (WebSocket)
├── users/                   # User management app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── groups/                  # Group management app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── expenses/                # Expense management app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── settlements/             # Settlement calculation app
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── chat/                    # Real-time chat app
│   ├── models.py
│   ├── views.py
│   ├── consumers.py         # WebSocket consumers
│   └── urls.py
├── budgets/                 # Budget management app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── templates/               # HTML templates
│   ├── base.html
│   ├── users/
│   ├── groups/
│   ├── expenses/
│   └── ...
├── static/                  # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
├── media/                   # User uploaded files
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore file
└── README.md               # This file
```

---

## 🚀 Usage

### First Time Users

1. **Register**
   - Go to `/users/register/`
   - Fill in email, password, and name
   - Verify email if required

2. **Create a Group**
   - Click "Create Group" on dashboard
   - Enter group name, description, currency

3. **Add Members**
   - Go to group settings
   - Click "Add Member"
   - Enter member email

4. **Add Expenses**
   - Click "Add Expense" in group
   - Enter description, amount, payer
   - Choose split method (equal/itemized/percentage)

5. **View Settlements**
   - See balances and who owes whom
   - Confirm settlement when paid

6. **Group Chat**
   - Click "Group Chat" to access real-time messaging
   - Chat with other group members

7. **Budget Management**
   - Create budgets for spending limits
   - Set category-wise budgets
   - Receive alerts when limits approached
---

## 📜 License

This project is licensed under the **MIT License** -
---

## 📞 Contact & Support

For questions, feedback, or support:

- **GitHub Issues** - [Report Issue](https://github.com/nitinlingwal91/SplitEase/issues)
- **Email** - nitinlingwal91@gmail.com
- **GitHub Discussions** - [Start Discussion](https://github.com/nitinlingwal91/SplitEase/discussions)
---

## 📚 Useful Resources

- [Django Official Documentation](https://docs.djangoproject.com/)
- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [Python Official Documentation](https://docs.python.org/3/)
- [Git Documentation](https://git-scm.com/doc)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 🎉 Acknowledgments

- Django community for excellent framework
- Bootstrap team for UI components
- Contributors and users for feedback
---


© 2025 SplitEase. All rights reserved.











