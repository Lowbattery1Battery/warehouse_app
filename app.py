import streamlit as st
import sqlite3
from datetime import date

# =========================
# PAGE SETUP
# =========================
st.set_page_config(page_title="Warehouse Inventory System", layout="wide")

st.title("Warehouse Inventory System")

# =========================
# DATABASE CONNECTION
# =========================
conn = sqlite3.connect("warehouse.db", check_same_thread=False)
conn.execute("PRAGMA journal_mode=WAL")
c = conn.cursor()

# =========================
# CREATE TABLES
# =========================
c.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT,
    quantity INTEGER,
    reorder_level INTEGER,
    reorder_amount INTEGER,
    category TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT,
    date TEXT,
    uses INTEGER
)
""")

conn.commit()

today = str(date.today())

# =========================
# SAFE USAGE LOGGER
# =========================
def log_usage(item):

    row = conn.execute(
        "SELECT uses FROM usage_log WHERE item=? AND date=?",
        (item, today)
    ).fetchone()

    if row is None:

        conn.execute(
            "INSERT INTO usage_log (item, date, uses) VALUES (?, ?, 1)",
            (item, today)
        )

    else:

        conn.execute(
            "UPDATE usage_log SET uses = uses + 1 WHERE item=? AND date=?",
            (item, today)
        )

# =========================
# LOAD DATA
# =========================
def load_inventory():

    return conn.execute(
        "SELECT * FROM inventory ORDER BY item ASC"
    ).fetchall()

def load_usage():

    return conn.execute(
        "SELECT * FROM usage_log ORDER BY date DESC"
    ).fetchall()

# =========================
# SIDEBAR
# =========================
page = st.sidebar.radio(
    "Navigation",
    ["Inventory", "Order List", "Usage Reports"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Add Item")

item = st.sidebar.text_input("Item Name")

qty = st.sidebar.number_input(
    "Starting Quantity",
    min_value=0,
    value=0
)

reorder = st.sidebar.number_input(
    "Low Stock Trigger",
    min_value=0,
    value=5
)

reorder_amount = st.sidebar.number_input(
    "Order Amount",
    min_value=1,
    value=10
)

category = st.sidebar.selectbox(
    "Category",
    [
        "Housekeeping",
        "Pool",
        "Front Desk",
        "Maintenance",
        "Storage",
        "Other"
    ]
)

if st.sidebar.button("Add Item"):

    if item.strip():

        conn.execute(
            """
            INSERT INTO inventory
            (item, quantity, reorder_level, reorder_amount, category)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                item,
                qty,
                reorder,
                reorder_amount,
                category
            )
        )

        conn.commit()
        st.rerun()

