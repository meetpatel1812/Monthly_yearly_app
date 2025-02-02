import streamlit as st
import pandas as pd
import datetime
import time

# File storage paths
PAY_INCOME_FILE = "pay_income.csv"
OTHER_INCOME_FILE = "other_income.csv"
EXPENSE_FILE = "expenses.csv"
TOTAL_INCOME_FILE = "total_income.csv"
TOTAL_EXPENSE_FILE = "total_expense.csv"

# Load Data Function
def load_data(file_path, columns):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return pd.DataFrame(columns=columns)

# Save Data Function
def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# Initialize Data
pay_income = load_data(PAY_INCOME_FILE, ["Date", "Name", "Amount"])
other_income = load_data(OTHER_INCOME_FILE, ["Date", "Name", "Amount"])
expenses = load_data(EXPENSE_FILE, ["Date", "Name", "Amount"])
total_income = load_data(TOTAL_INCOME_FILE, ["Year", "Month", "Date", "Name", "Amount"])
total_expense = load_data(TOTAL_EXPENSE_FILE, ["Year", "Month", "Date", "Name", "Amount"])

# Get current month and year
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year

# Streamlit UI
st.title("Welcome Komal..")

# st.header("Summary")
st.write(f"**Total Income:** ${total_income['Amount'].sum():.2f}")
st.write(f"**Total Expense:** ${total_expense['Amount'].sum():.2f}")
st.markdown("---")

# Sidebar for filtering monthly data
st.sidebar.header("Filter Monthly Data")
selected_month = st.sidebar.selectbox("Select Month", range(1, 13), current_month - 1)
selected_year = st.sidebar.selectbox("Select Year", range(current_year - 5, current_year + 1), 5)

# Filter data for the selected month and year
monthly_pay_income = pay_income[(pd.to_datetime(pay_income["Date"]).dt.month == selected_month) & 
                                (pd.to_datetime(pay_income["Date"]).dt.year == selected_year)]
monthly_other_income = other_income[(pd.to_datetime(other_income["Date"]).dt.month == selected_month) & 
                                    (pd.to_datetime(other_income["Date"]).dt.year == selected_year)]
monthly_expenses = expenses[(pd.to_datetime(expenses["Date"]).dt.month == selected_month) & 
                            (pd.to_datetime(expenses["Date"]).dt.year == selected_year)]

# Calculate monthly income and expense
monthly_income_value = monthly_pay_income["Amount"].sum() + monthly_other_income["Amount"].sum()
monthly_expense_value = monthly_expenses["Amount"].sum()

st.write(f"**Monthly Income ({selected_month}/{selected_year}):** ${monthly_income_value:.2f}")
st.write(f"**Monthly Expense ({selected_month}/{selected_year}):** ${monthly_expense_value:.2f}")
st.write(f"**Monthly Saving ({selected_month}/{selected_year}):** ${monthly_expense_value:.2f - monthly_expense_value:.2f}")
st.markdown("---")

st.header("Monthly Transactions")

# Display tables
st.subheader("Pay Income ({}/{})".format(selected_month, selected_year))
st.dataframe(monthly_pay_income)

st.subheader("Other Income ({}/{})".format(selected_month, selected_year))
st.dataframe(monthly_other_income)

st.subheader("Expenses ({}/{})".format(selected_month, selected_year))
st.dataframe(monthly_expenses)

st.markdown("---")
st.subheader("Total Income Records")
st.dataframe(total_income)

st.subheader("Total Expense Records")
st.dataframe(total_expense)

st.sidebar.header("Manage Entries")

# Sidebar Entry Management
entry_type = st.sidebar.selectbox("Select Table", ["Pay Income", "Other Income", "Expense"])
date = st.sidebar.date_input("Date", datetime.date.today())
name = st.sidebar.text_input("Name")
amount = st.sidebar.number_input("Amount", min_value=0.0, format="%.2f")

