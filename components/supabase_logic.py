import streamlit as st
import json
from components.supabase_logic import supabase

def show_refund():
    st.title("🔄 Refund Manager")

    # 1. Supabase ချိတ်ဆက်မှု စစ်ဆေးခြင်း
    if supabase is None:
        st.error("Database ချိတ်ဆက်၍မရပါ။ Configuration ကို စစ်ဆေးပါ။")
        return

    # 2. Session စတင်ခြင်း
    if "current_refund_inv" not in st.session_state: st.session_state.current_refund_inv = None
    if "msg" not in st.session_state: st.session_state.msg = None

    if st.session_state.msg:
        st.success(st.session_state.msg)
        st.session_state.msg = None 

    # 3. Data Fetching
    try:
        # ဒီနေရာမှာ supabase.table() ကို ခေါ်ပါတယ်
        response = supabase.table("sales").select("*").order("id", desc=True).execute()
        sales_data = response.data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return
    
    # 4. Selection
    options = {f"📄 {r.get('receipt_no')}": r for r in sales_data}
    selected = st.selectbox("🔍 Select Receipt:", [""] + list(options.keys()))
    
    if selected:
        st.session_state.current_refund_inv = options[selected]
    
    inv = st.session_state.current_refund_inv
    
    if inv:
        items = json.loads(inv.get('item', '[]')) if isinstance(inv.get('item'), str) else inv.get('item', [])

        with st.form("refund_form"):
            check_states = {i: st.checkbox(f"{item.get('product_name', 'Item')}", key=f"check_{i}") for i, item in enumerate(items)}
            submitted = st.form_submit_button("⚠️ Process Refund")
            
            if submitted:
                # သင်၏ Refund Logic ကို ဒီမှာ ထည့်ပါ
                st.session_state.msg = "✅ Refund processed successfully!"
                st.rerun() 

        st.divider()
        if st.button("🚫 Void Entire Receipt"):
            try:
                supabase.table("sales").delete().eq("id", inv['id']).execute()
                st.session_state.msg = "⚠️ Receipt voided!"
                st.session_state.current_refund_inv = None
                st.rerun()
            except Exception as e:
                st.error(f"Voiding Error: {e}")
            
        if st.button("❌ Exit"):
            st.session_state.current_refund_inv = None
            st.rerun()
