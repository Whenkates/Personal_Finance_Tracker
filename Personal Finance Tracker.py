# Import necessary libraries
import streamlit as st
import psycopg2
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Database setup
def init_db():
    connection = psycopg2.connect(
        dbname ='Finance_tracker',
        user = 'postgres',
        password = 'So@ph$ie%',
        host = 'localhost',
        port = '5432'
    )
    cursor = connection.cursor()

    # Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                    (user_id SERIAL PRIMARY KEY,
                    name TEXT,
                    email TEXT UNIQUE)''')

    #Budgets Tabke
    cursor.execute('''CREATE TABLE IF NOT EXISTS budgets
                    (u_id INTEGER,
                    category TEXT,
                    budget_limit REAL,
                    FOREIGN KEY(u_id) REFERENCES users(user_id))''')

    # Transaction Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                    (trans_id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    category TEXT,
                    amount REAL,
                    date TEXT,
                    description TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    connection.commit()
    connection.close()

#DB Connection
def get_connection_to_db():
        return psycopg2.connect(
            dbname = 'Finance_tracker',
            user = 'postgres',
            password = 'So@ph$ie%',
            host = 'localhost',
            port = 5432
            )

# Email Notification if budget exceeds
def send_email_notification(email,category,amount,budget_limit):
    sender = "venkateshkatta@gmail.com"
    password = "***********"
    msg = MIMEText(f"Warning: Your {category} spending ({amount}) has exceeded your budget limit ({budget_limit})!")
    msg['Subject'] = 'Budget Exceed Warning'
    msg['From'] = sender
    msg['To'] = email
    try:
        with smtplib.SMTP('smtp.gmail.com',587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
    except Exception as e:
        st.error(f"Email sending failed: {e}")

# Check budget limit and send warning if exceeded
def check_budget(user_id,category,amount):
    connection = get_connection_to_db()
    conn = connection.cursor()
    conn.execute(
        "SELECT budget_limit FROM budgets WHERE u_id = %s AND category = %s",(user_id,category))
    budget = conn.fetchone()
    conn.execute(
        "SELECT SUM(amount) FROM transaction WHERE user_id=%s AND category=%s",(user_id,category))
    total_spent = conn.fetchone()[0] or 0
    if budget and total_spent + amount>budget[0]:
        conn.execute("SELECT email FROM users WHERE user_id = %s",(user_id,))
        email = conn.fetchone()[0]
        send_email_warning(email, category, total_spent+amount,budget[0])
    connection.close()

#Streamlit App
def main():
    init_db()
    st.title("Personal Finance Tracker")
    #Sidebar
    menu = ['Login','Register','Dashboard','Add Transaction','Set Budget']
    choice = st.sidebar.selectbox("Menu",menu)
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id=None
        
    if choice == 'Register':
        with st.form('register_form'):
            name = st.text_input("Name")
            email = st.text_input("Email")
            submit = st.form_submit_button('Register')
            if submit:
                connection = get_connection_to_db()
                conn = connection.cursor()
                try:
                    conn.execute("INERT INTO users (name,email) VALUES (%s,%s)",(name,email))
                    connection.commit()
                    st.success("Registered succesfully! Please login.")
                except psycopg2.IntegrityError:
                    st.error("Emai' already exists!")
                finally:
                    connection.close()
                    
    elif choice == "Login":
        with st.form("login_form"):
            email = st.text_input("Email")
            submit = st.form_submit_button("Login")
            
            if submit:
                conn = get_connection_to_db()
                c = conn.cursor()
                c.execute("SELECT user_id FROM users WHERE email=%s", (email,))
                user = c.fetchone()
                conn.close()
                if user:
                    st.session_state.user_id = user[0]
                    st.success("Logged in successfully!")
                else:
                    st.error("User not found!")
    
    elif st.session_state.user_id:
        user_id = st.session_state.user_id
        conn = get_db_connection()
        c = conn.cursor()
        
        if choice == "Dashboard":
            # Show transactions
            c.execute("SELECT category, amount, date, description FROM transactions WHERE user_id=%s", (user_id,))
            transactions = pd.DataFrame(c.fetchall(), columns=['Category', 'Amount', 'Date', 'Description'])
            st.dataframe(transactions)
            
            # Show budget status
            c.execute("""
                SELECT b.category, b.budget_limit, SUM(t.amount) 
                FROM budgets b 
                LEFT JOIN transactions t ON b.u_id = t.user_id AND b.category = t.category 
                WHERE b.u_id=%s 
                GROUP BY b.category, b.budget_limit
            """, (user_id,))
            budget_data = pd.DataFrame(c.fetchall(), columns=['Category', 'Budget Limit', 'Spent'])
            st.dataframe(budget_data)
        
        elif choice == "Add Transaction":
            with st.form("transaction_form"):
                category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Other"])
                amount = st.number_input("Amount", min_value=0.0)
                desc = st.text_input("Description")
                submit = st.form_submit_button("Add")
                
                if submit:
                    date = datetime.now().strftime("%Y-%m-%d")
                    c.execute("INSERT INTO transactions (user_id, category, amount, date, description) VALUES (%s, %s, %s, %s, %s)",
                            (user_id, category, amount, date, desc))
                    conn.commit()
                    check_budget(user_id, category, amount)
                    st.success("Transaction added!")
        
        elif choice == "Set Budget":
            with st.form("budget_form"):
                category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Other"])
                limit = st.number_input("Budget Limit", min_value=0.0)
                submit = st.form_submit_button("Set Budget")
                
                if submit:
                    c.execute("INSERT INTO budgets (u_id, category, budget_limit) VALUES (%s, %s, %s) "
                            "ON CONFLICT (user_id, category) DO UPDATE SET budget_limit = EXCLUDED.budget_limit",
                            (user_id, category, limit))
                    conn.commit()
                    st.success("Budget set!")
        
        conn.close()

if __name__ == '__main__':
    main()              







































        
