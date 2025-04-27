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

    with open("token_usage.log", "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) != 2:
                continue
            timestamp_str, model_part = parts[0], parts[1]
            ts = datetime.datetime.strptime(timestamp_str[1:20], "%Y-%m-%d %H:%M:%S")
            if not (start_date <= ts <= end_date):
                continue

            model_name = model_part.split("Model: ")[1].split(" | ")[0].strip()
            tokens_used = int(model_part.split("Tokens used: ")[-1])

            total_tokens[model_name] = total_tokens.get(model_name, 0) + tokens_used

    total_cost = 0
    for model, tokens in total_tokens.items():
        cost_per_token = prices.get(model, 0) / 1000
        model_cost = cost_per_token * tokens
        total_cost += model_cost
        print(f"{model}: {tokens} tokens -> ${model_cost:.4f}")

    print(f"\nTotal cost from {start_date.date()} to {end_date.date()}: ${total_cost:.4f}")

if __name__ == "__main__":
    calculate_spent()
