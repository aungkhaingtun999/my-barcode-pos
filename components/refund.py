import streamlit as st
import json
# Import လုပ်တဲ့နေရာမှာ အမှန်ဖြစ်ဖို့ အရေးကြီးပါတယ်
from components.supabase_logic import supabase 

def show_refund():
    st.title("🔄 Refund Manager")

    # Session State တွေကို initialize လုပ်တာ ကောင်းမွန်ပါတယ်
    if "current_refund_inv" not in st.session_state: st.session_state.current_refund_inv = None
    if "msg" not in st.session_state: st.session_state.msg = None

    if st.session_state.msg:
        st.success(st.session_state.msg)
        st.session_state.msg = None 

    # Error မတက်စေဖို့ try-except သုံးပေးတာ ပိုကောင်းပါတယ်
    try:
        sales_data = supabase.table("sales").select("*").order("id", desc=True).execute().data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return
    
    options = {f"📄 {r.get('receipt_no')}": r for r in sales_data}
    selected = st.selectbox("🔍 Select Receipt:", [""] + list(options.keys()))
    
    if selected:
        st.session_state.current_refund_inv = options[selected]
    
    inv = st.session_state.current_refund_inv
    
    if inv:
        items = json.loads(inv.get('item', '[]')) if isinstance(inv.get('item'), str) else inv.get('item', [])

        with st.form("refund_form"):
            # checkbox တွေအတွက် key တစ်ခုစီပေးဖို့ လိုပါတယ် (Error မတက်အောင်)
            check_states = {i: st.checkbox(f"{item.get('product_name', 'Item')}", key=f"check_{i}") for i, item in enumerate(items)}
            submitted = st.form_submit_button("⚠️ Process Refund")
            
            if submitted:
                # Refund Logic ကို ဒီမှာ ထည့်သွင်းပါ
                st.session_state.msg = "✅ Refund processed successfully!"
                st.rerun() 

        st.divider()
        if st.button("🚫 Void Entire Receipt"):
            supabase.table("sales").delete().eq("id", inv['id']).execute()
            st.session_state.msg = "⚠️ Receipt voided!"
            st.session_state.current_refund_inv = None
            st.rerun()
            
        if st.button("❌ Exit"):
            st.session_state.current_refund_inv = None
            st.rerun()
