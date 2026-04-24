from flask import Flask, request, jsonify, send_file
import stripe
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Ihre echten Stripe Keys
stripe.api_key = "sk_test_51TIXOFRHyQYoj5HmDhFSkaMshuA5ByNONbqyuXdpoRcilQEBkSym42f0cCHabnoduKXgEIvM9B9IhTsxLaRbZPJg00v2GJpUJ0"

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.json
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': data['product'],
                    },
                    'unit_amount': data['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://lana-ki.de/success',
            cancel_url='https://lana-ki.de/cancel',
        )
        
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download')
def download_product():
    # Hier würden Sie das gekaufte Produkt ausliefern
    return '''
    <h1>✅ Zahlung erfolgreich!</h1>
    <p>Ihr Produkt wird per E-Mail gesendet.</p>
    <p>Bei Fragen: contact@lana-ki.de</p>
    '''

if __name__ == '__main__':
    print("💰 Payment Server gestartet auf http://localhost:5000")
    app.run(debug=True, port=5000)
