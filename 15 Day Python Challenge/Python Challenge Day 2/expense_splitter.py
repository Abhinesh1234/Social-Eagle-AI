import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import qrcode
from io import BytesIO
import base64
from collections import defaultdict
import math

# Page configuration
st.set_page_config(
    page_title="💰 Smart Expense Splitter",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .person-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .payment-button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'people' not in st.session_state:
    st.session_state.people = []
if 'split_history' not in st.session_state:
    st.session_state.split_history = []

def generate_qr_code(payment_info):
    """Generate QR code for payment information"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(payment_info)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def calculate_advanced_split(expenses, people, split_method="equal"):
    """Advanced calculation with different split methods"""
    results = {}
    
    if split_method == "equal":
        # Equal split
        total = sum([exp['amount'] for exp in expenses])
        per_person = total / len(people)
        
        for person in people:
            paid = sum([exp['amount'] for exp in expenses if exp['payer'] == person['name']])
            balance = paid - per_person
            results[person['name']] = {
                'paid': paid,
                'should_pay': per_person,
                'balance': balance,
                'owes': max(0, -balance),
                'gets_back': max(0, balance)
            }
    
    elif split_method == "proportional":
        # Split based on income/capacity
        total_amount = sum([exp['amount'] for exp in expenses])
        total_capacity = sum([person['capacity'] for person in people])
        
        for person in people:
            proportion = person['capacity'] / total_capacity
            should_pay = total_amount * proportion
            paid = sum([exp['amount'] for exp in expenses if exp['payer'] == person['name']])
            balance = paid - should_pay
            
            results[person['name']] = {
                'paid': paid,
                'should_pay': should_pay,
                'balance': balance,
                'owes': max(0, -balance),
                'gets_back': max(0, balance),
                'proportion': proportion * 100
            }
    
    elif split_method == "custom":
        # Custom percentages
        total_amount = sum([exp['amount'] for exp in expenses])
        
        for person in people:
            should_pay = total_amount * (person['percentage'] / 100)
            paid = sum([exp['amount'] for exp in expenses if exp['payer'] == person['name']])
            balance = paid - should_pay
            
            results[person['name']] = {
                'paid': paid,
                'should_pay': should_pay,
                'balance': balance,
                'owes': max(0, -balance),
                'gets_back': max(0, balance),
                'percentage': person['percentage']
            }
    
    return results

def optimize_payments(results):
    """Optimize payment settlements to minimize transactions"""
    debtors = []
    creditors = []
    
    for name, data in results.items():
        if data['balance'] < -0.01:  # Owes money
            debtors.append({'name': name, 'amount': -data['balance']})
        elif data['balance'] > 0.01:  # Gets money back
            creditors.append({'name': name, 'amount': data['balance']})
    
    # Sort debtors and creditors by amount
    debtors.sort(key=lambda x: x['amount'], reverse=True)
    creditors.sort(key=lambda x: x['amount'], reverse=True)
    
    transactions = []
    i, j = 0, 0
    
    while i < len(debtors) and j < len(creditors):
        debt = debtors[i]['amount']
        credit = creditors[j]['amount']
        
        if debt < credit:
            # Debtor pays full debt to creditor
            transactions.append({
                'from': debtors[i]['name'],
                'to': creditors[j]['name'],
                'amount': debt
            })
            creditors[j]['amount'] -= debt
            i += 1
        elif debt > credit:
            # Debtor pays partial debt to creditor
            transactions.append({
                'from': debtors[i]['name'],
                'to': creditors[j]['name'],
                'amount': credit
            })
            debtors[i]['amount'] -= credit
            j += 1
        else:
            # Exact match
            transactions.append({
                'from': debtors[i]['name'],
                'to': creditors[j]['name'],
                'amount': debt
            })
            i += 1
            j += 1
    
    return transactions

# Header
st.markdown("""
<div class="main-header">
    <h1>💰 Smart Expense Splitter Pro</h1>
    <p>Advanced expense splitting with payment integration & analytics</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("🧭 Navigation")
app_mode = st.sidebar.selectbox(
    "Choose Mode",
    ["🏠 Quick Split", "⚙️ Advanced Split", "📊 Analytics", "💳 Payment Hub", "📈 Split History"]
)

# Quick Split Mode
if app_mode == "🏠 Quick Split":
    st.header("🚀 Quick Split")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💸 Expense Details")
        total_amount = st.number_input("Total Amount (Rs.)", min_value=0.01, value=100.0, step=0.01)
        num_people = st.number_input("Number of People", min_value=2, value=3, step=1)
        
        # Quick names input
        st.write("**People Names:**")
        people_names = []
        for i in range(int(num_people)):
            name = st.text_input(f"Person {i+1}", value=f"Person {i+1}", key=f"quick_person_{i}")
            people_names.append(name)
    
    with col2:
        st.subheader("🧮 Split Results")
        per_person = total_amount / num_people
        
        st.metric("Amount per person", f"Rs.{per_person:.2f}")
        
        # Display split
        for name in people_names:
            st.info(f"**{name}** pays: Rs.{per_person:.2f}")
        
        # Save to history
        if st.button("💾 Save Split"):
            split_data = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_amount': total_amount,
                'people': people_names,
                'per_person': per_person,
                'method': 'Equal Split'
            }
            st.session_state.split_history.append(split_data)
            st.success("Split saved to history!")

