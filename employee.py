import streamlit as st
import sqlite3

st.set_page_config(
    page_title="Hotel Supply Status",
    layout="wide"
)

st.title("Hotel Supply Status")

# Database connection
conn = sqlite3.connect(
    "warehouse.db",
    check_same_thread=False
)

# Search box
search = st.text_input("Search Supply")

# Load inventory
rows = conn.execute("""
SELECT
    item,
    quantity,
    reorder_level,
    category
FROM inventory
ORDER BY item
""").fetchall()

if not rows:
    st.info("No inventory found.")

for item, qty, reorder, category in rows:

    if search:
        if search.lower() not in item.lower():
            continue

    # Status text
    if qty == 0:
        status = "Out of Stock"
    elif qty <= reorder:
        status = "Low Stock"
    else:
        status = "Available"

    # Display card
    st.markdown(
        f"""
<div style="
border:2px solid #555;
border-radius:12px;
padding:15px;
margin-bottom:15px;
background-color:#1e1e1e;
">

<h3>{item}</h3>

<p><strong>Category:</strong> {category}</p>

<p><strong>Quantity:</strong> {qty}</p>

<p><strong>Status:</strong> {status}</p>

</div>
""",
        unsafe_allow_html=True
    )