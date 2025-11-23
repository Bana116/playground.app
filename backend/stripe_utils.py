import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(user_type, user_id):
    """
    Creates a Stripe Checkout session.
    After payment, a webhook will add credits to the user.
    """
    YOUR_DOMAIN = os.getenv("DOMAIN", "http://localhost:5000")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price": os.getenv("STRIPE_PRICE_ID"),
                "quantity": 1
            }
        ],
        success_url=f"{YOUR_DOMAIN}/payment/success?user_type={user_type}&user_id={user_id}",
        cancel_url=f"{YOUR_DOMAIN}/payment/cancel",
    )

    return session.url
