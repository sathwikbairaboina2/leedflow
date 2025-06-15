from fuzzywuzzy import fuzz
import re
import json
import pandas as pd

# dataset = [
#     {"name": "Erik Svensson", "country": "Sweden"},
#     {"name": "Lars Mikkelsen", "country": "Denmark"},
#     {"name": "Kari Nordmann", "country": "Norway"},
#     {"name": "Anna Lund", "country": "Sweden"},
#     {"name": "Nils Bjørnstad", "country": "Norway"},
#     {"name": "Freja Hansen", "country": "Denmark"},
#     {"name": "Tord Hansen", "country": "Denmark"},
# ]

with open("app/utils/dataset.json", "r") as f:
    dataset = json.load(f)


def normalize_name(name):
    """Normalize name: lowercase, trim spaces."""
    return re.sub(r"\s+", " ", name.strip().lower())


def fuzzy_match_names(
    predicted_names, country, dataset, top_n=5, name_weight=0.8, country_weight=0.2
):
    results = []

    normalized_predicted_names = [normalize_name(name) for name in predicted_names]
    country = country.lower()

    for entry in dataset:
        original_name = entry["name"]
        dataset_name_normalized = normalize_name(original_name)
        dataset_country_normalized = entry["country"].lower()

        for i, pred_name in enumerate(normalized_predicted_names):
            name_similarity = fuzz.token_set_ratio(pred_name, dataset_name_normalized)
            country_similarity = fuzz.partial_ratio(country, dataset_country_normalized)

            score = (name_weight * name_similarity) + (
                country_weight * country_similarity
            )

            results.append(
                {
                    "corrected_name": original_name,  # keep original
                    "country": entry["country"],  # keep original
                    "score": round(score, 2),
                    "matched_predicted": predicted_names[i],  # original input
                }
            )

    results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_n]

    return [
        {"corrected_name": r["corrected_name"], "score": r["score"]} for r in results
    ]


def correct_name(predicted_names, country):
    suggestions = fuzzy_match_names(predicted_names, country, dataset)
    suggestions = list({item["corrected_name"] for item in suggestions})
    return suggestions


# # Example usage
# predicted_names = [
#     "Erik svensson",
#     "Ærik svensson",
#     "Erik svensson",
#     "Erik Svænssen",
#     "Ærik Svænssøn",
# ]
# country = "Sweden"

# suggestions = correct_name(predicted_names, country)

# for suggestion in suggestions:
#     print(suggestions)
