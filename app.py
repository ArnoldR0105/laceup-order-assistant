import pandas as pd
from thefuzz import process, fuzz
from utility import word_to_num, remove_words

inventory_df = pd.read_csv("jcfoods_inventory.csv")

inventory_df["normalized_name"] = inventory_df["item_name"].str.strip().str.lower()

normalized_to_original = dict(
    zip(inventory_df["normalized_name"], inventory_df["item_name"])
)

item_names = list(inventory_df["normalized_name"])

def normalize_customer_item_text(text):
    text = text.lower().strip()

    replacements = {
    # Existing order-language fixes
    "gandulez": "gandules",
    "gandules": "gandules frozen",
    "bacalao": "bacalao salted cod",
    "bacalao salado": "bacalao salted cod",
    "naranja agria": "sour orange naranja agria",
    "surillo": "sour orange naranja agria",
    "orange bitter": "bitter orange marinade",
    "mango pulp": "mango frozen pulp",
    "frozen mango pulp": "mango frozen pulp",
    "yuca rellena": "yuca rellena",
    "margarina": "margarine",
    "beef base": "beef base concentrate",
    "salsa tomato": "tomato sauce",
    "salsa de tomate": "tomato sauce",
    "pure de tomate": "tomato puree",
    "purre de tomate": "tomato puree",
    "purrre de tomate": "tomato puree",
    "mostaza": "mustard",
    "queso suizo": "swiss cheese",
    "pan cubano": "cuban bread",
    "malta tan bueno": "malta tan bueno",
    "madro tan bueno": "malta tan bueno",
    "platanos verdes": "plantains green",
    "platanos maduros": "plantains ripe",
    "aceite vegetal": "cooking oil vegetable",
    "aceite de oliva": "olive oil",
    "leche evaporada": "evaporated milk",
    "servilletas": "napkins 3 ply",
    "yuca": "yuca",
    "masa de yuca": "masa de yuca",
    "yuca frita": "yuca fries",
    "yuca fries": "yuca fries",
    "yuca cheese bites": "yuca cheese bites",
    "stuffed cassava": "yuca rellena",
    "cassava": "yuca",
    "arroz": "rice",
    "arroz rico": "rice rico",
    "arroz blanco": "white rice",
    "arroz jazmin": "jasmine rice",
    "arroz jasmin": "jasmine rice",
    "arroz largo": "long grain rice",
    "arroz de grano largo": "long grain rice",
    "parboiled rice": "parboiled rice",
    "aceituna negra": "black olives",
    "aceitunas negras": "black olives",
    "adobo con cumino": "adobo cumin",
    "adobo con comino": "adobo cumin",
    "adobo sin pimienta": "adobo without pepper",
    "adobo con pimienta": "adobo with pepper",
    "adobo sin pimiento": "adobo without pepper",
    "adobo con pimiento": "adobo with pepper",
    "aji amarillo": "aji amarillo",
    "aji amarillo poco picante": "aji amarillo mild",
    "aji panca": "aji panca",
    "aji panca poco picante": "aji panca mild",
    "pasta aji amarillo": "aji amarillo paste",
    "pasta aji panca": "aji panca paste",
    "maracumango": "maracumango pulp",
    "mora": "blackberry pulp",
    "nance": "nance pulp",
    "moro": "moro fruit",
    "okra": "okra",
    "whole okra": "whole okra",
    "cut okra": "cut okra",
    "palitos de queso": "cheese sticks",
    "pan de yuca": "pan de yuca",
    "pan de bono": "pan de bono",
    "pan sobao": "pan sobao",
    "pan soba": "pan sobao",
    "pan de mantequilla": "butter bread",
    "media noche": "media noche",
    "pan puertorriqueno": "puerto rican bread",
    "pan puertorriqueño": "puerto rican bread",
    "toston": "toston",
    "tostones": "tostones",
    "patacon": "toston patacon",
    "patacones": "toston patacon",
    "tostones de pana": "breadfruit tostones",
    "toston de pana": "breadfruit tostones",
    "masa alcapurria": "masa alcapurria",
    "masa guineo": "masa guineo",
    "masa malanga": "masa malanga",
    "malanga": "malanga root",
    "molasse dominicana": "dominican molasses",
    "melaza dominicana": "dominican molasses",
    "melaza": "molasses",
    "manteca": "lard",
    "huevos": "eggs",
    "jamon": "ham",
    "jamon serrano": "serrano ham",
    "jamon viejo": "aged ham",
    "jamonada": "ham loaf",
    "mortadella": "mortadella",
    "lomo": "pork loin",
    "costilla": "ribs",
    "tocino": "bacon",
    "chicharrones": "pork rinds",
    "chorizo molido": "ground chorizo",
    "chorizo mexicano": "mexican chorizo",
    "chorizo toscana": "toscana sausage",
    "chistorra": "chistorra",
    "cantimpalo": "cantimpalo",
    "salchichon": "salchichon",
    "morcilla": "blood sausage",
    "calamares": "squid",
    "mejillones": "mussels",
    "sardinas": "sardines",
    "paella": "paella",
    "corazon de palma": "hearts of palm",
    "corazones de palma": "hearts of palm",
    "alcachofa": "artichoke",
    "alcachofas": "artichokes",
    "queso": "cheese",
    "queso crema": "cream cheese",
    "queso amarillo": "yellow cheese",
    "queso blanco": "white cheese",
    "queso suizo": "swiss cheese",
    "queso de papa": "potato cheese",
    "pan de yucca": "pan de yuca",
    "aji": "aji",
    "pimienta": "pepper",
    "cumino": "cumin",
    "comino": "cumin"
}

    for source, target in replacements.items():
        text = text.replace(source, target)

    return text

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