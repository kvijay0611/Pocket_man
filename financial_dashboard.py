import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set page title, icon, and layout
st.set_page_config(
    page_title="My Finance Dashboard",
    page_icon="💰",
    layout="wide"
)

# App title
st.title("💰 Personal Finance Dashboard")

# Initialize empty DataFrames if they don't exist
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=[
        'Date', 'Description', 'Category', 'Amount', 'Type'
    ])

if 'budgets' not in st.session_state:
    st.session_state.budgets = pd.DataFrame(columns=[
        'Category', 'Amount'
    ])

# Sidebar for adding transactions
with st.sidebar:
    st.header("➕ Add New Transaction")
    trans_date = st.date_input("Date", datetime.today())
    trans_desc = st.text_input("Description")
    trans_category = st.selectbox(
        "Category",
        ["Food", "Transport", "Rent", "Entertainment", "Utilities", "Other"],
        key="trans_category"
    )
    trans_amount = st.number_input("Amount (Rs)", min_value=0.01, step=0.01)
    trans_type = st.radio("Type", ["Income", "Expense"])
    if st.button("Add Transaction"):
        new_transaction = pd.DataFrame([{
            'Date': trans_date,
            'Description': trans_desc,
            'Category': trans_category,
            'Amount': trans_amount,
            'Type': trans_type
        }])
        st.session_state.transactions = pd.concat(
            [st.session_state.transactions, new_transaction],
            ignore_index=True
        )
        st.success("Transaction added!")

    st.header("📊 Set Budgets")
    budget_category = st.selectbox(
        "Budget Category",
        ["Food", "Transport", "Rent", "Entertainment", "Utilities", "Other"],
        key="budget_category"
    )
    budget_amount = st.number_input("Budget Amount (Rs)", min_value=0.01, step=0.01)
    if st.button("Set Budget"):
        st.session_state.budgets = st.session_state.budgets[
            st.session_state.budgets['Category'] != budget_category
        ]
        new_budget = pd.DataFrame([{
            'Category': budget_category,
            'Amount': budget_amount
        }])
        st.session_state.budgets = pd.concat(
            [st.session_state.budgets, new_budget],
            ignore_index=True
        )
        st.success("Budget set!")

# Tabs for main content
tab1, tab2, tab3 = st.tabs(["📊 Overview", "💵 Transactions", "📉 Budget Analysis"])

with tab1:
    st.header("Financial Overview")
    if not st.session_state.transactions.empty:
        # Calculate total income, expenses, and net balance
        total_income = st.session_state.transactions[
            st.session_state.transactions['Type'] == 'Income'
        ]['Amount'].sum()
        total_expenses = st.session_state.transactions[
            st.session_state.transactions['Type'] == 'Expense'
        ]['Amount'].sum()
        net_balance = total_income - total_expenses

        # Display metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"Rs{total_income:,.2f}")
        col2.metric("Total Expenses", f"Rs{total_expenses:,.2f}")
        col3.metric("Net Balance", f"Rs{net_balance:,.2f}", 
                   delta_color="inverse" if net_balance < 0 else "normal")

        # Monthly trends (Plotly line chart)
        st.subheader("Monthly Trends")
        transactions = st.session_state.transactions.copy()
        transactions['Month'] = pd.to_datetime(transactions['Date']).dt.to_period('M').astype(str)
        monthly_data = transactions.groupby(['Month', 'Type']).sum(numeric_only=True).reset_index()
        fig = px.line(
            monthly_data,
            x='Month',
            y='Amount',
            color='Type',
            title="Income vs Expenses Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Expense breakdown (Pie chart)
        st.subheader("Expense Breakdown")
        expenses = transactions[transactions['Type'] == 'Expense']
        if not expenses.empty:
            fig = px.pie(
                expenses,
                names='Category',
                values='Amount',
                title="Spending by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transactions yet. Add some in the sidebar!")

with tab2:
    st.header("Transaction History")
    if not st.session_state.transactions.empty:
        st.dataframe(
            st.session_state.transactions.sort_values('Date', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
            label="📥 Export Transactions",
            data=st.session_state.transactions.to_csv(index=False).encode('utf-8'),
            file_name='transactions.csv',
            mime='text/csv'
        )
    else:
        st.info("No transactions yet. Add some in the sidebar!")

with tab3:
    st.header("Budget Analysis")
    if not st.session_state.transactions.empty and not st.session_state.budgets.empty:
        expenses_by_category = st.session_state.transactions[
            st.session_state.transactions['Type'] == 'Expense'
        ].groupby('Category').sum(numeric_only=True).reset_index()
        budget_vs_actual = pd.merge(
            st.session_state.budgets,
            expenses_by_category,
            on='Category',
            how='left',
            suffixes=('_budget', '_actual')
        ).fillna(0)
        budget_vs_actual['Remaining'] = budget_vs_actual['Amount_budget'] - budget_vs_actual['Amount_actual']
        budget_vs_actual['Percentage Used'] = (budget_vs_actual['Amount_actual'] / budget_vs_actual['Amount_budget']) * 100
        st.dataframe(
            budget_vs_actual,
            use_container_width=True,
            hide_index=True
        )
        st.subheader("Budget vs Actual Spending")
        fig = px.bar(
            budget_vs_actual.melt(id_vars='Category', value_vars=['Amount_budget', 'Amount_actual']),
            x='Category',
            y='value',
            color='variable',
            barmode='group',
            labels={'value': 'Amount (Rs)', 'variable': 'Type'},
            title="Budget vs Actual Spending"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add transactions and set budgets to see analysis.")


