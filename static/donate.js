// A reference to Stripe.js
var stripe;

function setupPayment(price) {
    tempData = {};
    Object.assign(tempData, orderData);
    tempData['price'] = price;

    fetch(url + "/api/create-payment-intent-for-donate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(tempData)
    })
        .then(function (result) {
            return result.json();
        })
        .then(function (data) {
            return setupElements(data);
        })
        .then(function ({stripe, card, clientSecret, intentId}) {
            document.querySelector("button").disabled = false;

            // Handle form submission.
            var form = document.getElementById("payment-form");
            form.addEventListener("submit", function (event) {
                event.preventDefault();
                // Initiate payment when the submit button is clicked
                var lambda = function(name) {pay(stripe, card, clientSecret, intentId, name);};

                window.handle_payment_request(lambda);
            });
        });
}

var orderData = {
    items: [{ id: "photo-subscription" }],
    currency: "usd"
};

let url = "{URL}";

// Disable the button until we have Stripe set up on the page
// document.querySelector("button").disabled = true;

// setupPayment();

// Set up Stripe.js and Elements to use in checkout form
var setupElements = function(data) {
    stripe = Stripe(data.publishableKey);
    var elements = stripe.elements();
    var style = {
        base: {
            color: "#32325d",
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: "antialiased",
            fontSize: "16px",
            "::placeholder": {
                color: "#aab7c4"
            }
        },
        invalid: {
            color: "#fa755a",
            iconColor: "#fa755a"
        }
    };

    var card = elements.create("card", { style: style });
    card.mount("#card-element");

    return {
        stripe: stripe,
        card: card,
        clientSecret: data.clientSecret,
        intentId: data.intentId
    };
};

/*
 * Calls stripe.confirmCardPayment which creates a pop-up modal to
 * prompt the user to enter extra authentication details without leaving your page
 */
var pay = function(stripe, card, clientSecret, intentId, name) {
    changeLoadingState(true);

    stripe
        .confirmCardPayment(clientSecret, {
            payment_method: {
                card: card
            }
        })
        .then(function(result) {
            if (result.error) {
                // Show error to your customer
                showError(result.error.message);
                handle_error()
            } else {
                // The payment has been processed!
                // orderComplete(clientSecret, intentId);
                handle_payment(intentId, name)
            }
        });
};

/* ------- Post-payment helpers ------- */

/* Shows a success / error message when the payment is complete */
var orderComplete = function(clientSecret, intentId) {
    $.post(url + '/api/handle-payment', {
        intentId: intentId
    });
};

var showError = function(errorMsgText) {
    var errorMsg = document.querySelector(".sr-field-error");
    errorMsg.textContent = errorMsgText;
    setTimeout(function() {
        errorMsg.textContent = "";
    }, 4000);
};

var changeLoadingState = function (state) {

};
