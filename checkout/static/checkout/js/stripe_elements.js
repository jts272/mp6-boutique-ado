// https://youtu.be/eUcMh5s_27I?t=206

// Get vars from DOM with jQuery and strip quotation marks
const stripe_public_key = $("#id_stripe_public_key").text().slice(1, -1);
const client_secret = $("#id_client_secret").text().slice(1, -1);
// Setup Stripe (uses CDN link in base template)
const stripe = Stripe(stripe_public_key);
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

// Use that to create a card element
// Include style argument
const card = elements.create("card", { style: style });

// Mount the card element to the div on checkout page
card.mount("#card-element");
