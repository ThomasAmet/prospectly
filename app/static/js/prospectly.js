// Script that works with register.html to handle stripe (v2)
$(document).ready(function(){
    .then(function(result) {
      return result.json();
    })
    .then(function(data) {
      checkoutSessionId = data.checkoutSessionId;
    });
    $("#register-submit").click(function(){        
        $("#register-form").submit(); // Submit the form
    });

    $(document).on('submit', '#register-form', function(e){
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            type:'POST',
            url: '/auth/inscription',
            data: formData,
            success: function(response) {
              var stripe_session_id = result.json();
              stripe.redirectToCheckout({
                  sessionId: stripe_session_id
                }).then(function (result) {
                }); 
            },
            processData: false,
            contentType: false,
        });
    });
});



// Script that works with register.html to handle stripe (v1)
// $(document).ready(function(){
  
//     $("#register-submit").click(function(){        
//         $("#register-form").submit(); // Submit the form
//     });

//     $(document).on('submit', '#register-form', function(e){
//         e.preventDefault();
//         var formData = new FormData(this);
//         $.ajax({
//             type:'POST',
//             url: '/auth/inscription',
//             data: formData,
//             success: function(response) {
//                 // Create a Stripe client
//                 var stripe = Stripe('pk_test_jFlcRaZnz7655oSCFSvTSEMV00cvQbSli5');
//                 stripe.redirectToCheckout({
//                     sessionId: $('#stripe-session-id').val()
//                 }).then(function (result) {
//                 }); 
//             },
//             processData: false,
//             contentType: false,
//         });

        
//     });
// });``


$(document).ready(function(){
// // JQuery to change the format of element from the datepicker class
  let datepicker = $('#due-date-datepicker');
  if(datepicker.length > 0){
    datepicker.datepicker({
      format: "mm/dd/yyyy",
      startDate: new Date()
    });
  }

  // JQuery for Displaying part of the Edition form
  if ($("#status-value").val()=='A faire'){
      $("[class*='note-form-group']").hide();
      $("[class*='task-form-group']").show();
    }
    else{
      $("[class*='note-form-group']").show();
      $("[class*='task-form-group']").hide();      
    }
  $("#status-value").change(function(){
    if ($("#status-value").val()=='A faire'){
      $("[class*='note-form-group']").hide();
      $("[class*='task-form-group']").show();
    }
    else{
      $("[class*='note-form-group']").show();
      $("[class*='task-form-group']").hide();      
    }
  });
});


$(document).ready(function(){
    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
});


// JS for Toggle Pricing
let monthlyChoice = document.getElementById("monthly-choice");
let yearlyChoice = document.getElementById("yearly-choice");
let switcher = document.getElementById("switcher");
// div monthly
let monthlySubs = document.getElementById("monthly-subscriptions");
// div hourly
let yearlySubs = document.getElementById("yearly-subscriptions");

monthlyChoice.addEventListener("click", function(){
  switcher.checked = false;
  monthlyChoice.classList.add("toggler--is-active");
  yearlyChoice.classList.remove("toggler--is-active");
  monthlySubs.classList.remove("hide");
  yearlySubs.classList.add("hide");
});

yearlyChoice.addEventListener("click", function(){
  switcher.checked = true;
  yearlyChoice.classList.add("toggler--is-active");
  monthlyChoice.classList.remove("toggler--is-active");
  monthlySubs.classList.add("hide");
  yearlySubs.classList.remove("hide");
});

switcher.addEventListener("click", function(){
  yearlyChoice.classList.toggle("toggler--is-active");
  monthlyChoice.classList.toggle("toggler--is-active");
  monthlySubs.classList.toggle("hide");
  yearlySubs.classList.toggle("hide");
})



//  Monthly Live
$(document).ready(function(){
  var stripe = Stripe('pk_live_9Pr3WyeRB8zqyhkbR8cUdCYB00IPEwGuN5');
  var checkoutButton = document.getElementById('checkout-button-plan_GgreHAs62bMtM8');

  checkoutButton.addEventListener('click', function () {
    // When the customer clicks on the button, redirect
    // them to Checkout.
    stripe.redirectToCheckout({
      items: [{plan: 'plan_GgreHAs62bMtM8', quantity: 1}],

      // Do not rely on the redirect to the successUrl for fulfilling
      // purchases, customers may not always reach the success_url after
      // a successful payment.
      // Instead use one of the strategies described in
      // https://stripe.com/docs/payments/checkout/fulfillment
      successUrl: window.location.protocol + '//app.prospectly.fr/success',
      cancelUrl: window.location.protocol + '//app.prospectly.fr/canceled',
    })
    .then(function (result) {
      if (result.error) {
        // If `redirectToCheckout` fails due to a browser or network
        // error, display the localized error message to your customer.
        var displayError = document.getElementById('error-message');
        displayError.textContent = result.error.message;
      }
    });
  });
});

