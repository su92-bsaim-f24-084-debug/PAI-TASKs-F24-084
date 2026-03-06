from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Get your free API key at https://www.exchangerate-api.com/
API_KEY = "efa4ad4ccdab990366348b66"
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}"

CURRENCIES = [
    ("USD", "US Dollar"),
    ("EUR", "Euro"),
    ("GBP", "British Pound"),
    ("JPY", "Japanese Yen"),
    ("CAD", "Canadian Dollar"),
    ("AUD", "Australian Dollar"),
    ("CHF", "Swiss Franc"),
    ("CNY", "Chinese Yuan"),
    ("INR", "Indian Rupee"),
    ("MXN", "Mexican Peso"),
    ("BRL", "Brazilian Real"),
    ("KRW", "South Korean Won"),
    ("SGD", "Singapore Dollar"),
    ("HKD", "Hong Kong Dollar"),
    ("NOK", "Norwegian Krone"),
    ("SEK", "Swedish Krona"),
    ("DKK", "Danish Krone"),
    ("NZD", "New Zealand Dollar"),
    ("ZAR", "South African Rand"),
    ("PKR", "Pakistani Rupee"),
]

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    amount = ""
    from_currency = "USD"
    to_currency = "EUR"

    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        from_currency = request.form.get("from_currency", "USD")
        to_currency = request.form.get("to_currency", "EUR")

        try:
            amount_float = float(amount)
            response = requests.get(
                f"{BASE_URL}/pair/{from_currency}/{to_currency}/{amount_float}",
                timeout=5
            )
            data = response.json()

            if data.get("result") == "success":
                result = {
                    "converted": round(data["conversion_result"], 2),
                    "rate": data["conversion_rate"],
                    "from": from_currency,
                    "to": to_currency,
                    "amount": amount_float,
                }
            else:
                error = data.get("error-type", "Conversion failed. Check your API key.")
        except ValueError:
            error = "Please enter a valid number."
        except requests.exceptions.ConnectionError:
            error = "Could not reach the exchange rate service. Check your connection."
        except Exception as e:
            error = f"An unexpected error occurred: {str(e)}"

    return render_template(
        "index.html",
        currencies=CURRENCIES,
        result=result,
        error=error,
        amount=amount,
        from_currency=from_currency,
        to_currency=to_currency,
    )


if __name__ == "__main__":
    app.run(debug=True)