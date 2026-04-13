import pandas as pd
from thefuzz import process

inventory_df = pd.read_csv('inventory.csv')

item_names = list(inventory_df['item_name'])

def process_order(customer_order, item_names):
    results = []
    customer_order = customer_order.replace("\n", ",")
    customer_order = customer_order.split(",")
    total_price = 0
    for item in customer_order:
        if not item.strip():
            continue
        parts = item.strip().split()
        if parts[0].isdigit():
            quantity = int(parts[0])
            item_name = " ".join(parts[1:])
        else:
                quantity = 1
                item_name = item.strip()
        clean_item = item_name.strip().lower()
        best_match = process.extractOne(clean_item, item_names)
        match, score = best_match
        if score >= 90:         
             status = "High confidence match"
        elif score >= 75:
             status = "Moderate confidence match, Review"
        else:             
             status = "No match found"
        
        if status != "No match found":
            price = inventory_df[inventory_df['item_name'] == match]['price'].values[0]
            item_total = price * quantity
            total_price += item_total
            results.append({
                    "item": item.strip(),
                    "match": match,
                    "quantity": quantity,
                    "unit_price": price,
                    "item_total": item_total,
                    "score": score,
                    "status": status
                })
        else:           
            price = None
            item_total = None
            results.append({
                    "item": item.strip(),
                    "match": "No match found",
                    "quantity": quantity,
                    "unit_price": None,
                    "item_total": None,
                    "score": score,
                    "status": status
                })
    return results, total_price