// Yearly Live
$(document).ready(function(){
  var stripe = Stripe('pk_live_9Pr3WyeRB8zqyhkbR8cUdCYB00IPEwGuN5');

  var checkoutButton = document.getElementById('checkout-button-plan_GgrfmtKZAV6j1l');
  checkoutButton.addEventListener('click', function () {
    // When the customer clicks on the button, redirect
    // them to Checkout.
    stripe.redirectToCheckout({
      items: [{plan: 'plan_GgrfmtKZAV6j1l', quantity: 1}],

      // Do not rely on the redirect to the successUrl for fulfilling
      // purchases, customers may not always reach the success_url after
      // a successful payment.
      // Instead use one of the strategies described in
      // https://stripe.com/docs/payments/checkout/fulfillment
      successUrl: window.location.protocol + '//app.prospectly.fr/success',
      cancelUrl: window.location.protocol + '//app.prospectly.fr/canceled',
    })
    .then(function (result) {
      if (result.error) {
        // If `redirectToCheckout` fails due to a browser or network
        // error, display the localized error message to your customer.
        var displayError = document.getElementById('error-message');
        displayError.textContent = result.error.message;
      }
    });
  });
});


// //  Monthly Test
// $(document).ready(function(){
//   var stripe = Stripe('pk_test_jFlcRaZnz7655oSCFSvTSEMV00cvQbSli5');
//   var checkoutButton = document.getElementById('checkout-button-plan_GggQmCKZATWq0c');

//   checkoutButton.addEventListener('click', function () {
//     // When the customer clicks on the button, redirect
//     // them to Checkout.
//     stripe.redirectToCheckout({
//       items: [{plan: 'plan_GggQmCKZATWq0c', quantity: 1}],

//       // Do not rely on the redirect to the successUrl for fulfilling
//       // purchases, customers may not always reach the success_url after
//       // a successful payment.
//       // Instead use one of the strategies described in
//       // https://stripe.com/docs/payments/checkout/fulfillment
//       successUrl: window.location.protocol + '//app.prospectly.fr/success',
//       cancelUrl: window.location.protocol + '//app.prospectly.fr/canceled',
//     })
//     .then(function (result) {
//       if (result.error) {
//         // If `redirectToCheckout` fails due to a browser or network
//         // error, display the localized error message to your customer.
//         var displayError = document.getElementById('error-message');
//         displayError.textContent = result.error.message;
//       }
//     });
//   });
// });

// // Yearly test
// $(document).ready(function(){
//   var stripe = Stripe('pk_test_jFlcRaZnz7655oSCFSvTSEMV00cvQbSli5');

//   var checkoutButton = document.getElementById('checkout-button-plan_GggP03CwhdtuYk');
//   checkoutButton.addEventListener('click', function () {
//     // When the customer clicks on the button, redirect
//     // them to Checkout.
//     stripe.redirectToCheckout({
//       items: [{plan: 'plan_GggP03CwhdtuYk', quantity: 1}],

//       // Do not rely on the redirect to the successUrl for fulfilling
//       // purchases, customers may not always reach the success_url after
//       // a successful payment.
//       // Instead use one of the strategies described in
//       // https://stripe.com/docs/payments/checkout/fulfillment
//       successUrl: window.location.protocol + '//app.prospectly.fr/success',
//       cancelUrl: window.location.protocol + '//app.prospectly.fr/canceled',
//     })
//     .then(function (result) {
//       if (result.error) {
//         // If `redirectToCheckout` fails due to a browser or network
//         // error, display the localized error message to your customer.
//         var displayError = document.getElementById('error-message');
//         displayError.textContent = result.error.message;
//       }
//     });
//   });
// });

// DO NOT DELETE
//   $(document).ready(function(){
//     if ($("#status-value").val()=='a_faire'){
//         $("[class*='note-form-group']").hide();
//         $("[class*='task-form-group']").show();
//       }
//       else{
//         $("[class*='note-form-group']").show();
//         $("[class*='task-form-group']").hide();      
//       }
//     $("#status-value").change(function(){
//       if ($("#status-value").val()=='a_faire'){
//         $("[class*='note-form-group']").hide();
//         $("[class*='task-form-group']").show();
//       }
//       else{
//         $("[class*='note-form-group']").show();
//         $("[class*='task-form-group']").hide();      
//       }
//   });
// });
