import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="Warehouse System", layout="wide")

# ------------------------
# SUPABASE
# ------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ------------------------
# LOAD DATA
# ------------------------
def load_items():
    try:
        return supabase.table("inventory").select("*").execute().data or []
    except Exception as e:
        st.error(f"Database error: {e}")
        return []

data = load_items()

# ------------------------
# LOG USAGE
# ------------------------
def log_usage(item_name, amount):
    supabase.table("usage_logs").insert({
        "item": item_name,
        "used": amount,
        "date": str(datetime.now().date())
    }).execute()

# ------------------------
# SIDEBAR
# ------------------------
page = st.sidebar.radio("Menu", [
    "Inventory",
    "Low Stock",
    "Orders",
    "Usage"
])

# =========================================================
# INVENTORY
# =========================================================
if page == "Inventory":

    st.title("📦 Inventory System")

    # ---------------- ADD ITEM ----------------
    st.subheader("➕ Add Item")

    with st.form("add_item"):
        item = st.text_input("Item Name")
        category = st.text_input("Category")
        qty = st.number_input("Quantity", 0)
        reorder_level = st.number_input("Reorder Level", 0)
        reorder_amount = st.number_input("Reorder Amount", 0)

        if st.form_submit_button("Add"):
            supabase.table("inventory").insert({
                "item": item,
                "category": category,
                "quantity": qty,
                "reorder_level": reorder_level,
                "reorder_amount": reorder_amount
            }).execute()
            st.rerun()

    st.divider()

    # ---------------- ITEM CARDS ----------------
    for i in data:

        item_id = i["id"]
        name = i["item"]
        qty = i["quantity"]
        category = i["category"]
        reorder = i["reorder_level"]

        # status
        if qty <= 0:
            status_color = "🔴"
            status_text = "OUT OF STOCK"
        elif qty <= reorder:
            status_color = "🟠"
            status_text = "LOW STOCK"
        else:
            status_color = "🟢"
            status_text = "OK"

        # CARD UI
        st.markdown(f"""
        <div style="
            background-color: white;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #ddd;
            margin-bottom: 12px;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
        ">
            <h3 style="margin-bottom:5px;">{name}</h3>
            <p style="margin:0;"><b>Category:</b> {category}</p>
            <p style="margin:0;"><b>Quantity:</b> {qty}</p>
            <p style="margin:0;"><b>Status:</b> {status_color} {status_text}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)

        # +1
        with col1:
            if st.button("+1", key=f"p1_{item_id}"):
                supabase.table("inventory").update({
                    "quantity": qty + 1
                }).eq("id", item_id).execute()
                st.rerun()

        # -1 (LOGS USAGE)
        with col2:
            if st.button("-1", key=f"m1_{item_id}"):
                new_qty = max(0, qty - 1)

                supabase.table("inventory").update({
                    "quantity": new_qty
                }).eq("id", item_id).execute()

                log_usage(name, 1)
                st.rerun()

        # +5
        with col3:
            if st.button("+5", key=f"p5_{item_id}"):
                supabase.table("inventory").update({
                    "quantity": qty + 5
                }).eq("id", item_id).execute()
                st.rerun()

        # DELETE
        with col4:
            if st.button("DELETE", key=f"d_{item_id}"):
                supabase.table("inventory").delete().eq("id", item_id).execute()
                st.rerun()

        # SETTINGS
        with col5:
            with st.expander("⚙ Settings"):
                new_reorder = st.number_input(
                    "Reorder Level",
                    value=reorder,
                    key=f"r_{item_id}"
                )

                new_amount = st.number_input(
                    "Reorder Amount",
                    value=i["reorder_amount"],
                    key=f"a_{item_id}"
                )

                if st.button("Save", key=f"s_{item_id}"):
                    supabase.table("inventory").update({
                        "reorder_level": new_reorder,
                        "reorder_amount": new_amount
                    }).eq("id", item_id).execute()
                    st.rerun()

# =========================================================
# LOW STOCK
# =========================================================
elif page == "Low Stock":

    st.title("⚠️ Low Stock Items")

    for i in data:
        if i["quantity"] <= i["reorder_level"]:
            st.warning(f"{i['item']} — Qty: {i['quantity']}")

# =========================================================
# ORDERS
# =========================================================
elif page == "Orders":

    st.title("📦 Orders Needed")

    for i in data:
        if i["quantity"] <= i["reorder_level"]:
            st.info(f"Order {i['reorder_amount']} of {i['item']}")

# =========================================================
# USAGE
# =========================================================
elif page == "Usage":

    st.title("📊 Usage Logs")

    logs = supabase.table("usage_logs").select("*").execute().data or []

    for log in logs:
        st.write(f"{log['date']} | {log['item']} | Used: {log['used']}")
