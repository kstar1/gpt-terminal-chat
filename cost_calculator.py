# cost_calculator.py
import datetime

def calculate_spent(start_date=None, end_date=None):
    # Prices per 1k tokens
    prices = {
        "gpt-4o": 0.005,
        "gpt-4": 0.03,
        "gpt-4-turbo": 0.01,
        "gpt-3.5-turbo": 0.0005,
    }

    total_tokens = {}

    if not start_date:
        start_date = datetime.datetime.now() - datetime.timedelta(days=30)
    if not end_date:
        end_date = datetime.datetime.now()

    try:
        with open("token_usage.log", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "Model:" not in line or "Tokens used:" not in line:
                    continue  # Skip invalid lines

                try:
                    timestamp_str = line.split("]")[0][1:]
                    ts = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    if not (start_date <= ts <= end_date):
                        continue

                    model_part = line.split("Model: ")[1]
                    model_name = model_part.split("|")[0].strip()
                    tokens_used = int(model_part.split("Tokens used:")[1].strip())

                    total_tokens[model_name] = total_tokens.get(model_name, 0) + tokens_used

                except Exception as e:
                    print(f"⚠️ Skipping malformed line: {line} -- Error: {e}")

    except FileNotFoundError:
        print("❌ token_usage.log not found!")
        return

    if not total_tokens:
        print(f"No token usage found from {start_date.date()} to {end_date.date()}.")
        return

    total_cost = 0
    print("\n--- Token Usage Breakdown ---")
    for model, tokens in total_tokens.items():
        cost_per_token = prices.get(model, 0) / 1000
        model_cost = cost_per_token * tokens
        total_cost += model_cost
        print(f"{model}: {tokens} tokens -> ${model_cost:.4f}")

    print(f"\nTotal cost from {start_date.date()} to {end_date.date()}: ${total_cost:.4f}")

if __name__ == "__main__":
    calculate_spent()
