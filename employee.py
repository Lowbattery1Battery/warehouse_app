import streamlit as st
import sqlite3

st.set_page_config(
    page_title="Hotel Supply Status",
    layout="wide"
)

st.title("Hotel Supply Status")

# Connect to database (works locally + Streamlit Cloud)
conn = sqlite3.connect("warehouse.db", check_same_thread=False)

# =========================
# CREATE TABLE (IMPORTANT FIX)
# =========================
conn.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT,
    quantity INTEGER,
    reorder_level INTEGER,
    category TEXT
)
""")

conn.commit()

# =========================
# SEARCH BAR
# =========================
search = st.text_input("Search Supply")

# =========================
# LOAD DATA
# =========================
rows = conn.execute("""
SELECT item, quantity, reorder_level, category
FROM inventory
ORDER BY item
""").fetchall()

if not rows:
    st.info("No inventory found yet.")

# =========================
# DISPLAY ITEMS (READ ONLY)
# =========================
for item, qty, reorder, category in rows:

    if search and search.lower() not in item.lower():
        continue

    # STATUS LOGIC
    if qty == 0:
        status = "Out of Stock"
    elif qty <= reorder:
        status = "Low Stock"
    else:
        status = "Available"

    # CARD DISPLAY
    st.markdown(
        f"""
        <div style="
            border: 1px solid #444;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 10px;
            background-color: #111827;
        ">
            <h3>{item}</h3>

            Category: {category}<br>
            Quantity: {qty}<br>
            Status: {status}
        </div>
        """,
        unsafe_allow_html=True
    )
