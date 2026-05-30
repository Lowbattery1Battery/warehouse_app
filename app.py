import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="Warehouse App", layout="wide")

# ----------------------------
# SUPABASE
# ----------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ----------------------------
# SIDEBAR MENU
# ----------------------------
page = st.sidebar.radio("Menu", [
    "Inventory",
    "Low Stock",
    "Daily Usage",
    "Monthly Usage"
])

# ----------------------------
# LOAD INVENTORY
# ----------------------------
def get_inventory():
    return supabase.table("inventory").select("*").execute().data or []

data = get_inventory()

# ============================
# INVENTORY PAGE
# ============================
if page == "Inventory":

    st.title("📦 Inventory")

    st.subheader("Add Item")

    with st.form("add"):
        item = st.text_input("Item")
        category = st.text_input("Category")
        qty = st.number_input("Quantity", 0)
        reorder = st.number_input("Reorder Level", 0)
        reorder_amt = st.number_input("Reorder Amount", 0)

        if st.form_submit_button("Add"):
            supabase.table("inventory").insert({
                "item": item,
                "category": category,
                "quantity": qty,
                "reorder_level": reorder,
                "reorder_amount": reorder_amt
            }).execute()
            st.rerun()

    st.divider()

    for i in data:
        st.write(f"**{i['item']}** | Qty: {i['quantity']}")

# ============================
# LOW STOCK PAGE
# ============================
elif page == "Low Stock":

    st.title("⚠️ Low Stock Items")

    for i in data:
        if i["quantity"] <= i["reorder_level"]:
            st.warning(f"{i['item']} — Qty: {i['quantity']} (Low)")

# ============================
# DAILY USAGE
# ============================
elif page == "Daily Usage":

    st.title("📊 Daily Usage Tracker")

    item = st.selectbox("Item", [i["item"] for i in data])
    used = st.number_input("Used Today", 0)

    if st.button("Log Daily Usage"):

        supabase.table("usage_logs").insert({
            "item": item,
            "used": used,
            "date": str(datetime.now().date())
        }).execute()

        st.success("Logged!")

# ============================
# MONTHLY USAGE
# ============================
elif page == "Monthly Usage":

    st.title("📈 Monthly Usage")

    logs = supabase.table("usage_logs").select("*").execute().data or []

    monthly = {}

    for log in logs:
        month = log["date"][:7]  # YYYY-MM
        key = (log["item"], month)

        monthly[key] = monthly.get(key, 0) + log["used"]

    for (item, month), used in monthly.items():
        st.write(f"{month} | {item}: {used}")