if st.sidebar.button("Submit"):
    new_entry = {"Date": date, "Name": name, "Amount": amount}
    new_entry_total = {"Year": date.year, "Month": date.month, "Date": date, "Name": name, "Amount": amount}
    
    if entry_type == "Pay Income":
        pay_income = pd.concat([pay_income, pd.DataFrame([new_entry])], ignore_index=True)
        save_data(pay_income, PAY_INCOME_FILE)
        total_income = pd.concat([total_income, pd.DataFrame([new_entry_total])], ignore_index=True)
        save_data(total_income, TOTAL_INCOME_FILE)
    elif entry_type == "Other Income":
        other_income = pd.concat([other_income, pd.DataFrame([new_entry])], ignore_index=True)
        save_data(other_income, OTHER_INCOME_FILE)
        total_income = pd.concat([total_income, pd.DataFrame([new_entry_total])], ignore_index=True)
        save_data(total_income, TOTAL_INCOME_FILE)
    else:
        expenses = pd.concat([expenses, pd.DataFrame([new_entry])], ignore_index=True)
        save_data(expenses, EXPENSE_FILE)
        total_expense = pd.concat([total_expense, pd.DataFrame([new_entry_total])], ignore_index=True)
        save_data(total_expense, TOTAL_EXPENSE_FILE)

    st.sidebar.success("Entry Added Successfully!")
    st.rerun()

# Sidebar for Modify/Delete Entries
st.sidebar.header("Modify or Delete Entries")
modify_entry_type = st.sidebar.selectbox("Select Table to Modify/Delete", ["Pay Income", "Other Income", "Expense"])
modify_date = st.sidebar.date_input("Select Date", datetime.date.today())
modify_name = st.sidebar.text_input("Select Name")

# Find the entry to modify or delete
if modify_entry_type == "Pay Income":
    df_to_modify = pay_income
    file_to_modify = PAY_INCOME_FILE
    total_df_to_modify = total_income
    total_file_to_modify = TOTAL_INCOME_FILE
elif modify_entry_type == "Other Income":
    df_to_modify = other_income
    file_to_modify = OTHER_INCOME_FILE
    total_df_to_modify = total_income
    total_file_to_modify = TOTAL_INCOME_FILE
else:
    df_to_modify = expenses
    file_to_modify = EXPENSE_FILE
    total_df_to_modify = total_expense
    total_file_to_modify = TOTAL_EXPENSE_FILE

# Filter the selected entry
selected_entry = df_to_modify[(df_to_modify["Date"] == modify_date.isoformat()) & 
                              (df_to_modify["Name"] == modify_name)]
selected_total_entry = total_df_to_modify[(total_df_to_modify["Date"] == modify_date.isoformat()) & 
                                          (total_df_to_modify["Name"] == modify_name)]

if not selected_entry.empty:
    st.sidebar.write(f"Selected Entry: {selected_entry.iloc[0]['Name']} on {selected_entry.iloc[0]['Date']} for ${selected_entry.iloc[0]['Amount']:.2f}")
    new_amount = st.sidebar.number_input("New Amount", value=float(selected_entry.iloc[0]["Amount"]), format="%.2f")

    if st.sidebar.button("Update Entry"):
        # Update the entry in the main DataFrame
        df_to_modify.loc[(df_to_modify["Date"] == modify_date.isoformat()) & 
                         (df_to_modify["Name"] == modify_name), "Amount"] = new_amount
        save_data(df_to_modify, file_to_modify)

        # Update the entry in the total DataFrame
        total_df_to_modify.loc[(total_df_to_modify["Date"] == modify_date.isoformat()) & 
                               (total_df_to_modify["Name"] == modify_name), "Amount"] = new_amount
        save_data(total_df_to_modify, total_file_to_modify)

        st.sidebar.success("Entry Updated Successfully!")
        st.rerun()

    if st.sidebar.button("Delete Entry"):
        # Delete the entry from the main DataFrame
        df_to_modify = df_to_modify[~((df_to_modify["Date"] == modify_date.isoformat()) & 
                                      (df_to_modify["Name"] == modify_name))]
        save_data(df_to_modify, file_to_modify)

        # Delete the entry from the total DataFrame
        total_df_to_modify = total_df_to_modify[~((total_df_to_modify["Date"] == modify_date.isoformat()) & 
                                                  (total_df_to_modify["Name"] == modify_name))]
        save_data(total_df_to_modify, total_file_to_modify)

        st.sidebar.success("Entry Deleted Successfully!")
        st.rerun()
else:
    st.sidebar.warning("No matching entry found.")

while True:
    time.sleep(1)