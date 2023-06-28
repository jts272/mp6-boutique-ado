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

  // For save info checkbox
  const saveInfo = Boolean($("#id-save-info").attr("checked"));

  // Get csrf token that Django creates
  const csrfToken = $("input[name='csrfmiddlewaretoken").val();
  // Obj to pass to the cache view
  const postData = {
    csrfmiddlewaretoken: csrfToken,
    // Pass client secret for payment intent
    client_secret: clientSecret,
    save_info: saveInfo,
  };
  const url = "/checkout/cache_checkout_data/";

  // Post with jQuery
  // callbackfn `.done()` to wait for payment intent updated before calling
  // confirm card payment function. done = 'do on status 200'
  // https://youtu.be/dewcliXUY8Y?t=123
  $.post(url, postData)
    .done(function () {
      // Call confirm card payment method
      stripe
        .confirmCardPayment(clientSecret, {
          payment_method: {
            // Give Stripe the card
            card: card,
            // Form data to go into payment intent obj
            // See Stripe docs for structure of payment intent object
            billing_details: {
              name: $.trim(form.full_name.value),
              phone: $.trim(form.phone_number.value),
              email: $.trim(form.email.value),
              address: {
                line1: $.trim(form.street_address1.value),
                line2: $.trim(form.street_address2.value),
                city: $.trim(form.town_or_city.value),
                country: $.trim(form.country.value),
                state: $.trim(form.county.value),
              },
            },
          },
          // For instances of different billing and shipping addresses
          shipping: {
            name: $.trim(form.full_name.value),
            phone: $.trim(form.phone_number.value),
            address: {
              line1: $.trim(form.street_address1.value),
              line2: $.trim(form.street_address2.value),
              city: $.trim(form.town_or_city.value),
              country: $.trim(form.country.value),
              postal_code: $.trim(form.postcode.value),
              state: $.trim(form.county.value),
            },
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
      // Failure function if view triggers 400 response
    })
    .fail(function () {
      // Reload the page; errors will be in Django messages
      location.reload();
    });
});
