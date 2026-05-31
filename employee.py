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
# LOAD INVENTORY
# -----------------------------
def load_inventory():
    data = supabase.table("inventory").select("*").execute().data or []

    return sorted(
        data,
        key=lambda x: x["item"].lower()
    )

# -----------------------------
# PAGE HEADER
# -----------------------------
st.title("Hotel Supply Inventory")
st.caption("View Only Access")

# -----------------------------
# SEARCH
# -----------------------------
search = st.text_input(
    "Search Inventory",
    placeholder="Type an item name..."
)

# -----------------------------
# GET DATA
# -----------------------------
try:
    inventory = load_inventory()

except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

# -----------------------------
# DISPLAY INVENTORY
# -----------------------------
for item in inventory:

    name = item.get("item", "")
    category = item.get("category", "")
    quantity = item.get("quantity", 0)
    reorder_level = item.get("reorder_level", 0)

    # Search filter
    if search:
        if search.lower() not in name.lower():
            continue

    # Status
    if quantity <= 0:
        glow = "#ff3b3b"
        status = "OUT OF STOCK"

    elif quantity <= reorder_level:
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
            border-radius:12px;
            padding:16px;
            margin-bottom:12px;
            color:white;
        ">
            <h3 style="
                margin:0;
                color:white;
            ">
                {name}
            </h3>

            <p style="
                margin:5px 0;
                color:#cbd5e1;
            ">
                Category: {category}
            </p>

            <p style="
                margin:5px 0;
                font-size:18px;
                color:white;
            ">
                Quantity: {quantity}
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
