import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Hotel Supply Inventory",
    layout="wide"
)

# -----------------------------
# SUPABASE
# -----------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

# -----------------------------
# LOAD DATA
# -----------------------------
def load_inventory():
    data = supabase.table("inventory").select("*").execute().data or []
    return sorted(data, key=lambda x: x["item"].lower())

# -----------------------------
# PAGE HEADER
# -----------------------------
st.title("Hotel Supply Inventory")
st.caption("View Only Access")

search = st.text_input(
    "Search Inventory",
    placeholder="Search by item name..."
)

try:
    inventory = load_inventory()
except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

# -----------------------------
# DISPLAY INVENTORY
# -----------------------------
for item in inventory:

    name = item["item"]
    category = item["category"]
    quantity = item["quantity"]
    reorder_level = item["reorder_level"]

    if search and search.lower() not in name.lower():
        continue

    if quantity <= 0:
        status = "OUT OF STOCK"
        border = "🔴"

    elif quantity <= reorder_level:
        status = "LOW STOCK"
        border = "🟠"

    else:
        status = "IN STOCK"
        border = "🟢"

    with st.container(border=True):
        st.subheader(f"{border} {name}")
        st.write(f"Category: {category}")
        st.write(f"Quantity: {quantity}")
        st.write(f"Status: {status}")
