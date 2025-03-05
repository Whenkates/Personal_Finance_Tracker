# Personal_Finance_Tracker
A web-based personal finance tracking application built with Python, Streamlit, and PostgreSQL. Users can register, log in, track expenses, set budgets, and receive email notifications when budget limits are exceeded.<br>

**Features:**
- User Management: Register and log in with an email and name.
- Expense Tracking: Add transactions with categories, amounts, and descriptions.
- Budget Management: Set budget limits per category and view spending status.
- Email Notifications: Receive warnings via email when spending exceeds budget limits.
- Web Interface: Interactive dashboard powered by Streamlit.

**Tech Stack**
- Frontend: Streamlit
- Backend: Python, PostgreSQL
- Database: PostgreSQL for persistent storage
- Email: SMTP integration (Gmail)
- Dependencies: streamlit, psycopg2-binary, pandas, smtplib

**Prerequisites**
- Python 3.8+
- PostgreSQL installed and running
- Gmail account for email notifications (with App Password if 2FA is enabled)

**Database Schema**
- users: (user_id SERIAL PRIMARY KEY, name TEXT, email TEXT UNIQUE)
- budgets: (u_id INTEGER, category TEXT, budget_limit REAL, FOREIGN KEY(u_id) REFERENCES users(user_id))
- transactions: (trans_id SERIAL PRIMARY KEY, user_id INTEGER, category TEXT, amount REAL, date TEXT, description TEXT, FOREIGN KEY(user_id) REFERENCES users(user_id))

**Usage**
1. Register: Create an account with your name and email.
2. Login: Use your email to log in.
3. Dashboard: View your transactions and budget status.
4. Add Transaction: Record expenses with category, amount, and description.
5. Set Budget: Define spending limits per category.
6. Receive email alerts when budgets are exceeded.
