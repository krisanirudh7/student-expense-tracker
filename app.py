# ============================================================
# Student Expense Tracker
# Built with Python, Streamlit, Pandas, and Matplotlib
# ============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date

# ----------------------------
# Configuration
# ----------------------------
CSV_FILE = "expenses.csv"          # File where all expenses are saved
CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Other"]

# ----------------------------
# Helper Functions
# ----------------------------

def load_expenses():
    """Load existing expenses from the CSV file.
    If the file doesn't exist yet, return an empty DataFrame."""
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, parse_dates=["Date"])
        return df
    else:
        # Create an empty DataFrame with the right columns
        return pd.DataFrame(columns=["Date", "Category", "Amount"])


def save_expense(new_expense: dict):
    """Append a single new expense to the CSV file."""
    df = load_expenses()                          # Load whatever already exists
    new_row = pd.DataFrame([new_expense])         # Turn the dict into a one-row DataFrame
    df = pd.concat([df, new_row], ignore_index=True)  # Add the new row
    df.to_csv(CSV_FILE, index=False)              # Save back to the file


def show_pie_chart(df: pd.DataFrame):
    """Draw a category-wise pie chart using Matplotlib."""
    # Group expenses by category and sum the amounts
    category_totals = df.groupby("Category")["Amount"].sum()

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(
        category_totals,
        labels=category_totals.index,
        autopct="%1.1f%%",          # Show percentage on each slice
        startangle=140,
        colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
    )
    ax.set_title("Spending by Category", fontsize=14, fontweight="bold")
    st.pyplot(fig)                  # Display the chart inside Streamlit


# ----------------------------
# Main App
# ----------------------------

def main():

    # ── Page title ──────────────────────────────────────────
    st.title("🎓 Student Expense Tracker")
    st.markdown("Track your spending, stick to your budget!")
    st.divider()

    # ── Sidebar: Budget Input ────────────────────────────────
    st.sidebar.header("💰 Monthly Budget")
    budget = st.sidebar.number_input(
        "Enter your monthly budget (₹ / $)",
        min_value=0.0,
        value=5000.0,
        step=100.0
    )

    # ── Sidebar: Add New Expense ────────────────────────────
    st.sidebar.header("➕ Add New Expense")

    expense_date = st.sidebar.date_input("Date", value=date.today())
    category     = st.sidebar.selectbox("Category", CATEGORIES)
    amount       = st.sidebar.number_input("Amount (₹ / $)", min_value=0.0, step=10.0)

    if st.sidebar.button("Add Expense"):
        if amount <= 0:
            st.sidebar.error("Please enter an amount greater than 0.")
        else:
            # Build the expense record and save it
            new_expense = {
                "Date"    : expense_date,
                "Category": category,
                "Amount"  : amount
            }
            save_expense(new_expense)
            st.sidebar.success(f"✅ Added ₹{amount:.2f} under '{category}'!")

    # ── Load all expenses ───────────────────────────────────
    df = load_expenses()

    # ── Summary Cards ───────────────────────────────────────
    total_spent    = df["Amount"].sum() if not df.empty else 0.0
    remaining      = budget - total_spent

    col1, col2, col3 = st.columns(3)

    col1.metric("📊 Monthly Budget",  f"₹ {budget:,.2f}")
    col2.metric("💸 Total Spent",     f"₹ {total_spent:,.2f}")
    col3.metric(
        "🏦 Remaining Balance",
        f"₹ {remaining:,.2f}",
        delta=f"{'Over budget!' if remaining < 0 else 'On track'}",
        delta_color="inverse"
    )

    st.divider()

    # ── Expense Table ───────────────────────────────────────
    st.subheader("📋 All Expenses")

    if df.empty:
        st.info("No expenses recorded yet. Add your first expense from the sidebar!")
    else:
        # Format the Date column nicely before displaying
        display_df = df.copy()
        display_df["Date"]   = pd.to_datetime(display_df["Date"]).dt.strftime("%d %b %Y")
        display_df["Amount"] = display_df["Amount"].apply(lambda x: f"₹ {x:,.2f}")

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # ── Pie Chart ───────────────────────────────────────
        st.divider()
        st.subheader("🥧 Spending by Category")
        show_pie_chart(df)

        # ── Category Summary Table ──────────────────────────
        st.divider()
        st.subheader("📊 Category-wise Summary")
        summary = (
            df.groupby("Category")["Amount"]
            .sum()
            .reset_index()
            .rename(columns={"Amount": "Total Spent"})
            .sort_values("Total Spent", ascending=False)
        )
        summary["Total Spent"] = summary["Total Spent"].apply(lambda x: f"₹ {x:,.2f}")
        st.dataframe(summary, use_container_width=True, hide_index=True)

        # ── Clear All Button ────────────────────────────────
        st.divider()
        if st.button("🗑️ Clear All Expenses", type="secondary"):
            os.remove(CSV_FILE)
            st.success("All expenses cleared!")
            st.rerun()


# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    main()
