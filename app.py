from flask import Flask, render_template, request, redirect, url_for
import paypalrestsdk
import os

app = Flask(__name__, static_folder='templates/media')

# Configuration PayPal
paypalrestsdk.configure({
    "mode": "sandbox",  # Passe à 'live' pour un environnement réel
    "client_id": "AUozu-hr6K7sOagqzaBjt3jnmMBXukDV3XCxylMMfdXD8Y-p6DatJWRU8P5-KjItkHByugQhTauWr7JD",  # Assure-toi que tes variables d'environnement sont définies
    "client_secret": "EKdMmrMFeCZThW2iP2kajfXL88RvTPjqeNrJBmZBtVSSjstUIPZ8iLfu6G8Rj2gys-Fqd2sVXXfztdqD"
})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checkout-go', methods=['GET'])
def checkout_go():
    service = request.args.get('service', 'VIP')  # Valeur par défaut VIP si rien n'est sélectionné
    prices = {'King': 10.00, 'Prince': 5.00, 'Knigth': 3.00}
    price = prices.get(service, 5.00)  # Récupérer le prix en fonction du service choisi

    return render_template('checkout.html', service=service, price=price)

# Route pour afficher la page de checkout avec le service sélectionné

@app.route('/checkout', methods=['POST'])
def checkout():
    # Vérifier et récupérer les valeurs du formulaire

    global username
    username= request.form.get('username')
    item_name = request.form.get("item_name")
    amount = request.form.get("amount")

    if not username or not item_name or not amount:
        return "Erreur : données manquantes"

    # Définir les URLs de retour
    return_url = url_for('payment_success', _external=True)
    cancel_url = url_for('payment_cancelled', _external=True)

    # Créer un paiement PayPal
    payment = paypalrestsdk.Payment({
        "intent": "sale",  # "sale" est correct
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": item_name,
                    "sku": "item_sku",
                    "price": str(amount),
                    "currency": "EUR",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(amount),
                "currency": "EUR"
            },
            "description": f"Payment for {item_name} by {username}"
        }]
    })

    # Vérifier si le paiement a été créé avec succès
    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
    else:
        print(payment.error)  # Debugging
        return "Erreur lors de la création du paiement, voir logs."

# Route de succès après paiement
@app.route('/payment_success')
def payment_success():
    payer_id = request.args.get('PayerID')
    payment_id = request.args.get('paymentId')
    if not payer_id or not payment_id:
        return "Error: missing payment details."

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return render_template('payment_success.html', message="Payment successful. Enjoy your service!")
    else:
        return "Error while executing payment"

# Route d'annulation de paiement
@app.route('/payment_cancelled')
def payment_cancelled():
    return render_template('payment_cancelled.html', message="Payment was cancelled.")

if __name__ == '__main__':
    app.run(debug=True)