# =========================
# INVENTORY PAGE
# =========================
if page == "Inventory":

    st.subheader("Inventory")

    search = st.text_input("Search Items")

    rows = load_inventory()

    if search:

        rows = [
            r for r in rows
            if search.lower() in r[1].lower()
        ]

    for r in rows:

        item_id = r[0]
        name = r[1]
        qty = r[2]
        reorder_level = r[3]
        reorder_amount = r[4]
        category = r[5]

        low_stock = qty <= reorder_level

        border_color = "#ff4b4b" if low_stock else "#444"

        st.markdown(
            f"""
            <div style="
                border: 2px solid {border_color};
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 15px;
                background-color: #111827;
            ">

            <h3>{name}</h3>

            <b>Category:</b> {category}<br>
            <b>Quantity:</b> {qty}<br>
            <b>Low Stock Trigger:</b> {reorder_level}<br>
            <b>Order Amount:</b> {reorder_amount}

            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        # -1
        with col1:

            if st.button("-1", key=f"minus_{item_id}"):

                if qty > 0:

                    conn.execute(
                        """
                        UPDATE inventory
                        SET quantity = quantity - 1
                        WHERE id=?
                        """,
                        (item_id,)
                    )

                    log_usage(name)

                    conn.commit()
                    st.rerun()

        # +1
        with col2:

            if st.button("+1", key=f"plus1_{item_id}"):

                conn.execute(
                    """
                    UPDATE inventory
                    SET quantity = quantity + 1
                    WHERE id=?
                    """,
                    (item_id,)
                )

                conn.commit()
                st.rerun()

        # +5
        with col3:

            if st.button("+5", key=f"plus5_{item_id}"):

                conn.execute(
                    """
                    UPDATE inventory
                    SET quantity = quantity + 5
                    WHERE id=?
                    """,
                    (item_id,)
                )

                conn.commit()
                st.rerun()

        # +10
        with col4:

            if st.button("+10", key=f"plus10_{item_id}"):

                conn.execute(
                    """
                    UPDATE inventory
                    SET quantity = quantity + 10
                    WHERE id=?
                    """,
                    (item_id,)
                )

                conn.commit()
                st.rerun()

        # DELETE
        with col5:

            if st.button("Delete", key=f"delete_{item_id}"):

                conn.execute(
                    "DELETE FROM inventory WHERE id=?",
                    (item_id,)
                )

                conn.commit()
                st.rerun()

        # =========================
        # SETTINGS DROPDOWN
        # =========================
        with st.expander("Settings"):

            new_low = st.number_input(
                "Low Stock Trigger",
                min_value=0,
                value=reorder_level,
                key=f"low_{item_id}"
            )

            new_order = st.number_input(
                "Order Amount",
                min_value=1,
                value=reorder_amount,
                key=f"order_{item_id}"
            )

            if st.button("Save Settings", key=f"save_{item_id}"):

                conn.execute(
                    """
                    UPDATE inventory
                    SET reorder_level=?,
                        reorder_amount=?
                    WHERE id=?
                    """,
                    (
                        new_low,
                        new_order,
                        item_id
                    )
                )

                conn.commit()
                st.rerun()

# =========================
# ORDER LIST PAGE
# =========================
elif page == "Order List":

    st.subheader("Low Stock Items")

    rows = conn.execute(
        """
        SELECT *
        FROM inventory
        WHERE quantity <= reorder_level
        ORDER BY item ASC
        """
    ).fetchall()

    if not rows:

        st.success("Nothing needs ordering.")

    else:

        for r in rows:

            st.markdown(
                f"""
                <div style="
                    border: 2px solid red;
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 15px;
                    background-color: #1f2937;
                ">

                <h3>{r[1]}</h3>

                <b>Current Quantity:</b> {r[2]}<br>
                <b>Reorder Trigger:</b> {r[3]}<br>
                <b>Suggested Order Amount:</b> {r[4]}

                </div>
                """,
                unsafe_allow_html=True
            )

# =========================
# USAGE REPORTS PAGE
# =========================
elif page == "Usage Reports":

    st.subheader("Usage Reports")

    rows = load_usage()

    if not rows:

        st.info("No usage data yet.")

    else:

        st.dataframe(
            rows,
            use_container_width=True
        )

        st.markdown("---")

        st.subheader("Edit Usage Log")

        options = [
            f"{r[0]} | {r[1]} | {r[2]} | Uses: {r[3]}"
            for r in rows
        ]

        selected = st.selectbox(
            "Select Entry",
            options
        )

        selected_id = int(selected.split("|")[0])

        selected_row = None

        for r in rows:

            if r[0] == selected_id:
                selected_row = r
                break

        new_uses = st.number_input(
            "Uses",
            min_value=0,
            value=selected_row[3]
        )

        c1, c2 = st.columns(2)

        # SAVE
        with c1:

            if st.button("Save Changes"):

                conn.execute(
                    """
                    UPDATE usage_log
                    SET uses=?
                    WHERE id=?
                    """,
                    (
                        new_uses,
                        selected_id
                    )
                )

                conn.commit()
                st.rerun()

        # DELETE
        with c2:

            if st.button("Delete Entry"):

                conn.execute(
                    "DELETE FROM usage_log WHERE id=?",
                    (selected_id,)
                )

                conn.commit()
                st.rerun()