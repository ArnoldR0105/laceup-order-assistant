# LaceUp Order Assistant

**Live Demo:** https://laceup-order-assistant.streamlit.app

A Streamlit-based application that processes messy and disorganized customer orders and converts them into structured, inventory-matched outputs with pricing, confidence scoring, and export functionality.

## 🚀 Features

- Fuzzy matching for messy, misspelled, or multilingual (English/Spanish) customer orders  
- Automatic quantity detection (numbers and word-based inputs)  
- Confidence scoring (High / Moderate / No Match)  
- Smart suggestions for ambiguous items 
- Interactive UI using Streamlit with editable order table  
- Real-time quantity updates and price recalculation  
- Order totals and pricing calculations  
- Export options for:
  - **Order Review CSV** (for verification)
  - **Order Import CSV** (structured for system use)
- Image-to-text (OCR) support using Tesseract *(local environment only)*  

## 🧠 How It Works

1. User enters a customer order (e.g., "5 oil, 4 rice, 2 beans") or uploads an image  
2. The system:
   - Cleans and normalizes the input text  
   - Extracts item names and quantities  
   - Matches items against the inventory using fuzzy matching  
   - Assigns confidence levels based on match quality  
3. For ambiguous matches:
   - The system provides multiple suggestions  
   - The user can manually select the correct item  
4. The app:
   - Calculates pricing and totals  
   - Allows inline editing (quantities, removals, overrides)  
5. Final results can be exported as structured CSV files  

## 🛠 Tech Stack

- Python  
- Pandas  
- Streamlit  
- TheFuzz  
- pytesseract (OCR – local only)  

## ▶️ How to Run

```bash
pip install -r requirements.txt
streamlit run app_ui.py