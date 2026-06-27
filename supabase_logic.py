import streamlit as st
import json
from supabase import create_client
from datetime import datetime
from config import SUPABASE_CONFIG 

# ==========================================
# 1. Connection Initialization
# ==========================================
@st.cache_resource
def _get_client():
    url = SUPABASE_CONFIG.get("url")
    key = SUPABASE_CONFIG.get("key")
    if not url or not key:
        return None
    return create_client(url, key)

supabase = _get_client()

def _clear_cache():
    st.cache_data.clear()

# ==========================================
# 2. Product & Stock Management
# ==========================================
def get_products_cached():
    if not supabase: return []
    try:
        response = supabase.table("products").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        # အင်တာနက်မရတဲ့အခါ error ကို log ပဲထုတ်ပြီး အလုပ်မရပ်သွားအောင် လုပ်ခြင်း
        print(f"Error fetching products: {e}") 
        return []

def find_by_barcode(barcode):
    products = get_products_cached()
    return next((p for p in products if str(p.get("barcode")) == str(barcode)), None)

def update_product_stock(barcode, new_stock):
    """Stock update လုပ်ခြင်း"""
    try:
        supabase.table("products").update({"stock_qty": int(new_stock)}).eq("barcode", barcode).execute()
        _clear_cache()
    except Exception as e:
        st.error(f"Error updating stock for {barcode}: {e}")
        raise e

def process_sale_stock_update(cart):
    """အရောင်းဖြစ်တိုင်း Stock အလိုအလျောက် နုတ်ပေးခြင်း"""
    for item in cart:
        barcode = str(item.get("barcode"))
        product = find_by_barcode(barcode)
        if product:
            new_stock = int(product.get("stock_qty", 0)) - int(item.get("qty", 0))
            update_product_stock(barcode, new_stock)

def reverse_stock_update(barcode, qty_to_add):
    """Refund လုပ်ပါက Stock ပြန်ဖြည့်ခြင်း"""
    product = find_by_barcode(barcode)
    if product:
        new_stock = int(product.get("stock_qty", 0)) + int(qty_to_add)
        update_product_stock(barcode, new_stock)

# ==========================================
# 3. Sales & Refund Records
# ==========================================
def insert_sale_to_supabase(cart, totals, receipt_no, payment_method, customer_name):
    """Cloud Database သို့ အရောင်းမှတ်တမ်းသိမ်းခြင်း"""
    if not supabase:
        raise Exception("Database Connection မရှိပါ။")
    
    try:
        data = {
            "receipt_no": receipt_no,
            "customer_name": customer_name,
            "grand_total": float(totals.get("grand_total", 0)),
            "payment_type": payment_method,
            "created_at": datetime.now().isoformat(),
            "item": json.dumps(cart, ensure_ascii=False),
            "totals": json.dumps(totals, ensure_ascii=False)
        }
        return supabase.table("sales").insert(data).execute()
    except Exception as e:
        st.error(f"Cloud Sync Error: {e}")
        raise e

def execute_refund(inv, items_to_refund):
    """Refund လုပ်ဆောင်ခြင်း"""
    total_refunded = 0
    try:
        for item in items_to_refund:
            barcode = str(item.get('barcode'))
            qty = int(item.get('qty', 0))
            reverse_stock_update(barcode, qty)
            
            price = float(item.get('sell_price') or item.get('price') or 0)
            total_refunded += (price * qty)
        
        refund_data = {
            "receipt_no": inv.get('receipt_no'),
            "items": json.dumps(items_to_refund, ensure_ascii=False),
            "refund_amount": float(total_refunded),
            "refunded_at": datetime.now().isoformat()
        }
        supabase.table("refunds").insert(refund_data).execute()
        return total_refunded
    except Exception as e:
        st.error(f"Refund လုပ်ဆောင်ချက် အမှားအယွင်း: {e}")
        raise e

def log_refund(receipt_no, items, total_refunded):
    """Refund Log ရေးမှတ်ခြင်း"""
    pass