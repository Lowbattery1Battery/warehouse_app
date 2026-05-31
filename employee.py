import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Hotel Supply View",
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

# -----------------------------
# SEARCH BAR
# -----------------------------
search = st.text_input(
    "Search Inventory",
    placeholder="Search by item name..."
)

# -----------------------------
# GET INVENTORY
# -----------------------------
try:
    inventory = load_inventory()
except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

# -----------------------------
# DISPLAY ITEMS
# -----------------------------
for item in inventory:

    name = item["item"]
    category = item["category"]
    qty = item["quantity"]
    reorder = item["reorder_level"]

    if search:
        if search.lower() not in name.lower():
            continue

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

            <p style="margin:5px 0;">
                Category: {category}
            </p>

            <p style="margin:5px 0; font-size:18px;">
                Quantity: {qty}
            </p>

            <p style="
                margin:0;
                color:{glow};
                font-weight:bold;
            ">
                {status}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
