import streamlit as st
from datetime import datetime
from database import save_sale
from utils import show_receipt
from products import get_products_cached
from cart import add_to_cart, remove_from_cart, calculate_total

# အရေးကြီးဆုံးပြင်ဆင်ချက် - components လမ်းကြောင်းကို အပြည့်အစုံထည့်ပါ
from components.supabase_logic import process_sale_stock_update, insert_sale_to_supabase, supabase

# ==========================================
# 2. Helper Functions (Business Logic)
# ==========================================
def _get_product_display_map(products):
    """Product များကို UI တွင်ပြသရန် Map ဖန်တီးပေးခြင်း"""
    def get_price(r): return float(r.get('sell_price') or r.get('price') or 0)
    
    product_map = {str(r.get('barcode')): r for r in products}
    product_options = {f"{r['product_name']} | ဈေး: {get_price(r):,.0f} | {r.get('barcode')}": r for r in products}
    return product_map, product_options, get_price

def _handle_checkout(cart, totals, payment_method, customer_name):
    """အရောင်းစာရင်းသိမ်းခြင်းနှင့် Stock နုတ်ခြင်းလုပ်ငန်းစဉ်"""
    rec_no = "INV-" + datetime.now().strftime("%Y%m%d%H%M%S")
    totals.update({'payment_method': payment_method, 'customer_name': customer_name or "Walk-in"})
    
    # 1. Local Database (SQLite) operations
    save_sale(cart, totals, receipt_no=rec_no, payment_method=payment_method, customer_name=totals['customer_name'])
    
    # 2. Cloud (Supabase) Stock Update & Sales Logging
    try:
        # Stock update လုပ်ခြင်း
        process_sale_stock_update(cart)
        # Cloud သို့ အရောင်းမှတ်တမ်းပို့ခြင်း
        insert_sale_to_supabase(cart, totals, rec_no, payment_method, totals['customer_name'])
    except Exception as e:
        st.error(f"Cloud Sync အဆင်မပြေပါ။ အော့ဖ်လိုင်းသိမ်းထားပါသည်။ Error: {e}")
    
    # 3. Session update
    st.session_state.update(
        receipt=cart,
        receipt_totals=totals,
        receipt_no=rec_no,
        current_payment_method=payment_method,
        current_customer=totals['customer_name'],
        cart=[]
    )
    st.rerun()

# ==========================================
# 3. Main Run Module (UI Components)
# ==========================================
def show_pos_system():
    st.title("💰 POS System")

    # Receipt display
    if st.session_state.get("receipt"):
        show_receipt(st.session_state.receipt, st.session_state.receipt_totals, st.session_state.receipt_no, 
                     st.session_state.get("current_payment_method", "Cash"), st.session_state.get("current_customer", "Walk-in"))
        if st.button("🖨️ နောက်ထပ်အရောင်းအသစ်"):
            st.session_state.receipt = None
            st.rerun()

    products = get_products_cached()
    if not products: 
        st.warning("ပစ္စည်းစာရင်း မရှိသေးပါ။")
        return

    product_map, product_options, get_price = _get_product_display_map(products)

    # Barcode Scanning
    st.text_input("🔫 Barcode Scan:", key="barcode_input", on_change=lambda: [
        st.session_state.cart.extend(add_to_cart(st.session_state.cart, product_map[str(st.session_state.barcode_input)])) 
        if str(st.session_state.barcode_input) in product_map else None,
        st.session_state.update(barcode_input="")
    ])
    
    # Manual Search
    st.selectbox("🔍 ပစ္စည်းရှာရန်:", [""] + list(product_options.keys()), key="prod_select", 
                 on_change=lambda: st.session_state.cart.extend(add_to_cart(st.session_state.cart, product_options[st.session_state.prod_select])) 
                 if st.session_state.prod_select else None)

    # Cart UI
    if st.session_state.cart:
        for i, item in enumerate(st.session_state.cart):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"{item.get('product_name')} ({get_price(item):,.0f})")
            item['qty'] = col2.number_input("Qty", value=int(item.get('qty', 1)), min_value=1, key=f"q_{i}")
            if col3.button("❌", key=f"del_{i}"):
                st.session_state.cart = remove_from_cart(st.session_state.cart, i)
                st.rerun()

        st.markdown("---")
        col_a, col_b = st.columns(2)
        totals = calculate_total(st.session_state.cart, tax_rate=col_a.number_input("Tax Rate (%)", value=0.0)/100, 
                                 discount=col_b.number_input("Discount (MMK)", value=0))
        
        st.subheader(f"Grand Total: {totals['grand_total']:,.0f} MMK")
        
        # Checkout Actions
        p_col1, p_col2 = st.columns(2)
        method = p_col1.selectbox("💳 ငွေပေးချေမှုပုံစံ:", ["Cash", "Credit (အကြွေး)", "Installment (အရစ်ကျ)"])
        name = p_col2.text_input("👤 ဖောက်သည်အမည်:")
        
        if st.button("✅ Confirm Checkout"):
            if ("Credit" in method or "Installment" in method) and not name:
                st.warning("⚠️ ဖောက်သည်အမည် ထည့်ပေးရန် လိုအပ်ပါသည်။")
            else:
                _handle_checkout(st.session_state.cart, totals, method, name)