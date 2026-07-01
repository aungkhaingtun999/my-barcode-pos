# ==========================================
# profit_loss.py
# ==========================================

import streamlit as st
import json
import pandas as pd

from database import get_sales
from products import get_products_cached
from config import APP_SETTINGS


# ==========================================
# Helper Function
# ==========================================

def _calculate_detailed_profit(sales, products):

    total_sales = 0
    total_cost = 0

    product_map = {
        str(p.get("barcode")): p
        for p in products
    }


    for sale in sales:

        try:

            # Supabase dictionary format
            if isinstance(sale, dict):

                items_json = sale.get(
                    "items",
                    sale.get("cart", [])
                )

                totals_json = sale.get(
                    "totals",
                    {}
                )


            # Old tuple format
            else:

                items_json = sale[3]

                totals_json = sale[4]


            # JSON decode

            items_data = (
                json.loads(items_json)
                if isinstance(items_json, str)
                else items_json
            )


            totals_data = (
                json.loads(totals_json)
                if isinstance(totals_json, str)
                else totals_json
            )


            if isinstance(totals_data, list):

                totals_data = totals_data[0]


            if not isinstance(totals_data, dict):

                totals_data = {}


            total_sales += float(
                totals_data.get(
                    "grand_total",
                    0
                )
            )


            # Cost Calculation

            if isinstance(items_data, list):

                for item in items_data:

                    barcode = str(
                        item.get(
                            "barcode",
                            ""
                        )
                    )


                    qty = int(
                        item.get(
                            "qty",
                            1
                        )
                    )


                    product = product_map.get(
                        barcode,
                        {}
                    )


                    buy_price = float(
                        product.get(
                            "buy_price",
                            0
                        )
                    )


                    total_cost += (
                        buy_price * qty
                    )


        except Exception:

            continue



    return {

        "total_sales": total_sales,

        "total_cost": total_cost,

        "net_profit": (
            total_sales - total_cost
        )

    }



# ==========================================
# Profit & Loss Page
# ==========================================

def show_profit_loss():

    st.title(
        "📈 Profit & Loss Report"
    )


    sales = get_sales()

    products = get_products_cached()



    if not sales:

        st.info(
            "လက်ရှိတွင် အရောင်းမှတ်တမ်း မရှိသေးပါ။"
        )

        return



    data = _calculate_detailed_profit(
        sales,
        products
    )



    col1, col2, col3 = st.columns(3)



    col1.metric(
        "💰 ရောင်းရငွေ (Sales)",
        f"{data['total_sales']:,.0f} {APP_SETTINGS['currency']}"
    )


    col2.metric(
        "📉 ကုန်ကျစရိတ် (Cost)",
        f"{data['total_cost']:,.0f} {APP_SETTINGS['currency']}"
    )


    col3.metric(
        "📊 အမြတ် (Profit)",
        f"{data['net_profit']:,.0f} {APP_SETTINGS['currency']}"
    )



    st.divider()



    st.subheader(
        "📝 အရောင်းမှတ်တမ်းအသေးစိတ်"
    )



    formatted_sales = []



    for sale in sales:


        try:


            if isinstance(sale, dict):


                totals = sale.get(
                    "totals",
                    {}
                )


                receipt_no = sale.get(
                    "receipt_no",
                    sale.get(
                        "rec_no",
                        ""
                    )
                )


                sale_date = sale.get(
                    "sale_date",
                    ""
                )


            else:


                totals = sale[4]

                receipt_no = sale[1]

                sale_date = sale[2]



            if isinstance(totals, str):

                totals = json.loads(
                    totals
                )



            if isinstance(totals, list):

                totals = totals[0]



            formatted_sales.append({

                "ပြေစာအမှတ်": receipt_no,

                "ရက်စွဲ": sale_date,

                "စုစုပေါင်း (MMK)": float(
                    totals.get(
                        "grand_total",
                        0
                    )
                ),

                "ပေးချေမှု": totals.get(
                    "payment_method",
                    "Cash"
                )

            })



        except Exception:

            continue



    if formatted_sales:


        df = pd.DataFrame(
            formatted_sales
        )


        st.dataframe(

            df,

            use_container_width=True

        )

    else:

        st.info(
            "အရောင်းအသေးစိတ် မရှိပါ။"
        )
