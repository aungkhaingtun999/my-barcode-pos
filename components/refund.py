import streamlit as st
import json
from components.supabase_logic import supabase

def show_refund():
    st.title("🔄 Refund Manager")

    # Supabase ချိတ်ဆက်မှုရှိမရှိ စစ်ဆေးခြင်း
    if supabase is None:
        st.error("Supabase ချိတ်ဆက်၍မရပါ။ URL သို့မဟုတ် KEY မှန်ကန်မှုရှိမရှိ စစ်ဆေးပါ။")
        return

    # Session State များ သတ်မှတ်ခြင်း
    if "current_refund_inv" not in st.session_state: st.session_state.current_refund_inv = None
    if "msg" not in st.session_state: st.session_state.msg = None

    if st.session_state.msg:
        st.success(st.session_state.msg)
        st.session_state.msg = None 

    # Data Fetching
    try:
        # ဤနေရာတွင် 'table' attribute ကို အသုံးပြုသည်
        response = supabase.table("sales").select("*").order("id", desc=True).execute()
        sales_data = response.data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return
    
    # UI ပြသခြင်း
    options = {f"📄 {r.get('receipt_no')}": r for r in sales_data}
    selected = st.selectbox("🔍 Select Receipt:", [""] + list(options.keys()))
    
    if selected:
        st.session_state.current_refund_inv = options[selected]
    
    inv = st.session_state.current_refund_inv
    
    if inv:
        items = json.loads(inv.get('item', '[]')) if isinstance(inv.get('item'), str) else inv.get('item', [])
        
        with st.form("refund_form"):
            for i, item in enumerate(items):
                st.checkbox(f"{item.get('product_name', 'Item')}", key=f"item_{i}")
            
            if st.form_submit_button("⚠️ Process Refund"):
                st.session_state.msg = "✅ Refund processed successfully!"
                st.rerun() 

        st.divider()
        if st.button("🚫 Void Entire Receipt"):
            supabase.table("sales").delete().eq("id", inv['id']).execute()
            st.session_state.msg = "⚠️ Receipt voided!"
            st.session_state.current_refund_inv = None
            st.rerun()
