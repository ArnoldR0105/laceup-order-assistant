import pandas as pd
from thefuzz import process, fuzz
from utility import word_to_num, remove_words
from translations import translations

def normalize_customer_item_text(text):
    text = text.lower().strip()

    for source, target in sorted(translations.items(), key=lambda x: len(x[0]), reverse=True):
        text = text.replace(source, target)

    return text

inventory_df = pd.read_csv("foods_inventory.csv")

inventory_df["normalized_name"] = inventory_df["item_name"].apply(lambda x: normalize_customer_item_text(str(x).strip().lower()))

normalized_to_original = dict(
    zip(inventory_df["normalized_name"], inventory_df["item_name"])
)

item_names = list(inventory_df["normalized_name"])


def process_order(customer_order, item_names):
    results = []
    customer_order = customer_order.replace("\n", ",")
    customer_order = customer_order.split(",")
    total_price = 0
    for item in customer_order:
        if not item.strip():
            continue
        item = item.strip()
        if ":" in item:
             left, right = item.split(":", 1)
             right = right.strip().lower()
             if right.isdigit():
                 quantity = int(right)
                 item_name = left.strip()
             elif right in word_to_num:
                 quantity = word_to_num[right]
                 item_name = left.strip()
             else:
                 quantity = 1
                 item_name = item
        else:
            parts = item.lower().split()
            if parts[0].isdigit():
                quantity = int(parts[0])
                item_name = " ".join(parts[1:])
            elif parts[-1].isdigit():
                quantity = int(parts[-1])
                item_name = " ".join(parts[:-1])
            elif parts[0] in word_to_num:
                quantity = word_to_num[parts[0]]
                item_name = " ".join(parts[1:])
            elif parts[-1] in word_to_num:
                quantity = word_to_num[parts[-1]]
                item_name = " ".join(parts[:-1])
            else:
                    quantity = 1
                    item_name = item
        item_name = " ".join(
            word for word in item_name.split() if word not in remove_words
        )

        clean_item_original = item_name.strip().lower()
        clean_item_helper = normalize_customer_item_text(clean_item_original)
        scored_matches = []
        input_words_original = set(clean_item_original.split())
        input_words_helper = set(clean_item_helper.split())
        for name in item_names:
            token_score_original = fuzz.token_sort_ratio(clean_item_original, name)
            partial_score_original = fuzz.partial_ratio(clean_item_original, name)
            base_score_original = max(token_score_original, partial_score_original)

            token_score_helper = fuzz.token_sort_ratio(clean_item_helper, name)
            partial_score_helper = fuzz.partial_ratio(clean_item_helper, name)
            base_score_helper = max(token_score_helper, partial_score_helper)
            
            name_words = set(name.split())
            common_words_original = input_words_original & name_words
            common_words_helper = input_words_helper & name_words
            
            boost_original = len(common_words_original) * 3
            boost_helper = len(common_words_helper) * 3
            final_score_original = min(base_score_original + boost_original, 100)
            final_score_helper = min(base_score_helper + boost_helper, 100)
            final_score = max(final_score_original, final_score_helper)
            
            scored_matches.append((name, final_score))

        scored_matches.sort(key=lambda x: x[1], reverse=True)

        top_scored = scored_matches[:15]
        filtered_matches = []
        if top_scored:
            best_score = top_scored[0][1]

        for name, score_value in top_scored:
            if best_score - score_value <= 10:
                filtered_matches.append((name, score_value))
            else:
                break
        filtered_matches = filtered_matches[:7]

        top_matches = [normalized_to_original[name] for name, score in filtered_matches]
        if top_scored:
            match = normalized_to_original[top_scored[0][0]]
            score = top_scored[0][1]

            if len(top_scored) > 1:
                second_score = top_scored[1][1]
            else:
                second_score = 0

            score_gap = score - second_score
        else:
            match = None
            score = 0
            second_score = 0
            score_gap = 0

        if score >= 90 and score_gap >= 5:
             status = "High confidence match"
        elif score >= 75:
             status = "Moderate confidence match, Review"
        else:             
             status = "No match found"
        
        if status != "No match found" and match is not None:
            price = inventory_df.loc[
                inventory_df["item_name"] == match, "price"
            ].values[0]
            item_total = price * quantity
            total_price += item_total
            results.append({
                    "item": item.strip(),
                    "match": match,
                    "quantity": quantity,
                    "unit_price": price,
                    "item_total": item_total,
                    "score": score,
                    "status": status,
                    "suggestions": top_matches
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
                    "status": status,
                    "suggestions": top_matches
                })
    return results, total_price