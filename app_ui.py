import pandas as pd
import streamlit as st
from app import process_order, item_names

def highlight_status(val):
    if val == "High confidence match":
        return 'background-color: #28a745; color: black; font-weight: bold; text-align: center'
    elif val == "Moderate confidence match, Review":
        return 'background-color: #ffc107; color: black; font-weight: bold; text-align: center'
    else:
        return 'background-color: #dc3545; color: black; font-weight: bold; text-align: center'

st.title("LaceUp Order Assistant")

user_input = st.text_input("Enter customer order:")

if st.button("Process Order"):
    if not user_input:
        st.warning("Please enter a customer order to process.")
    else:  
        results, total_price = process_order(user_input, item_names)
        df = pd.DataFrame(results)
        raw_df = pd.DataFrame(results)
        
        df.columns = [
            "Customer Item", 
            "Matched Item", 
            "Quantity", 
            "Unit Price", 
            "Item Total", 
            "Match Score", 
            "Status"
            ]
        
        matched_count = (df["Status"] == "High confidence match").sum()
        review_count = (df["Status"] == "Moderate confidence match, Review").sum()
        no_match_count = (df["Status"] == "No match found").sum()
        st.markdown("### Order Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("High Confidence Matches", matched_count)
        col2.metric("Moderate Matches (Review)", review_count)
        col3.metric("No Matches", no_match_count)
            
        df["Unit Price"] = df["Unit Price"].map(lambda x: f"${x:.2f}" if pd.notna(x) else "")
        df["Item Total"] = df["Item Total"].map(lambda x: f"${x:.2f}" if pd.notna(x) else "")

        csv_data = df.to_csv(index=False)
        raw_csv_data = raw_df.to_csv(index=False)
        
        styled_df = df.style.map(highlight_status, subset=['Status'])

        st.subheader("Order Details")
        st.dataframe(styled_df, use_container_width=True)
        st.success(f"Total Price: ${total_price:.2f}")
        st.download_button(
            "Download Order Review CSV",
            data=csv_data,
            file_name = 'laceup_order.csv',
            mime='text/csv'
        )
        st.download_button(
            "Download Order Import CSV",
            data=raw_csv_data,
            file_name = 'laceup_order_raw.csv',
            mime='text/csv'
        )