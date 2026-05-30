import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(
page_title="Warehouse Management System",
layout="wide"
)

# --------------------------------------------------

# SUPABASE

# --------------------------------------------------

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --------------------------------------------------

# LOAD DATA

# --------------------------------------------------

def load_inventory():
try:
return supabase.table("inventory").select("*").execute().data or []
except Exception as e:
st.error(f"Inventory Error: {e}")
return []

def load_usage_logs():
try:
return (
supabase
.table("usage_logs")
.select("*")
.execute()
.data
or []
)
except Exception as e:
st.error(f"Usage Log Error: {e}")
return []

def log_usage(item_name, amount):
try:
supabase.table("usage_logs").insert({
"item": item_name,
"used": amount,
"date": str(datetime.now().date())
}).execute()
except Exception as e:
st.error(f"Usage Log Error: {e}")

inventory = load_inventory()

# --------------------------------------------------

# SIDEBAR

# --------------------------------------------------

st.sidebar.title("Warehouse Management")
st.sidebar.caption("Hotel Supply System")

page = st.sidebar.radio(
"",
[
"Inventory",
"Low Stock",
"Orders",
"Usage Reports"
]
)

# ==================================================

# INVENTORY

# ==================================================

if page == "Inventory":

```
st.title("Inventory")

# ---------------- SEARCH ----------------
search = st.text_input(
    "Search Inventory",
    placeholder="Search by item name..."
)

if search:
    inventory = [
        item
        for item in inventory
        if search.lower() in item["item"].lower()
    ]

# ---------------- ADD ITEM ----------------
with st.expander("Add New Item"):

    with st.form("add_item_form"):

        item_name = st.text_input("Item Name")
        category = st.text_input("Category")

        quantity = st.number_input(
            "Starting Quantity",
            min_value=0,
            value=0
        )

        reorder_level = st.number_input(
            "Reorder Level",
            min_value=0,
            value=5
        )

        reorder_amount = st.number_input(
            "Reorder Amount",
            min_value=0,
            value=10
        )

        submit = st.form_submit_button("Add Item")

        if submit:

            supabase.table("inventory").insert({
                "item": item_name,
                "category": category,
                "quantity": quantity,
                "reorder_level": reorder_level,
                "reorder_amount": reorder_amount
            }).execute()

            st.success("Item Added")
            st.rerun()

st.divider()

# ---------------- ITEM CARDS ----------------
for item in inventory:

    item_id = item["id"]
    name = item["item"]
    category = item["category"]
    quantity = item["quantity"]
    reorder_level = item["reorder_level"]
    reorder_amount = item["reorder_amount"]

    if quantity <= 0:
        status = "OUT OF STOCK"
        status_color = "#b00020"
    elif quantity <= reorder_level:
        status = "LOW STOCK"
        status_color = "#c77700"
    else:
        status = "IN STOCK"
        status_color = "#006400"

    st.markdown(
        f"""
        <div style="
            background-color:#1f4e79;
            color:white;
            padding:18px;
            border-radius:12px;
            margin-bottom:12px;
        ">
            <h3 style="margin-bottom:8px;color:white;">
                {name}
            </h3>

            <p style="margin:2px 0;">
                Category: {category}
            </p>

            <p style="
                font-size:22px;
                margin:6px 0;
                font-weight:bold;
            ">
                Quantity: {quantity}
            </p>

            <p style="
                color:{status_color};
                font-weight:bold;
                margin:0;
            ">
                {status}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    # +1
    with col1:
        if st.button("+1", key=f"plus_{item_id}"):

            supabase.table("inventory").update({
                "quantity": quantity + 1
            }).eq("id", item_id).execute()

            st.rerun()

    # -1
    with col2:
        if st.button("-1", key=f"minus_{item_id}"):

            new_quantity = max(0, quantity - 1)

            supabase.table("inventory").update({
                "quantity": new_quantity
            }).eq("id", item_id).execute()

            log_usage(name, 1)

            st.rerun()

    # +5
    with col3:
        if st.button("+5", key=f"plus5_{item_id}"):

            supabase.table("inventory").update({
                "quantity": quantity + 5
            }).eq("id", item_id).execute()

            st.rerun()

    # DELETE ITEM
    with col4:
        if st.button(
            "Delete Item",
            key=f"delete_{item_id}"
        ):

            supabase.table("inventory").delete().eq(
                "id",
                item_id
            ).execute()

            st.rerun()

    # SETTINGS
    with col5:

        with st.expander("Settings"):

            new_reorder_level = st.number_input(
                "Reorder Level",
                value=int(reorder_level),
                key=f"rl_{item_id}"
            )

            new_reorder_amount = st.number_input(
                "Reorder Amount",
                value=int(reorder_amount),
                key=f"ra_{item_id}"
            )

            if st.button(
                "Save Settings",
                key=f"save_{item_id}"
            ):

                supabase.table("inventory").update({
                    "reorder_level": new_reorder_level,
                    "reorder_amount": new_reorder_amount
                }).eq(
                    "id",
                    item_id
                ).execute()

                st.rerun()
```

# ==================================================

# LOW STOCK

# ==================================================

elif page == "Low Stock":

```
st.title("Low Stock")

found = False

for item in inventory:

    if item["quantity"] <= item["reorder_level"]:

        found = True

        st.warning(
            f"{item['item']} "
            f"(Qty: {item['quantity']})"
        )

if not found:
    st.success("No low stock items.")
```

# ==================================================

# ORDERS

# ==================================================

elif page == "Orders":

```
st.title("Order Suggestions")

found = False

for item in inventory:

    if item["quantity"] <= item["reorder_level"]:

        found = True

        st.info(
            f"Order {item['reorder_amount']} "
            f"of {item['item']}"
        )

if not found:
    st.success("No orders needed.")
```

# ==================================================

# USAGE REPORTS

# ==================================================

elif page == "Usage Reports":

```
st.title("Usage Reports")

logs = load_usage_logs()

if not logs:
    st.info("No usage data available.")
    st.stop()

st.subheader("Daily Summary")

daily_totals = {}

for log in logs:

    key = (
        log["date"],
        log["item"]
    )

    daily_totals[key] = (
        daily_totals.get(key, 0)
        + log["used"]
    )

for (date, item_name), total in sorted(
    daily_totals.items(),
    reverse=True
):

    st.write(
        f"{date} | {item_name} | Used: {total}"
    )

st.divider()

st.subheader("Monthly Summary")

monthly_totals = {}

for log in logs:

    month = log["date"][:7]

    key = (
        month,
        log["item"]
    )

    monthly_totals[key] = (
        monthly_totals.get(key, 0)
        + log["used"]
    )

for (month, item_name), total in sorted(
    monthly_totals.items(),
    reverse=True
):

    st.write(
        f"{month} | {item_name} | Used: {total}"
    )

st.divider()

st.subheader("Usage Log Entries")

for log in sorted(
    logs,
    key=lambda x: x["id"],
    reverse=True
):

    c1, c2 = st.columns([6, 1])

    with c1:
        st.write(
            f"{log['date']} | "
            f"{log['item']} | "
            f"Used: {log['used']}"
        )

    with c2:
        if st.button(
            "Delete",
            key=f"log_{log['id']}"
        ):

            supabase.table(
                "usage_logs"
            ).delete().eq(
                "id",
                log["id"]
            ).execute()

            st.rerun()
```

"""
