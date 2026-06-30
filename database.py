import streamlit as st
import json

from datetime import datetime

from components.supabase_logic import supabase



# ==========================================
# USER MANAGEMENT
# ==========================================


def get_all_users():

    """
    Return format:

    [
        {
            username:"",
            password:"",
            role:"",
            active:true
        }
    ]

    """

    if not supabase:

        return []


    try:

        result = (
            supabase
            .table("users")
            .select("*")
            .execute()
        )


        return result.data or []


    except Exception as e:

        print(
            f"Get users error : {e}"
        )

        return []





def get_user(username):


    if not supabase:

        return None



    try:


        result = (

            supabase
            .table("users")
            .select("*")
            .eq(
                "username",
                username
            )
            .execute()

        )


        if result.data:

            return result.data[0]


        return None



    except Exception as e:


        print(e)

        return None





def update_password_db(
    username,
    old_password,
    new_password
):


    user = get_user(
        username
    )


    if not user:

        return False



    if user["password"] != old_password:

        return False



    try:


        supabase.table(
            "users"
        ).update(

            {
                "password":
                    new_password
            }

        ).eq(

            "username",
            username

        ).execute()



        return True



    except Exception as e:


        print(e)

        return False






def reset_password(
    username
):


    try:


        result = (

            supabase
            .table("users")
            .update(

                {
                    "password":
                        "123"
                }

            )
            .eq(
                "username",
                username
            )
            .execute()

        )



        return bool(
            result.data
        )



    except Exception as e:


        print(e)

        return False





# ==========================================
# SALES
# ==========================================


def save_sale(
    cart,
    totals,
    receipt_no=None,
    payment_method="Cash",
    customer_name="Walk-in"
):


    if not supabase:

        raise Exception(
            "Supabase connection မရှိပါ"
        )



    try:


        sale_data = {


            "receipt_no":
                receipt_no,


            "customer_name":
                customer_name,


            "payment_method":
                payment_method,


            "grand_total":
                float(
                    totals.get(
                        "grand_total",
                        0
                    )
                ),


            "item":
                json.dumps(
                    cart,
                    ensure_ascii=False
                ),


            "totals":
                json.dumps(
                    totals,
                    ensure_ascii=False
                ),


            "created_at":
                datetime.now().isoformat()

        }



        response = (

            supabase
            .table("sales")
            .insert(
                sale_data
            )
            .execute()

        )


        return response.data



    except Exception as e:


        raise Exception(
            f"Save Sale Error : {e}"
        )





# ==========================================
# SALES REPORT
# ==========================================


def get_sales():


    if not supabase:

        return []



    try:


        result = (

            supabase
            .table("sales")
            .select("*")
            .order(
                "created_at",
                desc=True
            )
            .execute()

        )


        return result.data or []



    except Exception as e:


        print(e)

        return []






def get_report_by_date(
    start_date,
    end_date
):


    if not supabase:

        return []



    try:


        result = (

            supabase
            .table("sales")
            .select("*")
            .gte(
                "created_at",
                start_date.isoformat()
            )
            .lte(
                "created_at",
                end_date.isoformat()
            )
            .execute()

        )


        return result.data or []



    except Exception as e:


        print(e)

        return []





# ==========================================
# PRODUCTS
# ==========================================


def get_products():


    if not supabase:

        return []


    try:


        result = (

            supabase
            .table("products")
            .select("*")
            .execute()

        )


        return result.data or []



    except Exception as e:


        print(e)

        return []






def update_stock(
    barcode,
    qty
):


    try:


        product = (

            supabase
            .table("products")
            .select("*")
            .eq(
                "barcode",
                barcode
            )
            .execute()

        ).data



        if not product:

            return False



        current = product[0].get(
            "stock",
            0
        )



        new_stock = (
            int(current)
            -
            int(qty)
        )



        supabase.table(
            "products"
        ).update(

            {
                "stock":
                    new_stock
            }

        ).eq(

            "barcode",
            barcode

        ).execute()



        return True



    except Exception as e:


        print(e)

        return False
