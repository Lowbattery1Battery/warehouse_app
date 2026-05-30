import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Hotel Supply View", layout="wide")

# ----------------------------
# SUPABASE CONNECTION
# ----------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🏨 Hotel Supply Status (Live View)")

search = st.text_input("Search item")

# ----------------------------
# LOAD DATA
# ----------------------------
try:
    data = supabase.table("inventory").select("*").execute().data
except Exception as e:
    st.error(f"Database error: {e}")
    data = []

# ----------------------------
# DISPLAY
# ----------------------------
for row in data:

    item = row["item"]
    qty = row["quantity"]
    category = row["category"]
    reorder = row["reorder_level"]

    if search and search.lower() not in item.lower():
        continue

    if qty <= 0:
        status = "🔴 OUT OF STOCK"
    elif qty <= reorder:
        status = "🟠 LOW STOCK"
    else:
        status = "🟢 AVAILABLE"

    st.markdown(f"""
<div style="
    border:1px solid #333;
    border-radius:10px;
    padding:12px;
    margin-bottom:10px;
">
<h3>{item}</h3>
Category: {category}<br>
Quantity: {qty}<br>
Status: {status}
</div>
""", unsafe_allow_html=True)
