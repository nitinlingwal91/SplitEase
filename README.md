# SplitEase

SplitEase is a modern, Django-based web application designed to simplify expense sharing and settlement management among groups of people. Whether it's roommates sharing bills, friends traveling together, or colleagues managing group expenses, SplitEase offers an intuitive and real-time solution to keep track of who owes what.

## Features

- User registration and authentication with email verification.
- Group creation and management with role-based access.
- Expense logging with flexible splitting methods (equal, itemized, percentage).
- Automatic balance and settlement calculation to minimize transactions.
- Real-time group chat powered by WebSockets.
- Budget tracking with alerts to keep spending in check.
- Multi-language support for global users.
- User profile management with optional information and photo.
- Secure password reset workflow via email.
- Responsive design including light and dark mode themes.

## Technology Stack

- Backend: Django 5.2, Django Channels
- Frontend: Bootstrap 5, JavaScript
- Database: SQLite (for development), PostgreSQL support for production
- Real-time Communication: WebSockets using Django Channels
- Deployment-ready with CI/CD support on platforms like Render.com

## Installation and Setup

1. Clone the repository:
https://github.com/nitinlingwal91/SplitEase.git
 
2. Create a virtual environment and activate it:
python -m venv .venv
# On Windows use 
.venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Setup environment variables by copying `.env.example` to `.env` and modifying it.

5. Run migrations:
   python manage.py migrate


6. Run the development server:
   python manage.py runserver

## Usage

- Register a new user or log in.
- Create groups and add members.
- Log expenses and view settlements.
- Chat in real-time with group members.
- Track budgets with alerts.

## Contributing

Contributions are welcome! Please fork the project and create pull requests.

## License

This project is licensed under the MIT License.






