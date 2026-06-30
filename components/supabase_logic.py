import streamlit as st
import json

from datetime import datetime
from supabase import create_client



# ==========================================
# SUPABASE CONNECTION
# ==========================================


@st.cache_resource

def get_supabase():


    url = st.secrets.get(
        "SUPABASE_URL"
    )


    key = st.secrets.get(
        "SUPABASE_KEY"
    )


    if not url or not key:

        return None



    return create_client(
        url,
        key
    )



supabase = get_supabase()



def clear_cache():

    st.cache_data.clear()



# ==========================================
# PRODUCTS
# ==========================================


@st.cache_data(ttl=600)

def get_products_cached():


    if not supabase:

        return []



    result = (
        supabase
        .table("products")
        .select("*")
        .execute()
    )


    return result.data or []





def find_by_barcode(barcode):


    products = get_products_cached()



    for p in products:


        if str(
            p.get("barcode")
        ) == str(barcode):

            return p



    return None




def update_product_stock(
    barcode,
    stock
):


    supabase.table(
        "products"
    ).update(

        {
            "stock":int(stock)
        }

    ).eq(
        "barcode",
        barcode
    ).execute()



    clear_cache()





def process_sale_stock_update(cart):


    for item in cart:


        product=find_by_barcode(
            item["barcode"]
        )


        if product:


            new_stock = (

                int(product.get(
                    "stock",
                    0
                ))

                -

                int(item.get(
                    "qty",
                    1
                ))

            )


            update_product_stock(

                item["barcode"],

                new_stock

            )





# ==========================================
# SALES
# ==========================================


def insert_sale_to_supabase(
    cart,
    totals,
    receipt_no,
    payment_method,
    customer_name
):


    sale = {


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


        "created_at":
            datetime.now().isoformat(),


        "item":
            json.dumps(
                cart,
                ensure_ascii=False
            ),


        "totals":
            json.dumps(
                totals,
                ensure_ascii=False
            )

    }



    return (

        supabase
        .table("sales")
        .insert(sale)
        .execute()

    )





def sync_to_supabase(
    pending_sales
):


    if not supabase:

        raise Exception(
            "Supabase connection မရှိပါ"
        )



    for sale in pending_sales:


        insert_sale_to_supabase(

            sale["cart"],

            sale["totals"],

            sale["rec_no"],

            sale["payment_method"],

            sale["customer"]

        )



    clear_cache()





# ==========================================
# REFUND
# ==========================================


def execute_refund(
    invoice,
    items
):


    amount=0



    for item in items:


        qty=int(
            item.get(
                "qty",
                0
            )
        )


        price=float(
            item.get(
                "sell_price",
                0
            )
        )


        amount += qty * price



        product=find_by_barcode(
            item["barcode"]
        )


        if product:


            update_product_stock(

                item["barcode"],

                int(product["stock"])
                +
                qty

            )



    supabase.table(
        "refunds"
    ).insert(

        {

        "receipt_no":
            invoice["receipt_no"],


        "refund_amount":
            amount,


        "reason":
            json.dumps(
                items,
                ensure_ascii=False
            ),


        "created_at":
            datetime.now().isoformat()

        }

    ).execute()



    return amount
