import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import re
import random
import string

# For PDF export
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

st.set_page_config(page_title="🍔 Restaurant Order & Billing", layout="wide")

# ---------------------------- Data ----------------------------
MENU = [
    {"item": "Classic Burger", "price": 149, "cat": "Burger"},
    {"item": "Cheese Burst Burger", "price": 189, "cat": "Burger"},
    {"item": "Veggie Pizza (8\")", "price": 249, "cat": "Pizza"},
    {"item": "Margherita Pizza (8\")", "price": 269, "cat": "Pizza"},
    {"item": "Fries", "price": 99, "cat": "Sides"},
    {"item": "Peri Peri Fries", "price": 129, "cat": "Sides"},
    {"item": "Iced Tea", "price": 79, "cat": "Beverage"},
    {"item": "Cold Coffee", "price": 119, "cat": "Beverage"},
]
MENU_DF = pd.DataFrame(MENU)
GST_RATE = 0.05  # 5% demo tax

# Sandbox VPAs (for demo verification only)
SANDBOX_VALID_VPAs = {
    "pstest2@yesb", "pstest4@yesb", "pstest6@yesb",
    "pstest7@yesb", "pstest8@yesb", "pstest9@yesb"
}

# ------------------------ Session State ------------------------
if "cart" not in st.session_state:
    st.session_state.cart = {row["item"]: 0 for _, row in MENU_DF.iterrows()}
if "paid" not in st.session_state:
    st.session_state.paid = False
if "payment_meta" not in st.session_state:
    st.session_state.payment_meta = {}

# ------------------------ Helpers ------------------------
def calc_bill():
    rows = []
    subtotal = 0
    for _, r in MENU_DF.iterrows():
        qty = st.session_state.cart.get(r["item"], 0)
        if qty > 0:
            line_total = qty * r["price"]
            subtotal += line_total
            rows.append({"Item": r["item"], "Qty": qty, "Unit Price": r["price"], "Line Total": line_total, "Category": r["cat"]})
    tax = round(subtotal * GST_RATE, 2)
    total = round(subtotal + tax, 2)
    return pd.DataFrame(rows), subtotal, tax, total

def reset_cart():
    st.session_state.cart = {row["item"]: 0 for _, row in MENU_DF.iterrows()}
    st.session_state.paid = False
    st.session_state.payment_meta = {}

def upi_format_valid(vpa: str) -> bool:
    # Basic NPCI-style format check: user@psp
    pattern = r'^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$'
    return bool(re.match(pattern, vpa.strip()))

def upi_demo_verify(vpa: str) -> dict:
    """
    Demo 'verification':
    - If matches sandbox VPAs, return valid with a dummy name.
    - Else, if format is valid, return 'unknown but plausible' (success=False but explain).
    """
    vpa = vpa.strip().lower()
    if vpa in SANDBOX_VALID_VPAs:
        return {"ok": True, "status": "valid", "account_name": "Test User", "note": "Sandbox VPA matched"}
    if upi_format_valid(vpa):
        return {"ok": False, "status": "format-ok", "account_name": None,
                "note": "Format looks valid, but live verification needs a PSP API (not free/no-key)."}
    return {"ok": False, "status": "invalid-format", "account_name": None, "note": "Invalid UPI ID format"}

def gen_receipt_id():
    return "RCPT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def build_invoice_pdf_bytes(order_df: pd.DataFrame, customer_name: str, upi: str, subtotal: float, tax: float, total: float, receipt_id: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    y = height - 20*mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20*mm, y, "🍔 ByteBite Diner")
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, y - 6*mm, "Order Invoice")
    c.drawRightString(width - 20*mm, y, f"Receipt: {receipt_id}")
    c.drawRightString(width - 20*mm, y - 6*mm, datetime.now().strftime("%Y-%m-%d %H:%M"))

    # Customer
    y -= 16*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20*mm, y, "Billed To:")
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, y - 5*mm, customer_name or "Walk-in Customer")
    if upi:
        c.drawString(20*mm, y - 10*mm, f"UPI: {upi}")

    # Table header
    y -= 22*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20*mm, y, "Item")
    c.drawRightString(120*mm, y, "Qty")
    c.drawRightString(150*mm, y, "Unit")
    c.drawRightString(190*mm, y, "Total")

    # Items
    c.setFont("Helvetica", 10)
    y -= 6*mm
    for _, row in order_df.iterrows():
        c.drawString(20*mm, y, str(row["Item"]))
        c.drawRightString(120*mm, y, str(row["Qty"]))
        c.drawRightString(150*mm, y, f"₹{row['Unit Price']:.2f}")
        c.drawRightString(190*mm, y, f"₹{row['Line Total']:.2f}")
        y -= 6*mm
        if y < 40*mm:
            c.showPage()
            y = height - 20*mm

    # Summary
    y -= 6*mm
    c.line(120*mm, y, 190*mm, y)
    y -= 8*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(170*mm, y, "Subtotal:")
    c.drawRightString(190*mm, y, f"₹{subtotal:.2f}")
    y -= 6*mm
    c.drawRightString(170*mm, y, f"Tax ({int(GST_RATE*100)}%):")
    c.drawRightString(190*mm, y, f"₹{tax:.2f}")
    y -= 6*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(170*mm, y, "Total:")
    c.drawRightString(190*mm, y, f"₹{total:.2f}")

    # Footer
    y = 20*mm
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width/2, y, "Thank you for dining with us! This is a computer-generated invoice.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# ------------------------ UI Layout ------------------------
st.title("🍔 Restaurant Order & Billing App")
st.caption("Select items, generate bill, and simulate UPI payment + invoice export.")

