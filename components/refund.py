import streamlit as st
import json
from components.supabase_logic import supabase

def show_refund():
    st.title("🔄 Refund Manager")

    # [Setup]
    if "current_refund_inv" not in st.session_state: 
        st.session_state.current_refund_inv = None
    if "msg" not in st.session_state: 
        st.session_state.msg = None

    # Message Display
    if st.session_state.msg:
        st.success(st.session_state.msg)
        st.session_state.msg = None 

    # Data Fetching
    if supabase is None:
        st.error("Supabase ကို ချိတ်ဆက်လို့မရပါ။ Secrets ကို စစ်ဆေးပါ။")
        return

    try:
        sales_data = supabase.table("sales").select("*").order("id", desc=True).execute().data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return
    
    # Selection
    options = {f"📄 {r.get('receipt_no')}": r for r in sales_data}
    selected = st.selectbox("🔍 Select Receipt:", [""] + list(options.keys()))
    
    if selected:
        st.session_state.current_refund_inv = options[selected]
    
    inv = st.session_state.current_refund_inv
    
    if inv:
        # Items Handling
        items = inv.get('item', [])
        if isinstance(items, str):
            items = json.loads(items)

        st.subheader(f"Receipt: {inv.get('receipt_no')}")
        
        with st.form("refund_form"):
            # Checkbox တွေအတွက် unique key ပေးထားပါသည်
            check_states = {i: st.checkbox(f"{item.get('product_name', 'Item')}", key=f"item_{i}") for i, item in enumerate(items)}
            submitted = st.form_submit_button("⚠️ Process Refund")
            
            if submitted:
                # Refund logic ထည့်ရန်
                st.session_state.msg = "✅ Refund processed successfully!"
                st.rerun() 

        st.divider()
        # Void Action
        if st.button("🚫 Void Entire Receipt"):
            try:
                supabase.table("sales").delete().eq("id", inv['id']).execute()
                st.session_state.msg = "⚠️ Receipt voided!"
                st.session_state.current_refund_inv = None
                st.rerun()
            except Exception as e:
                st.error(f"Void Error: {e}")
            
        if st.button("❌ Exit"):
            st.session_state.current_refund_inv = None
            st.rerun()
