
import csv

def calculate_answerability_rate(filename):
    total = 0
    answered = 0

    with open(filename, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            total += 1
            prediction = (row.get("predicted_sql") or "").strip()
            normalized = prediction.rstrip(";").strip().upper()

            if normalized != "SELECT NULL":
                answered += 1

    abstentions = total - answered
    answerability_rate = (answered / total * 100) if total else 0

    return {
        "total_predictions": total,
        "non_abstained_predictions": answered,
        "abstentions": abstentions,
        "answerability_rate": answerability_rate,
    }


results1 = calculate_answerability_rate(
    "RTF_restaurants_dataset_predictions.csv"
)

print("RTF Restaurants Dataset Predictions:")
print(f"Total predictions: {results1['total_predictions']}")
print(f"Non-abstained predictions: {results1['non_abstained_predictions']}")
print(f"Abstentions: {results1['abstentions']}")
print(f"Answerability Rate: {results1['answerability_rate']:.2f}%")

results2 = calculate_answerability_rate(
    "RACE_restaurants_dataset_predictions.csv"
)

print("RACE Restaurants Dataset Predictions:")
print(f"Total predictions: {results2['total_predictions']}")
print(f"Non-abstained predictions: {results2['non_abstained_predictions']}")
print(f"Abstentions: {results2['abstentions']}")
print(f"Answerability Rate: {results2['answerability_rate']:.2f}%")


results3 = calculate_answerability_rate(
    "ICIO_restaurants_dataset_predictions.csv"
)

print("ICIO Restaurants Dataset Predictions:")
print(f"Total predictions: {results3['total_predictions']}")
print(f"Non-abstained predictions: {results3['non_abstained_predictions']}")
print(f"Abstentions: {results3['abstentions']}")
print(f"Answerability Rate: {results3['answerability_rate']:.2f}%")