left, right = st.columns([7, 5], gap="large")

# ------------------------ LEFT: Menu & Cart ------------------------
with left:
    st.subheader("🧾 Menu")
    # Group by category with expanders
    for cat in sorted(MENU_DF["cat"].unique()):
        with st.expander(f"{cat}", expanded=True):
            cat_df = MENU_DF[MENU_DF["cat"] == cat]
            for _, r in cat_df.iterrows():
                col1, col2, col3 = st.columns([6, 2, 2])
                with col1:
                    st.markdown(f"**{r['item']}**  \n₹{r['price']}")
                with col2:
                    qty = st.number_input(
                        f"Qty_{r['item']}",
                        min_value=0, max_value=20, value=st.session_state.cart[r['item']],
                        step=1, label_visibility="collapsed", key=f"qty_{r['item']}"
                    )
                with col3:
                    if st.button("Add", key=f"add_{r['item']}"):
                        st.session_state.cart[r['item']] = qty

    st.markdown("---")
    st.subheader("🛒 Cart & Bill")
    order_df, subtotal, tax, total = calc_bill()
    if order_df.empty:
        st.info("Your cart is empty. Add some delicious items from the menu!")
    else:
        st.dataframe(order_df[["Item", "Qty", "Unit Price", "Line Total"]], use_container_width=True)
        colA, colB, colC = st.columns(3)
        colA.metric("Subtotal", f"₹{subtotal:.2f}")
        colB.metric(f"Tax ({int(GST_RATE*100)}%)", f"₹{tax:.2f}")
        colC.metric("Payable", f"₹{total:.2f}")

        st.progress(min(1.0, total / 1000))  # playful progress up to ₹1000 goal

        # Small category analytics bar
        cat_totals = (order_df.groupby("Category")["Line Total"].sum().sort_values(ascending=False)).to_dict()
        if cat_totals:
            st.markdown("**🍽️ Spend by Category**")
            for k, v in cat_totals.items():
                st.write(f"{k} (₹{v:.0f})")
                st.progress(min(1.0, v / max(total, 1)))

        # Cart actions
        colx, coly = st.columns([1, 1])
        if colx.button("🧹 Clear Cart"):
            reset_cart()
            st.experimental_rerun() if hasattr(st, "experimental_rerun") else st.rerun()

# ------------------------ RIGHT: Payment & Exports ------------------------
with right:
    st.subheader("💳 Dummy Payment Gateway (UPI)")

    customer_name = st.text_input("Customer Name", placeholder="e.g., Abhinaya")
    upi_id = st.text_input("UPI ID (VPA)", placeholder="e.g., name@bank")
    pay_btn_disabled = order_df.empty if 'order_df' in locals() else True

    if st.button("✅ Verify UPI & Pay", disabled=pay_btn_disabled):
        if order_df.empty:
            st.warning("Please add items to the cart before payment.")
        else:
            result = upi_demo_verify(upi_id)
            if result["status"] == "invalid-format":
                st.error("UPI ID format is invalid. Example: username@bank")
            elif result["ok"]:
                # Simulate success
                rid = gen_receipt_id()
                st.session_state.paid = True
                st.session_state.payment_meta = {
                    "receipt_id": rid,
                    "upi": upi_id,
                    "name": customer_name,
                    "verified": True,
                    "verified_note": result["note"],
                    "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success(f"✅ Payment successful via UPI. Receipt: **{rid}**")
                st.balloons()
            elif result["status"] == "format-ok":
                # Format OK but not verifiable without real API
                rid = gen_receipt_id()
                st.session_state.paid = True  # simulate payment success (demo)
                st.session_state.payment_meta = {
                    "receipt_id": rid,
                    "upi": upi_id,
                    "name": customer_name,
                    "verified": False,
                    "verified_note": result["note"],
                    "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.warning("UPI looks valid")
                st.success(f"✅ Payment simulated. Receipt: **{rid}**")
            else:
                st.error("UPI verification failed. Please check the ID and try again.")

    if st.session_state.paid:
        meta = st.session_state.payment_meta
        st.markdown(
            f"**Receipt:** `{meta.get('receipt_id','')}`  \n"
            f"**Paid By:** {meta.get('name','Walk-in')}  \n"
            f"**UPI:** {meta.get('upi','-')}  \n"
            f"**Verified:** {'Yes' if meta.get('verified') else 'No'}  \n"
            f"_{meta.get('verified_note','')}_"
        )

    st.markdown("---")
    st.subheader("📄 Export Invoice")

    # Build files
    if not order_df.empty:
        # CSV
        csv_bytes = df_to_csv_bytes(order_df.assign(Subtotal=subtotal, Tax=tax, Total=total))
        st.download_button("⬇️ Download CSV", data=csv_bytes, file_name="invoice.csv", mime="text/csv")

        # PDF
        pdf_bytes = build_invoice_pdf_bytes(
            order_df, customer_name, upi_id, subtotal, tax, total,
            st.session_state.payment_meta.get("receipt_id", gen_receipt_id()) if st.session_state.paid else gen_receipt_id()
        )
        st.download_button("⬇️ Download PDF", data=pdf_bytes, file_name="invoice.pdf", mime="application/pdf")
    else:
        st.info("Add items to generate an invoice.")

    st.markdown("---")
    if st.button("🔄 New Order"):
        reset_cart()
        st.experimental_rerun() if hasattr(st, "experimental_rerun") else st.rerun()

