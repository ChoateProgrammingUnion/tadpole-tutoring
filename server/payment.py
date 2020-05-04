import stripe
stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"

charge = stripe.Charge.create(
    amount=2000,
    currency="usd",
    description="My First Test Charge (created for API docs)",
    source="tok_mastercard", # obtained with Stripe.js
    idempotency_key='JrAvt3hEhIYW4LnT'
)

intent = stripe.PaymentIntent.create(
    amount=1099,
    currency='usd',
    payment_method_types=['card'],
)

pass