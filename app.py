import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Warehouse Manager", layout="wide")

# Supabase connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("Warehouse Inventory Manager")

# =========================
# LOAD DATA
# =========================
def load_data():
    return supabase.table("inventory").select("*").execute().data

data = load_data()

# =========================
# ADD ITEM
# =========================
st.subheader("Add Item")

with st.form("add_item"):
    item = st.text_input("Item Name")
    category = st.text_input("Category")
    quantity = st.number_input("Quantity", min_value=0, step=1)
    reorder_level = st.number_input("Reorder Level", min_value=0, step=1)
    reorder_amount = st.number_input("Reorder Amount", min_value=0, step=1)

    submit = st.form_submit_button("Add Item")

    if submit:
        supabase.table("inventory").insert({
            "item": item,
            "category": category,
            "quantity": quantity,
            "reorder_level": reorder_level,
            "reorder_amount": reorder_amount
        }).execute()
        st.success("Item added!")

# =========================
# INVENTORY DISPLAY
# =========================
st.subheader("Inventory")

for row in data:

    item_id = row["id"]
    item = row["item"]
    qty = row["quantity"]
    category = row["category"]
    reorder = row["reorder_level"]

    if qty == 0:
        status = "OUT"
    elif qty <= reorder:
        status = "LOW"
    else:
        status = "OK"

    st.markdown(f"""
    ### {item}
    Category: {category}  
    Quantity: {qty}  
    Status: {status}
    ---
    """)

    col1, col2, col3, col4 = st.columns(4)

    # +1
    with col1:
        if st.button("+1", key=f"p1_{item_id}"):
            supabase.table("inventory").update({
                "quantity": qty + 1
            }).eq("id", item_id).execute()
            st.rerun()

    # -1
    with col2:
        if st.button("-1", key=f"m1_{item_id}"):
            new_qty = max(0, qty - 1)
            supabase.table("inventory").update({
                "quantity": new_qty
            }).eq("id", item_id).execute()
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
