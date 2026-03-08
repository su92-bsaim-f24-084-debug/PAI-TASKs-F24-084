from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Get your free API key at https://www.exchangerate-api.com/
API_KEY = "efa4ad4ccdab990366348b66"
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}"

SUPPORTED_CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY",
    "INR", "MXN", "BRL", "KRW", "SGD", "HKD", "NOK", "SEK",
    "DKK", "NZD", "ZAR", "PKR"
]


# ── Route 0: Home ─────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Currency Converter API",
        "endpoints": {
            "GET  /currencies": "List all supported currencies",
            "GET  /rate?from=USD&to=EUR": "Get live exchange rate",
            "POST /convert": "Convert an amount (body: from, to, amount)"
        }
    })


# ── Route 1: List all supported currencies ────────────────────────────────────
@app.route("/currencies", methods=["GET"])
def get_currencies():
    return jsonify({
        "supported_currencies": SUPPORTED_CURRENCIES
    })


# ── Route 2: Get live exchange rate between two currencies ────────────────────
@app.route("/rate", methods=["GET"])
def get_rate():
    from_currency = request.args.get("from", "").upper()
    to_currency   = request.args.get("to", "").upper()

    if not from_currency or not to_currency:
        return jsonify({"error": "Please provide both 'from' and 'to' query params."}), 400

    try:
        response = requests.get(f"{BASE_URL}/pair/{from_currency}/{to_currency}", timeout=5)
        data = response.json()

        if data.get("result") == "success":
            return jsonify({
                "from": from_currency,
                "to": to_currency,
                "rate": data["conversion_rate"]
            })
        else:
            return jsonify({"error": data.get("error-type", "Failed to fetch rate.")}), 400

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not reach exchange rate service."}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Route 3: Convert an amount from one currency to another ───────────────────
@app.route("/convert", methods=["POST"])
def convert():
    body = request.get_json()

    if not body:
        return jsonify({"error": "Request body must be JSON."}), 400

    from_currency = str(body.get("from", "")).upper()
    to_currency   = str(body.get("to", "")).upper()
    amount        = body.get("amount")

    # Validate fields
    if not from_currency or not to_currency or amount is None:
        return jsonify({"error": "Required fields: 'from', 'to', 'amount'."}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "'amount' must be greater than 0."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "'amount' must be a valid number."}), 400

    try:
        response = requests.get(
            f"{BASE_URL}/pair/{from_currency}/{to_currency}/{amount}",
            timeout=5
        )
        data = response.json()

        if data.get("result") == "success":
            return jsonify({
                "from": from_currency,
                "to": to_currency,
                "amount": amount,
                "converted": round(data["conversion_result"], 2),
                "rate": data["conversion_rate"]
            })
        else:
            return jsonify({"error": data.get("error-type", "Conversion failed.")}), 400

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not reach exchange rate service."}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)