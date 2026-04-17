import pandas as pd
import streamlit as st
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
from PIL import Image
from app import process_order, item_names, inventory_df

COLUMN_NAMES = [
    "Customer Item",
    "Matched Item",
    "Quantity",
    "Unit Price",
    "Item Total",
    "Match Score",
    "Status",
    "Suggestions",
    "Selected Match",
    "Remove"
]

def ocr_function(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return ""

def clean_ocr_text(text):
    lines = text.splitlines()
    cleaned_lines = []

    ignore_words = {
        "total", "subtotal", "tax", "thank", "thanks", "receipt",
        "invoice", "date", "phone", "address", "cash", "card"
    }

    number_words = {
        "one", "two", "three", "four", "five",
        "six", "seven", "eight", "nine", "ten",
        "uno", "dos", "tres", "cuatro", "cinco",
        "seis", "siete", "ocho", "nueve", "diez"
    }

    inventory_keywords = set()
    for name in item_names:
        for word in name.split():
            inventory_keywords.add(word)

    for line in lines:
        line = line.strip()
        if not line:
            continue

        lower_line = line.lower()

        if any(word in lower_line for word in ignore_words):
            continue

        words = lower_line.split()

        has_digit = any(word.isdigit() for word in words)
        has_number_word = any(word in number_words for word in words)
        has_inventory_word = any(word in inventory_keywords for word in words)

        if has_inventory_word and (has_digit or has_number_word):
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def clear_order():
    st.session_state.raw_df = None
    st.session_state.order_input = ""
    st.session_state.selected_suggestions = {}
    

def highlight_status(val):
    if val == "High confidence match":
        return 'background-color: #28a745; color: black; font-weight: bold; text-align: center'
    elif val == "Moderate confidence match, Review":
        return 'background-color: #ffc107; color: black; font-weight: bold; text-align: center'
    else:
        return 'background-color: #dc3545; color: black; font-weight: bold; text-align: center'

if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "order_input" not in st.session_state:
    st.session_state.order_input = ""
if "selected_suggestions" not in st.session_state:
    st.session_state.selected_suggestions = {}
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""

st.title("LaceUp Order Assistant")

col1, col2 = st.columns([4, 1])

with col1:
    upload_file = st.file_uploader("Upload order photo", type=["png", "jpg", "jpeg"])
    if upload_file is not None:
        if st.button("Extract Text from Photo"):
            extracted_text = ocr_function(upload_file)
            cleaned_text = clean_ocr_text(extracted_text)
            st.session_state.ocr_text = extracted_text
            st.session_state.order_input = cleaned_text
            st.rerun()
    user_input = st.text_area("Enter customer order:", key="order_input")

with col2:
    st.write("")
    st.write("")
    st.button("Clear Order", on_click=clear_order)

if st.button("Process Order"):
    if not user_input.strip():
        st.warning("Please enter a customer order to process.")
    else:  
        results, total_price = process_order(user_input, item_names)
        st.session_state.raw_df = pd.DataFrame(results)
        st.session_state.raw_df["selected_match"] = ""
        st.session_state.raw_df["remove"] = False
        st.session_state.selected_suggestions = {}
if st.session_state.raw_df is not None:      
    display_df = st.session_state.raw_df.copy()     
    display_df.columns = COLUMN_NAMES
    
    matched_count = (display_df["Status"] == "High confidence match").sum()
    review_count = (display_df["Status"] == "Moderate confidence match, Review").sum()
    no_match_count = (display_df["Status"] == "No match found").sum()
    
    st.markdown("### Order Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("High Confidence Matches", matched_count)
    col2.metric("Moderate Matches (Review)", review_count)
    col3.metric("No Matches", no_match_count)
    
    st.subheader("Order Details")
    edited_df = st.data_editor(
        display_df,
        use_container_width=True,
        hide_index=True,
        disabled=[
            "Customer Item",
            "Matched Item",
            "Unit Price",
            "Item Total",
            "Match Score",
            "Status",
            "Suggestions"
        ],
        column_config={
            "Quantity": st.column_config.NumberColumn(
                "Quantity",
                min_value=1,
                step=1,
                format="%d"
            ),
            "Unit Price": st.column_config.NumberColumn(
                "Unit Price",
                format="$%.2f"
            ),
            "Item Total": st.column_config.NumberColumn(
                "Item Total",
                format="$%.2f"
            ),
            "Match Score": st.column_config.NumberColumn(
                "Match Score",
                format="%d"
            ),
            "Selected Match": st.column_config.TextColumn(
                "Selected Match"
            ),
            "Remove": st.column_config.CheckboxColumn(
                "Remove"
            )
        }
    )

    
    st.markdown("### Submit Suggestion(s)")
    for i in range(len(st.session_state.raw_df)):
        row_status = st.session_state.raw_df.loc[i, "status"]
        row_suggestions = st.session_state.raw_df.loc[i, "suggestions"]
        customer_item = st.session_state.raw_df.loc[i, "item"]
        current_selected = st.session_state.raw_df.loc[i, "selected_match"]

        should_show_suggestion_box = (
            row_status in ["Moderate confidence match, Review", "No match found", "User selected match"]
            or current_selected != ""
        )

        if should_show_suggestion_box:
            if isinstance(row_suggestions, list) and len(row_suggestions) > 0:
                options = [""] + row_suggestions

                if current_selected and current_selected not in options:
                    options.append(current_selected)

                default_value = st.session_state.selected_suggestions.get(i, current_selected)

                if default_value not in options:
                    default_value = ""

                st.session_state.selected_suggestions[i] = st.selectbox(
                    f"Choose match for: {customer_item}",
                    options=options,
                    index=options.index(default_value),
                    key=f"suggestion_select_{i}"
                )
        
    if st.button("Confirm Changes"):
        if edited_df["Quantity"].isna().any():
            st.error("Quantity cannot be empty")
        elif (edited_df["Quantity"] < 1).any():
            st.error("Quantity must be at least 1")
        elif not (edited_df["Quantity"] % 1 == 0).all():
            st.error("Quantity must be a whole number.")
        else:
            st.session_state.raw_df["quantity"] = edited_df["Quantity"]
            st.session_state.raw_df["item_total"] = (
                st.session_state.raw_df["quantity"] * st.session_state.raw_df["unit_price"]
            )
            st.session_state.raw_df["remove"] = edited_df["Remove"]
            for i in range(len(st.session_state.raw_df)):
                selected = st.session_state.selected_suggestions.get(i, "")
                if selected:
                    price = inventory_df.loc[
                        inventory_df["item_name"] == selected, "price"
                        ].values[0]

                    st.session_state.raw_df.loc[i, "match"] = selected
                    st.session_state.raw_df.loc[i, "unit_price"] = price
                    st.session_state.raw_df.loc[i, "item_total"] = (
                        price * st.session_state.raw_df.loc[i, "quantity"]
                    )
                    st.session_state.raw_df.loc[i, "status"] = "User selected match"
                    st.session_state.raw_df.loc[i, "selected_match"] = selected
            st.success("Changes confirmed.")
    display_df = st.session_state.raw_df.copy()
    display_df.columns = COLUMN_NAMES
    display_df["Suggestions"] = display_df["Suggestions"].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    display_df.loc[display_df["Status"] == "High confidence match","Suggestions"] = ""
    
    review_export_df = display_df.copy()
    review_export_df = review_export_df.drop(columns=["Selected Match", "Remove"], errors="ignore")
    review_csv = review_export_df.to_csv(index=False)
    
    import_df = st.session_state.raw_df.copy()
    import_df = import_df[import_df["remove"] == False]
    excluded_no_match_count = (import_df["status"] == "No match found").sum()
    import_df = import_df[import_df["status"] != "No match found"]
    import_df = import_df[["match", "quantity", "unit_price", "item_total"]]
    import_df.columns = ["item_name", "quantity", "unit_price", "item_total"]
    
    import_csv = import_df.to_csv(index=False)
    
    filtered_df = st.session_state.raw_df[st.session_state.raw_df["remove"] == False]
    total_price = filtered_df["item_total"].fillna(0).sum()
    st.success(f"Total Price: ${total_price:.2f}")
    
    if excluded_no_match_count > 0:
        st.warning(
            f"{excluded_no_match_count} unresolved row(s) with 'No match found' were excluded from the import file."
        )
    st.download_button(
        "Download Order Review CSV",
        data=review_csv,
        file_name = 'laceup_order_review.csv',
        mime='text/csv'
    )
    st.download_button(
        "Download Order Import CSV",
        data=import_csv,
        file_name = 'laceup_order_import.csv',
        mime='text/csv'
    )