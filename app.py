import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="Warehouse System", layout="wide")

# -----------------------------
# SUPABASE
# -----------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# -----------------------------
# DATA
# -----------------------------
def load_inventory():
    data = supabase.table("inventory").select("*").execute().data or []
    return sorted(data, key=lambda x: x["item"].lower())

def load_logs():
    return supabase.table("usage_logs").select("*").execute().data or []

def log_usage(item, amount):
    supabase.table("usage_logs").insert({
        "item": item,
        "used": amount,
        "date": str(datetime.now().date())
    }).execute()

inventory = load_inventory()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Warehouse System")

page = st.sidebar.radio(
    "",
    ["Inventory", "Low Stock", "Orders", "Usage Reports"]
)

# =====================================================
# INVENTORY
# =====================================================
if page == "Inventory":

    st.title("Inventory")

    # ---------------- SEARCH ----------------
    search = st.text_input("Search item")

    if search:
        inventory = [
            i for i in inventory
            if search.lower() in i["item"].lower()
        ]

    # ---------------- ADD ITEM ----------------
    with st.expander("Add Item"):

        with st.form("add_item"):

            item = st.text_input("Item Name")
            category = st.text_input("Category")
            qty = st.number_input("Quantity", min_value=0, value=0)

            reorder_level = st.number_input(
                "Reorder Level",
                min_value=0,
                value=5
            )

            submit = st.form_submit_button("Add")

            if submit:
                supabase.table("inventory").insert({
                    "item": item,
                    "category": category,
                    "quantity": qty,
                    "reorder_level": reorder_level
                }).execute()
                st.rerun()

    st.divider()

    # =================================================
    # ITEM CARDS (GLOW STYLE)
    # =================================================
    for i in inventory:

        item_id = i["id"]
        name = i["item"]
        category = i["category"]
        qty = i["quantity"]
        reorder = i["reorder_level"]

        # status color logic
        if qty <= 0:
            glow = "#ff3b3b"
            status = "OUT OF STOCK"
        elif qty <= reorder:
            glow = "#ffb020"
            status = "LOW STOCK"
        else:
            glow = "#2ecc71"
            status = "IN STOCK"

        st.markdown(
            f"""
            <div style="
                background:#0f172a;
                border:1px solid {glow};
                box-shadow:0 0 12px {glow};
                padding:16px;
                border-radius:12px;
                margin-bottom:12px;
                color:white;
            ">
                <h3 style="margin:0;">{name}</h3>
                <p style="margin:5px 0;">Category: {category}</p>
                <p style="margin:5px 0;font-size:18px;">
                    Quantity: {qty}
                </p>
                <p style="margin:0;color:{glow};font-weight:bold;">
                    {status}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if st.button("+1", key=f"p1_{item_id}"):
                supabase.table("inventory").update({
                    "quantity": qty + 1
                }).eq("id", item_id).execute()
                st.rerun()

        with col2:
            if st.button("-1", key=f"m1_{item_id}"):

                new_qty = max(0, qty - 1)

                supabase.table("inventory").update({
                    "quantity": new_qty
                }).eq("id", item_id).execute()

                log_usage(name, 1)

                st.rerun()

        with col3:
            if st.button("+5", key=f"p5_{item_id}"):
                supabase.table("inventory").update({
                    "quantity": qty + 5
                }).eq("id", item_id).execute()
                st.rerun()

        with col4:
            if st.button("Delete", key=f"d_{item_id}"):
                supabase.table("inventory").delete().eq("id", item_id).execute()
                st.rerun()

        with col5:
            with st.expander("Settings"):

                new_reorder = st.number_input(
                    "Reorder Level",
                    value=int(reorder),
                    key=f"r_{item_id}"
                )

                if st.button("Save", key=f"s_{item_id}"):

                    supabase.table("inventory").update({
                        "reorder_level": new_reorder
                    }).eq("id", item_id).execute()

                    st.rerun()

# =====================================================
# LOW STOCK
# =====================================================
elif page == "Low Stock":

    st.title("Low Stock")

    for i in inventory:
        if i["quantity"] <= i["reorder_level"]:
            st.warning(f"{i['item']} | Qty: {i['quantity']}")

# =====================================================
# ORDERS
# =====================================================
elif page == "Orders":

    st.title("Orders")

    found = False

    for i in inventory:
        if i["quantity"] <= i["reorder_level"]:
            found = True
            st.info(f"Order more: {i['item']}")

    if not found:
        st.success("No orders needed")

# =====================================================
# USAGE REPORTS
# =====================================================
elif page == "Usage Reports":

    st.title("Usage Reports")

    logs = load_logs()

    if not logs:
        st.info("No usage data yet")
        st.stop()

    st.subheader("Daily Summary")

    daily = {}

    for log in logs:
        key = (log["date"], log["item"])
        daily[key] = daily.get(key, 0) + log["used"]

    for (date, item), total in sorted(daily.items(), reverse=True):
        st.write(f"{date} | {item} | Used: {total}")

    st.divider()

    st.subheader("Monthly Summary")

    monthly = {}

    for log in logs:
        month = log["date"][:7]
        key = (month, log["item"])
        monthly[key] = monthly.get(key, 0) + log["used"]

    for (month, item), total in sorted(monthly.items(), reverse=True):
        st.write(f"{month} | {item} | Used: {total}")
