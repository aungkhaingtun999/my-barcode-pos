# ==========================================
# auth.py
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

    if "logged_in" not in st.session_state:

        st.session_state.logged_in = False


    if "username" not in st.session_state:

        st.session_state.username = None


    if "user_role" not in st.session_state:

        st.session_state.user_role = None



# ==========================================
# PASSWORD CHECK
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

    st.session_state.logged_in=False

    st.session_state.username=None

    st.session_state.user_role=None


    clear_keys=[

        "cart",
        "receipt",
        "receipt_totals",
        "receipt_no",
        "pending_sales",
        "show_pwd"

    ]


    for key in clear_keys:

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
        "Log In"
    ):


        users = get_all_users()


        user_found=None



        # database.py က list ပြန်ရင်

        if isinstance(users,list):

            for user in users:

                if (
                    user.get("username")
                    ==
                    username
                ):

                    user_found=user

                    break



        # database.py က dict ပြန်ရင်

        elif isinstance(users,dict):

            if username in users:

                user_found={

                    "username":username,

                    "password":users[username]

                }



        if user_found:


            if user_found.get(
                "password"
            ) == password:



                # Active check

                if user_found.get(
                    "active",
                    True
                ):


                    st.session_state.logged_in=True

                    st.session_state.username=username


                    st.session_state.user_role=(

                        user_found.get(
                            "role",
                            "Cashier"
                        )

                    )


                    st.success(
                        "✅ Login Successful"
                    )

                    st.rerun()



                else:

                    st.error(
                        "User ပိတ်ထားပါသည်"
                    )


            else:

                st.error(
                    "❌ Username သို့မဟုတ် Password မှားယွင်းနေပါသည်။"
                )


        else:

            st.error(
                "❌ Username သို့မဟုတ် Password မှားယွင်းနေပါသည်။"
            )



    return False





# ==========================================
# PASSWORD CHANGE
# ==========================================

def change_password():


    st.subheader(
        "🔑 Password ပြောင်းလဲခြင်း"
    )


    user = st.session_state.get(
        "username"
    )


    old = st.text_input(
        "Old Password",
        type="password"
    )


    new = st.text_input(
        "New Password",
        type="password"
    )


    confirm = st.text_input(
        "Confirm Password",
        type="password"
    )



    if st.button(
        "Update Password"
    ):


        users=get_all_users()


        current=None



        for u in users:

            if u["username"]==user:

                current=u["password"]

                break



        if current != old:

            st.error(
                "Password အဟောင်းမှားနေပါသည်"
            )

            return



        if new != confirm:

            st.error(
                "Password အသစ်မတူပါ"
            )

            return



        update_password_db(
            user,
            new
        )


        st.success(
            "✅ Password ပြောင်းပြီးပါပြီ"
        )





# ==========================================
# RESET PASSWORD
# ==========================================

def reset_password(username):


    result = db_reset_password(
        username
    )


    return result