# Advanced Split Mode
elif app_mode == "⚙️ Advanced Split":
    st.header("🎯 Advanced Split")
    
    # Split method selection
    split_method = st.selectbox(
        "Split Method",
        ["equal", "proportional", "custom"],
        format_func=lambda x: {
            "equal": "💯 Equal Split",
            "proportional": "⚖️ Proportional (by capacity)",
            "custom": "🎨 Custom Percentages"
        }[x]
    )
    
    # People management
    st.subheader("👥 Manage People")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_person_name = st.text_input("Add Person Name")
    
    with col2:
        if st.button("➕ Add Person"):
            if new_person_name and new_person_name not in [p['name'] for p in st.session_state.people]:
                person_data = {'name': new_person_name}
                
                if split_method == "proportional":
                    person_data['capacity'] = 1.0
                elif split_method == "custom":
                    person_data['percentage'] = 0.0
                
                st.session_state.people.append(person_data)
                st.success(f"Added {new_person_name}")
    
    # Display and edit people
    if st.session_state.people:
        st.write("**Current People:**")
        
        people_to_remove = []
        for i, person in enumerate(st.session_state.people):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                st.write(f"**{person['name']}**")
            
            with col2:
                if split_method == "proportional":
                    capacity = st.number_input(
                        f"Capacity", 
                        min_value=0.1, 
                        value=person.get('capacity', 1.0),
                        step=0.1,
                        key=f"capacity_{i}"
                    )
                    st.session_state.people[i]['capacity'] = capacity
                elif split_method == "custom":
                    percentage = st.number_input(
                        f"Percentage", 
                        min_value=0.0, 
                        max_value=100.0,
                        value=person.get('percentage', 0.0),
                        step=1.0,
                        key=f"percentage_{i}"
                    )
                    st.session_state.people[i]['percentage'] = percentage
            
            with col3:
                if split_method == "proportional":
                    st.caption("Higher = pays more")
                elif split_method == "custom":
                    st.caption("% of total")
            
            with col4:
                if st.button("🗑️", key=f"remove_{i}"):
                    people_to_remove.append(i)
        
        # Remove people
        for idx in reversed(people_to_remove):
            st.session_state.people.pop(idx)
    
    # Expense management
    st.subheader("💰 Manage Expenses")
    
    if st.session_state.people:
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            expense_desc = st.text_input("Expense Description")
        
        with col2:
            expense_amount = st.number_input("Amount (Rs.)", min_value=0.01, value=10.0, step=0.01)
        
        with col3:
            payer = st.selectbox("Who Paid?", [p['name'] for p in st.session_state.people])
        
        with col4:
            if st.button("➕ Add Expense"):
                if expense_desc:
                    expense = {
                        'description': expense_desc,
                        'amount': expense_amount,
                        'payer': payer,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.expenses.append(expense)
                    st.success("Expense added!")
        
        # Display expenses
        if st.session_state.expenses:
            st.write("**Current Expenses:**")
            expenses_df = pd.DataFrame(st.session_state.expenses)
            st.dataframe(expenses_df, use_container_width=True)
            
            # Calculate and display results
            if st.button("🧮 Calculate Split"):
                results = calculate_advanced_split(
                    st.session_state.expenses, 
                    st.session_state.people, 
                    split_method
                )
                
                st.subheader("📊 Split Results")
                
                # Display individual results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Individual Breakdown:**")
                    for name, data in results.items():
                        with st.expander(f"{name} - Balance: Rs.{data['balance']:.2f}"):
                            st.metric("Paid", f"Rs.{data['paid']:.2f}")
                            st.metric("Should Pay", f"Rs.{data['should_pay']:.2f}")
                            
                            if data['balance'] > 0:
                                st.success(f"Gets back: Rs.{data['gets_back']:.2f}")
                            else:
                                st.error(f"Owes: Rs.{data['owes']:.2f}")
                
                with col2:
                    st.write("**Optimized Transactions:**")
                    transactions = optimize_payments(results)
                    
                    if transactions:
                        for i, txn in enumerate(transactions):
                            st.info(
                                f"**{txn['from']}** pays **{txn['to']}**: Rs.{txn['amount']:.2f}"
                            )
                    else:
                        st.success("✅ All settled! No payments needed.")
                
                # Visualization
                st.subheader("📈 Visual Breakdown")
                
                # Balance chart
                names = list(results.keys())
                balances = [results[name]['balance'] for name in names]
                
                fig = go.Figure(data=go.Bar(
                    x=names,
                    y=balances,
                    marker_color=['green' if b >= 0 else 'red' for b in balances]
                ))
                fig.update_layout(
                    title="Balance Overview (Green = Gets Money, Red = Owes Money)",
                    xaxis_title="People",
                    yaxis_title="Balance (Rs.)"
                )
                st.plotly_chart(fig, use_container_width=True)

# Analytics Mode
elif app_mode == "📊 Analytics":
    st.header("📊 Expense Analytics")
    
    if st.session_state.expenses and st.session_state.people:
        # Total statistics
        total_spent = sum([exp['amount'] for exp in st.session_state.expenses])
        avg_expense = total_spent / len(st.session_state.expenses)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Spent", f"Rs.{total_spent:.2f}")
        
        with col2:
            st.metric("Average Expense", f"Rs.{avg_expense:.2f}")
        
        with col3:
            st.metric("Number of Expenses", len(st.session_state.expenses))
        
        # Expense breakdown by person
        st.subheader("💳 Who Paid What")
        
        payer_totals = defaultdict(float)
        for exp in st.session_state.expenses:
            payer_totals[exp['payer']] += exp['amount']
        
        if payer_totals:
            fig = px.pie(
                values=list(payer_totals.values()),
                names=list(payer_totals.keys()),
                title="Expenses by Payer"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Expense timeline
        st.subheader("📅 Expense Timeline")
        
        expenses_df = pd.DataFrame(st.session_state.expenses)
        expenses_df['timestamp'] = pd.to_datetime(expenses_df['timestamp'])
        
        fig = px.line(
            expenses_df, 
            x='timestamp', 
            y='amount',
            title='Expenses Over Time',
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top expenses
        st.subheader("🔝 Top Expenses")
        top_expenses = sorted(st.session_state.expenses, key=lambda x: x['amount'], reverse=True)[:5]
        
        for i, exp in enumerate(top_expenses, 1):
            st.info(f"{i}. **{exp['description']}** - Rs.{exp['amount']:.2f} (paid by {exp['payer']})")
    
    else:
        st.info("No expense data available. Add some expenses in Advanced Split mode!")

# Payment Hub
elif app_mode == "💳 Payment Hub":
    st.header("💳 Payment Hub")
    
    if st.session_state.expenses and st.session_state.people:
        # Calculate current split
        results = calculate_advanced_split(
            st.session_state.expenses, 
            st.session_state.people, 
            "equal"
        )
        transactions = optimize_payments(results)
        
        if transactions:
            st.subheader("💸 Required Payments")
            
            for txn in transactions:
                with st.expander(f"{txn['from']} → {txn['to']}: Rs.{txn['amount']:.2f}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Payment Methods:**")
                        
                        # Generate payment links/info
                        payment_methods = {
                            "Venmo": f"venmo://pay?recipients={txn['to']}&amount={txn['amount']}&note=Expense%20Split",
                            "PayPal": f"https://paypal.me/{txn['to']}/{txn['amount']}",
                            "Zelle": f"mailto:{txn['to']}@email.com?subject=Payment%20Request&body=Please%20pay%20Rs.{txn['amount']}%20for%20shared%20expenses",
                            "Cash App": f"https://cash.app/Rs.{txn['to']}/{txn['amount']}"
                        }
                        
                        for method, link in payment_methods.items():
                            if st.button(f"Pay via {method}", key=f"{method}_{txn['from']}_{txn['to']}"):
                                st.info(f"Payment link: {link}")
                    
                    with col2:
                        st.write("**QR Code for Payment:**")
                        
                        # Generate QR code
                        payment_info = f"Pay {txn['to']} Rs.{txn['amount']:.2f} for shared expenses"
                        qr_code = generate_qr_code(payment_info)
                        
                        st.markdown(
                            f'<img src="data:image/png;base64,{qr_code}" width="150">',
                            unsafe_allow_html=True
                        )
                        
                        if st.button("✅ Mark as Paid", key=f"paid_{txn['from']}_{txn['to']}"):
                            st.success("Payment marked as completed!")
        
        else:
            st.success("🎉 All payments are settled!")
    
    else:
        st.info("No payment data available. Add expenses first!")

# Split History
elif app_mode == "📈 Split History":
    st.header("📈 Split History")
    
    if st.session_state.split_history:
        st.write(f"**Total Splits Saved:** {len(st.session_state.split_history)}")
        
        for i, split in enumerate(reversed(st.session_state.split_history)):
            with st.expander(f"Split #{len(st.session_state.split_history)-i} - {split['timestamp']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Amount", f"Rs.{split['total_amount']:.2f}")
                    st.metric("Per Person", f"Rs.{split['per_person']:.2f}")
                
                with col2:
                    st.write("**People:**")
                    for person in split['people']:
                        st.write(f"• {person}")
        
        # Clear history
        if st.button("🗑️ Clear History"):
            st.session_state.split_history = []
            st.success("History cleared!")
    
    else:
        st.info("No split history available.")

# Clear data button
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset All Data"):
    st.session_state.expenses = []
    st.session_state.people = []
    st.session_state.split_history = []
    st.success("All data cleared!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666;">
        💰 Smart Expense Splitter Pro | Made with Streamlit<br>
        Features: Quick Split • Advanced Calculations • Payment Integration • Analytics
    </div>
    """,
    unsafe_allow_html=True
)