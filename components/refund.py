import streamlit as st
import json

from components.supabase_logic import (
    supabase,
    execute_refund
)



# ==========================================
# REFUND MANAGER
# ==========================================

def show_refund():


    st.title(
        "🔄 Refund Manager"
    )


    # ======================================
    # SESSION
    # ======================================

    if "current_refund_inv" not in st.session_state:

        st.session_state.current_refund_inv = None


    if "refund_msg" not in st.session_state:

        st.session_state.refund_msg = None



    if st.session_state.refund_msg:

        st.success(
            st.session_state.refund_msg
        )

        st.session_state.refund_msg = None



    # ======================================
    # CHECK DATABASE
    # ======================================

    if not supabase:

        st.error(
            "❌ Supabase Connection မရှိပါ"
        )

        return



    # ======================================
    # LOAD SALES
    # ======================================

    try:

        response = (
            supabase
            .table("sales")
            .select("*")
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )


        sales_data = response.data or []


    except Exception as e:

        st.error(
            f"Sales Load Error : {e}"
        )

        return




    if not sales_data:

        st.info(
            "အရောင်းမှတ်တမ်း မရှိပါ"
        )

        return



    # ======================================
    # RECEIPT SELECT
    # ======================================

    receipt_map = {

        f"📄 {x.get('receipt_no')}":
        x

        for x in sales_data

    }



    selected = st.selectbox(

        "🔍 Select Receipt",

        [
            ""
        ]
        +
        list(receipt_map.keys())

    )



    if selected:


        st.session_state.current_refund_inv = (
            receipt_map[selected]
        )



    invoice = (
        st.session_state.current_refund_inv
    )



    if not invoice:

        return



    # ======================================
    # ITEMS
    # ======================================

    try:

        items = invoice.get(
            "item",
            []
        )


        if isinstance(
            items,
            str
        ):

            items = json.loads(
                items
            )


    except:

        items=[]



    if not items:

        st.warning(
            "ဒီ Invoice မှာ Item မတွေ့ပါ"
        )

        return




    st.subheader(
        f"Invoice : {invoice.get('receipt_no')}"
    )


    st.write(
        f"Customer : {invoice.get('customer_name','Walk-in')}"
    )



    st.divider()



    # ======================================
    # REFUND FORM
    # ======================================


    with st.form(
        "refund_form"
    ):


        selected_items=[]



        for i,item in enumerate(items):


            checked = st.checkbox(

                (
                    f"{item.get('product_name')}"
                    f" | Qty : {item.get('qty',1)}"
                    f" | Price : {item.get('sell_price',0)}"
                ),

                key=f"refund_{i}"

            )


            if checked:

                selected_items.append(
                    item
                )



        submit = st.form_submit_button(
            "⚠️ Process Refund"
        )



        if submit:


            if not selected_items:

                st.warning(
                    "Refund Item ရွေးပါ"
                )

                return



            try:


                amount = execute_refund(

                    invoice,

                    selected_items

                )



                st.session_state.refund_msg = (

                    f"✅ Refund Complete : "
                    f"{amount:,.0f} MMK"

                )



                st.session_state.current_refund_inv=None



                st.rerun()



            except Exception as e:


                st.error(
                    f"Refund Error : {e}"
                )



    st.divider()



    # ======================================
    # VOID RECEIPT
    # ======================================


    if st.button(
        "🚫 Void Entire Receipt",
        use_container_width=True
    ):


        try:


            supabase.table(
                "sales"
            ).delete().eq(

                "id",

                invoice["id"]

            ).execute()



            st.session_state.refund_msg = (
                "⚠️ Receipt Voided"
            )


            st.session_state.current_refund_inv=None


            st.rerun()



        except Exception as e:


            st.error(
                f"Void Error : {e}"
            )




    # ======================================
    # EXIT
    # ======================================


    if st.button(
        "❌ Exit",
        use_container_width=True
    ):


        st.session_state.current_refund_inv=None

        st.rerun()
