import sys
import os
import socket
import streamlit as st


# ==========================================
# ROOT PATH
# ==========================================

ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)


# ==========================================
# IMPORTS
# ==========================================

from auth import logout, change_password
from language import get_text

from components.supabase_logic import (
    sync_to_supabase
)



# ==========================================
# INTERNET CHECK
# ==========================================

def _check_internet():

    try:
        socket.create_connection(
            ("8.8.8.8",53),
            timeout=2
        )

        return True

    except OSError:

        return False



# ==========================================
# MENU CHANGE
# ==========================================

def _handle_menu_change(menu):

    st.session_state.menu = menu

    try:
        st.query_params["menu"] = menu

    except:
        pass

    st.rerun()



# ==========================================
# SIDEBAR
# ==========================================

def show_sidebar():


    if "lang" not in st.session_state:

        st.session_state.lang="MY"



    if "menu" not in st.session_state:

        st.session_state.menu="POS System"



    with st.sidebar:


        # --------------------------
        # STATUS
        # --------------------------

        c1,c2 = st.columns(2)


        with c1:

            if _check_internet():

                st.success(
                    "🟢 Online"
                )

            else:

                st.error(
                    "🔴 Offline"
                )


        with c2:

            lang = st.selectbox(

                "🌐",

                [
                    "MY",
                    "EN"
                ],

                index=0,

                label_visibility="collapsed"

            )


            st.session_state.lang=lang



        st.divider()



        # --------------------------
        # USER
        # --------------------------

        username = st.session_state.get(
            "username",
            "User"
        )


        role = st.session_state.get(
            "user_role",
            "Cashier"
        )


        st.info(

            f"👤 {username}\n\n"
            f"🛡️ Role : {role}"

        )



        # --------------------------
        # SYNC
        # --------------------------

        if st.button(
            "🔄 Sync Data",
            use_container_width=True
        ):


            pending = st.session_state.get(
                "pending_sales",
                []
            )


            if not pending:

                st.info(
                    "Sync လုပ်ရန် Data မရှိပါ"
                )


            else:


                try:


                    with st.spinner(
                        "Syncing..."
                    ):


                        sync_to_supabase(
                            pending
                        )


                    st.session_state.pending_sales=[]


                    st.success(
                        "✅ Sync Complete"
                    )


                    st.rerun()



                except Exception as e:


                    st.error(
                        f"Sync Failed : {e}"
                    )



        st.divider()



        # --------------------------
        # MENU
        # --------------------------

        menu=[
            "POS System"
        ]


        if role in [
            "Admin",
            "Inventory Manager"
        ]:

            menu.append(
                "Inventory"
            )


        if role=="Admin":

            menu.extend(
                [
                    "Reports",
                    "Profit & Loss",
                    "User Management"
                ]
            )


        menu.append(
            "Refund"
        )



        current = st.session_state.menu


        if current not in menu:

            current="POS System"



        selected = st.radio(

            "📌 Main Menu",

            menu,

            index=menu.index(current)

        )



        if selected != current:

            _handle_menu_change(
                selected
            )



        st.divider()



        # --------------------------
        # PASSWORD
        # --------------------------

        if st.button(
            "🔑 Change Password",
            use_container_width=True
        ):

            st.session_state.show_pwd=True



        if st.session_state.get(
            "show_pwd",
            False
        ):

            change_password()



            if st.button(
                "Close"
            ):

                st.session_state.show_pwd=False

                st.rerun()



        # --------------------------
        # LOGOUT
        # --------------------------

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            logout()
