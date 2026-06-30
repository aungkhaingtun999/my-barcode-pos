# ==========================================
# auth.py
# Supabase Authentication
# ==========================================

import streamlit as st
import re

from database import (
    get_all_users,
    update_password_db,
    reset_password as db_reset_password
)



# ==========================================
# SESSION INIT
# ==========================================

def init_auth_state():

    defaults = {

        "logged_in": False,

        "username": None,

        "user_role": None

    }


    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value





# ==========================================
# PASSWORD STRENGTH
# ==========================================

def is_strong(password):

    if len(password) < 8:

        return False


    if not re.search("[a-z]", password):

        return False


    if not re.search("[A-Z]", password):

        return False


    if not re.search("[0-9]", password):

        return False


    if not re.search("[!@#$%^&*]", password):

        return False


    return True





# ==========================================
# LOGOUT
# ==========================================

def logout():

    st.session_state.logged_in = False

    st.session_state.username = None

    st.session_state.user_role = None


    remove_keys = [

        "cart",

        "receipt",

        "receipt_totals",

        "receipt_no",

        "pending_sales",

        "current_customer",

        "current_payment_method",

        "show_pwd_change"

    ]


    for key in remove_keys:

        if key in st.session_state:

            del st.session_state[key]


    st.rerun()





# ==========================================
# LOGIN
# ==========================================

def check_password():

    init_auth_state()


    if st.session_state.logged_in:

        return True



    st.subheader(
        "🔐 Login"
    )


    username = st.text_input(
        "Username"
    )


    password = st.text_input(
        "Password",
        type="password"
    )



    if st.button(
        "Log In",
        use_container_width=True
    ):


        users = get_all_users()


        user_found = None



        # ==============================
        # Supabase List Format
        # ==============================

        if isinstance(users, list):


            for user in users:


                if (
                    str(user.get("username"))
                    ==
                    str(username)
                ):

                    user_found = user

                    break



        # ==============================
        # Dictionary Format Backup
        # ==============================

        elif isinstance(users, dict):


            if username in users:


                user_found = {

                    "username": username,

                    "password": users[username]

                }




        # ==============================
        # Check User
        # ==============================


        if not user_found:


            st.error(
                "❌ Username သို့မဟုတ် Password မှားယွင်းနေပါသည်။"
            )

            return False



        db_password = str(
            user_found.get(
                "password",
                ""
            )
        )


        input_password = str(
            password
        )



        if db_password != input_password:


            st.error(
                "❌ Username သို့မဟုတ် Password မှားယွင်းနေပါသည်။"
            )

            return False




        # Active Check

        if (
            "active" in user_found
            and
            user_found["active"] is False
        ):


            st.error(
                "❌ User account ပိတ်ထားပါသည်။"
            )

            return False




        # Success


        st.session_state.logged_in = True

        st.session_state.username = (

            user_found.get(
                "username"
            )

        )


        st.session_state.user_role = (

            user_found.get(
                "role",
                "Cashier"
            )

        )


        st.success(
            "✅ Login Successful"
        )


        st.rerun()



    return False





# ==========================================
# CHANGE PASSWORD
# ==========================================

def change_password():

    st.subheader(
        "🔑 Password ပြောင်းလဲခြင်း"
    )


    username = st.session_state.get(
        "username"
    )


    old_password = st.text_input(
        "Old Password",
        type="password",
        key="old_password"
    )


    new_password = st.text_input(
        "New Password",
        type="password",
        key="new_password"
    )


    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="confirm_password"
    )



    if st.button(
        "Update Password",
        use_container_width=True
    ):



        if new_password != confirm_password:


            st.error(
                "❌ Password အသစ်မတူပါ"
            )

            return



        if not is_strong(new_password):


            st.warning(
                "⚠️ Password သည် ၈ လုံးအထက်၊ စာလုံးအကြီး၊ အသေး၊ ဂဏန်းနှင့် သင်္ကေတ ပါရမည်"
            )

            return




        success = update_password_db(

            username,

            old_password,

            new_password

        )



        if success:


            st.success(
                "✅ Password ပြောင်းပြီးပါပြီ"
            )


        else:


            st.error(
                "❌ Password အဟောင်းမှားနေပါသည်"
            )






# ==========================================
# RESET PASSWORD
# ==========================================

def reset_password(username):


    return db_reset_password(
        username
    )
