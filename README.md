# LaceUp Order Assistant
A Streamlit-based tool that processes messy customer orders and converts them into structured inventory matches with pricing, confidence scoring, and export functionality.

## 🚀 Features

- Fuzzy matching for messy or misspelled customer orders
- Automatic quantity detection
- Confidence scoring (High / Moderate / No Match)
- Interactive UI using Streamlit
- Color-coded match visualization
- Order totals and pricing calculations
- Export options for:
  - Order Review
  - Order Import (for system use)

## 🧠 How It Works

1. User enters a customer order (e.g., "5 oil, 4 rice, 2 beans")
2. The system:
   - Cleans and parses input
   - Matches items using fuzzy matching
   - Assigns confidence levels
   - Calculates pricing
3. Results are displayed in a structured table with visual indicators

## 🛠 Tech Stack

- Python
- Pandas
- Streamlit
- TheFuzz (fuzzy matching)

## ▶️ How to Run

```bash
pip install -r requirements.txt
streamlit run app_ui.py