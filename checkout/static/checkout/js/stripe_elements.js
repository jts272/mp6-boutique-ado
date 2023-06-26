// https://youtu.be/eUcMh5s_27I?t=206

// Get vars from DOM with jQuery and strip quotation marks
const stripePublicKey = $("#id_stripe_public_key").text().slice(1, -1);
const clientSecret = $("#id_client_secret").text().slice(1, -1);
// Setup Stripe (uses CDN link in base template)
const stripe = Stripe(stripePublicKey);
// Use this to setup instance of Stripe elements
const elements = stripe.elements();

// https://github.com/Code-Institute-Solutions/boutique_ado_v1/blob/a75791ce63bfce9a05f614d7712199c893063ed9/checkout/static/checkout/js/stripe_elements.js
var style = {
  base: {
    color: "#000",
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: "antialiased",
    fontSize: "16px",
    "::placeholder": {
      color: "#aab7c4",
    },
  },
  invalid: {
    // Match bs-danger class
    color: "#dc3545",
    iconColor: "#dc3545",
  },
};

// Use elements to create a card element
// Include style argument
const card = elements.create("card", { style: style });

// Mount the card element to the div on checkout page
card.mount("#card-element");

// VALIDATION ERRORS
card.addEventListener("change", function (event) {
  const errorDiv = document.getElementById("card-errors");
  if (event.error) {
    const html = `   
    <span class="icon" role="alert">
      <i class="fas fa-times"></i>
    </span>
    <span>${event.error.message}</span>
    `;
    $(errorDiv).html(html);
  } else {
    errorDiv.textContent = "";
  }
});

// FORM SUBMISSION
// https://github.com/Code-Institute-Solutions/boutique_ado_v1/blob/6b3837fb56fdb60655292badbb2dcf649a074ec7/checkout/static/checkout/js/stripe_elements.js

var form = document.getElementById("payment-form");

form.addEventListener("submit", function (ev) {
  ev.preventDefault();
  // Prevent multiple card submissions
  card.update({ disabled: true });
  $("#submit-button").attr("disabled", true);
  // Engage loading spinner overlay
  $("#payment-form").fadeToggle(100);
  $("#loading-overlay").fadeToggle(100);
  // Call confirm card payment method
  stripe
    .confirmCardPayment(clientSecret, {
      payment_method: {
        // Give Stripe the card
        card: card,
      },
    })
    // Execute this function on the result
    .then(function (result) {
      // Handle errors first if applicable
      if (result.error) {
        var errorDiv = document.getElementById("card-errors");
        var html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
        $(errorDiv).html(html);
        // Revert overlay toggle
        $("#payment-form").fadeToggle(100);
        $("#loading-overlay").fadeToggle(100);
        // Re-enable card element to allow user to fix the issue
        card.update({ disabled: false });
        $("#submit-button").attr("disabled", false);
      } else {
        // Submit the form if payment succeed
        if (result.paymentIntent.status === "succeeded") {
          form.submit();
        }
      }
    });
});
