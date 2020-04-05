$(document).ready(function(){

  // #####################
  // Script to toogle state of input fields in both form when clicking on CompanySettings toggle button
  $('#checkboxCompanySettings').click(function(){
    if($(this).prop("checked")){
      // Enable all input + select field + button in the CompanyForm.
      $.each($('#companyLeadsForm').find("input"), function(){
        $(this).prop('disabled', false);
      });
      $("#companyLeadsForm").find('#company_activity_field').prop('disabled', false);
      $.each($('#companyLeadsForm').find("button"), function(){
        $(this).prop('disabled', false);
      });   
      // Disable all inputs, select field  and buttons in ContactFrom
      $.each($('#contactLeadsForm').find("input"), function(){
        $(this).prop('disabled', true);
      });
      $("#contactLeadsForm").find('#company_activity_field').prop('disabled', true);
      $.each($('#contactLeadsForm').find("button"), function(){
        $(this).prop('disabled', true);
      });   
      // Uncheck the toggle button in ContactForm but keep both Company and Contact switch btn enabled
      $('#checkboxContactSettings').prop('disabled', false);
      $('#checkboxCompanySettings').prop('disabled', false);
      $('#checkboxContactSettings').prop('checked', false);
    }
    else{
      // Disable all input + select field + button in the CompanyForm.
      $.each($('#companyLeadsForm').find("input"), function(){
        $(this).prop('disabled', true);
      });
      $("#companyLeadsForm").find('#company_activity_field').prop('disabled', true);
      $.each($('#companyLeadsForm').find("button"), function(){
        $(this).prop('disabled', true);
      });   
      // Enable all inputs, select field  and buttons in ContactFrom
      $.each($('#contactLeadsForm').find("input"), function(){
        $(this).prop('disabled', false);
      });
      $("#contactLeadsForm").find('#company_activity_field').prop('disabled', false);
      $.each($('#contactLeadsForm').find("button"), function(){
        $(this).prop('disabled', false);
      });   
      // Check the toggle button in ContactForm
      $('#checkboxContactSettings').prop('disabled', false);
      $('#checkboxCompanySettings').prop('disabled', false);
      $('#checkboxContactSettings').prop('checked', true);
    }
  })




  // #####################
  // Script to toogle state of input fields in both form when clicking on ContactSettings toggle button
  $('#checkboxContactSettings').click(function(){
    if($(this).prop("checked")){
      // Enable all input + select field + button in the CompanyForm.
      $.each($('#contactLeadsForm').find("input"), function(){
        $(this).prop('disabled', false);
      });
      $("#contactLeadsForm").find('#company_activity_field').prop('disabled', false);
      $.each($('#contactLeadsForm').find("button"), function(){
        $(this).prop('disabled', false);
      });   
      // Disable all inputs, select field  and buttons in ContactFrom
      $.each($('#companyLeadsForm').find("input"), function(){
        $(this).prop('disabled', true);
      });
      $("#companyLeadsForm").find('#company_activity_field').prop('disabled', true);
      $.each($('#companyLeadsForm').find("button"), function(){
        $(this).prop('disabled', true);
      });   
      // Uncheck the toggle button in ContactForm but keep both Company and Contact switch btn enabled
      $('#checkboxContactSettings').prop('disabled', false);
      $('#checkboxCompanySettings').prop('disabled', false);
      $('#checkboxCompanySettings').prop('checked', false);
    }
    else{
      // Disable all input + select field + button in the ContactSettings Form.
      $.each($('#contactLeadsForm').find("input"), function(){
        $(this).prop('disabled', true);
      });
      $("#contactLeadsForm").find('#company_activity_field').prop('disabled', true);
      $.each($('#contactLeadsForm').find("button"), function(){
        $(this).prop('disabled', true);
      });   
      // Enable all inputs, select field  and buttons in ContactFrom
      $.each($('#companyLeadsForm').find("input"), function(){
        $(this).prop('disabled', false);
      });
      $("#companyLeadsForm").find('#company_activity_field').prop('disabled', false);
      $.each($('#companyLeadsForm').find("button"), function(){
        $(this).prop('disabled', false);
      });   
      // Check the toggle button in CompanyForm
      $('#checkboxContactSettings').prop('disabled', false);
      $('#checkboxCompanySettings').prop('disabled', false);
      $('#checkboxCompanySettings').prop('checked', true);
    }
  })


  // #####################
  // Jquery to edit Company attributes directly from the OpportunityEditForm
  $('#toggle-company-fields').click(function(){
    $.each($("[class*='company-field']"), function(){
      $(this).prop('disabled', function (_, val) { return ! val; });
    });
  });


  // #####################
  // Jquery to activate sorting in tables
  $("#opportunitiesTable").tablesorter();
  $('#companiesTable').tablesorter();
  $('#contactsTable').tablesorter();
  $('#companyLeadsTable').tablesorter();
  $('#contactLeadsTable').tablesorter();
  $("div.tablesorter-header-inner").css('display','inline');

  
  // #####################
  // Select all the checkboxes when clicking on the checkbox in table head
  $("#selectAll").click(function(){
    $("input[name='checkbox[]']").prop('checked', $(this).prop('checked'));// $(this).prop('checked') equals True or False depending on state of master checkbox
  });


  // #####################
  // Script to load CompanyLeads when they are selected
  $("#uploadContactLeads").click(function(){
    var rowIds = [];
    let activity_field;
    $.each($('#contactLeadsTable').find("input[name='checkbox[]']:checked"), function(){
      rowIds.push($(this).val());
    });
    activity_field = $("#contactLeadsForm").find('#company_activity_field').val()
    data = JSON.stringify({'leads_ids':rowIds, 'activity_field':activity_field})
    // alert(data);
    $.ajax({
      type: 'POST',
      url: '/app/leads/import-contacts',
      data: data,
      dataType: 'json',
      contentType: 'application/json',
      async: false,
    })
    // The function always fails because "/app/oppportunites/suppression" never return success due to handling both individual and collective deletion
    .done(function(data){
      // location.href = '/app/opportunites/liste';
      location.href = '/app/leads/generator';
    })
    .fail(function(jqXHR, textStatus, errorThrown){
      location.href = '/leads/erreur/upload';
    });
  });


  // #####################
  // Script to load ContactLeads when they are selected
  $("#uploadCompanyLeads").click(function(){
    var rowIds = [];
    let activity_field;
    $.each($('#companyLeadsTable').find("input[name='checkbox[]']:checked"), function(){
      rowIds.push($(this).val());
    });
    activity_field = $("#companyLeadsForm").find('#company_activity_field').val()
    data = JSON.stringify({'leads_ids':rowIds, 'activity_field':activity_field})
    // alert(data);
    $.ajax({
      type: 'POST',
      url: '/app/leads/import-entreprises',
      data: data,
      dataType: 'json',
      contentType: 'application/json',
      async: false,
    })
    // The function always fails because "/app/oppportunites/suppression" never return success due to handling both individual and collective deletion
    .done(function(data){
      // location.href = '/app/opportunites/liste';
      location.href = '/app/leads/generator';
    })
    .fail(function(jqXHR, textStatus, errorThrown){
      location.href = '/leads/erreur/upload';
    });
  });



  // Script to delete multiple rows in opportunities view page  
  $('#deleteAllOpportunities').click(function(){
    var rowIds = [];
    $.each($('#opportunitiesTable').find("input[name='checkbox[]']:checked"), function(){
      rowIds.push($(this).val());
    });
    data = JSON.stringify({'opp_ids':rowIds})
    // alert(data)
    $.ajax({
      type: 'POST',
      // url: '/app/oppportunites/suppression-multiple',
      url: '/app/oppportunites/suppression',
      data: data,
      dataType: 'json',
      contentType: 'application/json',
      async: false,
    })
    // The function always fails because "/app/oppportunites/suppression" never return success due to handling both individual and collective deletion
    .done(function(data){
      // location.href = '/app/opportunites/liste';
      location.href = '/app/dashboard';
    })
    .fail(function(jqXHR, textStatus, errorThrown){
      location.href = '/app/opportunites/liste';
    });
  });
  
  // ###############
  // Script to delete all rows in the company view page
  $('#deleteAllCompanies').click(function(){
    var rowIds = [];
    $.each($('#companiesTable').find("input[name='checkbox[]']:checked"), function(){
              rowIds.push($(this).val());
            });
    data = JSON.stringify({'companies_ids':rowIds})
    $.ajax({
      type: 'POST',
      // url: '/app/oppportunites/suppression-multiple',
      url: '/app/entreprises/suppression',
      data: data,
      dataType: 'json',
      contentType: 'application/json',
      async: false,
    })
    .done(function(data){
      // location.href = '/app/opportunites/liste';
      location.href = '/app/dashboard';
    })
    .fail(function(jqXHR, textStatus, errorThrown){
      location.href = '/app/entreprises/liste';
    });
  });

  // ###########
  // Script to delete all rows in the contacts view page
  $('#deleteAllContacts').click(function(){
    var rowIds = [];
    $.each($('#contactsTable').find("input[name='checkbox[]']:checked"), function(){
                rowIds.push($(this).val());
            });
    data = JSON.stringify({'contacts_ids':rowIds})
    // alert(data);
    $.ajax({
      type: 'POST',
      // url: '/app/oppportunites/suppression-multiple',
      url: '/app/contacts/suppression',
      data: data,
      dataType: 'json',
      contentType: 'application/json',
      async: false,
    })
    .done(function(data){
      // location.href = '/app/opportunites/liste';
      location.href = '/app/dashboard';
    })
    .fail(function(jqXHR, textStatus, errorThrown){
      location.href = '/app/contacts/liste';
    });
  });

});





// Script that works with register.html to handle stripe (v2)
$(document).ready(function(){
    var stripe = null;

    // $.ajax({
    //     type:'GET',
    //     url: '/auth/stripe-public-key',
    //     success: function(response) {
    //       // alert(response['publicKey']);
    //       stripe = Stripe(response['publicKey']); //pk_test_jFlcRaZnz7655oSCFSvTSEMV00cvQbSli5');
    //     },
    //     processData: false,
    //     contentType: false,
    // });

    // $("#register-submit").click(function(){        
    //     $("#register-form").submit(); // Submit the form
    // });

    $(document).on('submit', '#register-form', function(e){
        e.preventDefault();
        $.ajax({
          type:'GET',
          url: '/auth/stripe-public-key',
          success: function(response) {
            // alert(response['publicKey']);
            stripe = Stripe(response['publicKey']); //pk_test_jFlcRaZnz7655oSCFSvTSEMV00cvQbSli5');
          },
          processData: false,
          contentType: false,
        });
        var formData = new FormData(this);
        $.ajax({
            type:'POST',
            url: '/auth/inscription',
            data: formData,
            dataType: 'text',
            // contentType: "form-data",
            // success: function(response) {
            //   alert(response);
            //   var stripe_session_id = response;
            //   // Public Key for test
            //   // var stripe = Stripe('pk_test_jFlcRaZnz7655oSCFSvTSEMV00cvQbSli5');
            //   // Public Key for production
            //   // var stripe = Stripe('pk_live_9Pr3WyeRB8zqyhkbR8cUdCYB00IPEwGuN5');
            //   stripe.redirectToCheckout({
            //       sessionId: stripe_session_id
            //     }).then(function (result) {
            //     }); 
            // },
            processData: false,
            contentType: false,
        })
        .done(function(data) { 
          // alert('Success')
          // alert(data);
          var stripe_session_id = data;
            // Public Key for test
            // var stripe = Stripe('pk_test_jFlcRaZnz7655oSCFSvTSEMV00cvQbSli5');
            // Public Key for production
            // var stripe = Stripe('pk_live_9Pr3WyeRB8zqyhkbR8cUdCYB00IPEwGuN5');
            stripe.redirectToCheckout({
              sessionId: stripe_session_id
            })
            .then(function (result) {
            });
        })
        .fail(function(jqXHR, textStatus, errorThrown){
          // alert('Fail')
          // alert(jqXHR.responseText);
          // window.location.replace("http://stackoverflow.com");
          // window.location.assign(jqXHR.responseText);
          location.href=jqXHR.responseText;
        });

    });
});



$(document).ready(function(){
  // 
  // Script to change appearance of flash message
  $('#offerBar').css("display","block");
  $('#closeBar').click(function(){
    // $('#offerBar').css("visibility","hidden");
    $('#offerBar').css("display","none");
    // $('#offerBar').hide();
  });
  $('#banner-wrap').addClass("fadeInDown wow");
 
  // 
  // JQuery to change the format of element from the datepicker class
  let datepicker = $('#due-date-datepicker');
  if(datepicker.length > 0){
    datepicker.datepicker({
      format: "mm/dd/yyyy",
      startDate: new Date()
    });
  }


  // Jquery to send True/False when the checkbox from task and note form is clicked/uncliked
  // var task_done = $('input.checkbox-task-done:checkbox');
  // var task_done_field = $('input.checkbox-task-done-hidden:checkbox');
  // task_done_field.val(task_done.is(':checked'));
  // task_done.change(function(){
  //   // alert(task_done.is(':checked'));  
  //   task_done_field.val(task_done.is(':checked'));
  // });

  
  // JQuery for displaying task module or note moduel within EditOpportunityForm
  var loadEditTaskAndNote = function(){
    if ($("#status-field-edit-form").val()=='A faire'){
      $("[class*='note-form-group']").hide();
      $("[class*='task-form-group']").show();
      $.each($("input.task-form-group"), function(){
        $(this).prop('required',true);
      });
    }
    else{
      $("[class*='note-form-group']").show();
      $("[class*='task-form-group']").hide();   
      $.each($("input.task-form-group"), function(){
        $(this).removeAttr('required');
      });
    }
  }
  $(".clickable-cell").click(function() {
    loadEditTaskAndNote();  
  });
  $('#status-field-edit-form').change(function(){
      // alert($(this).val());
      if ($("#status-field-edit-form").val()=='A faire'){
        $("[class*='note-form-group']").hide();
        $("[class*='task-form-group']").show();
        $.each($("input.task-form-group"), function(){
          $(this).prop('required',true);
        });
      }
      else{
        $("[class*='note-form-group']").show();
        $("[class*='task-form-group']").hide();
        $.each($("input.task-form-group"), function(){
          $(this).removeAttr('required');
      });      
      }
    });



  // JQuery for displaying task module or note moduel within AddOppportunityForm 
  var loadAddTaskAndNote = function(){
    if ($("#status-field-add-form").val()=='A faire'){
        $("[class*='note-form-group']").hide();
        $("[class*='task-form-group']").show();
        $.each($("input.task-form-group"), function(){
        $(this).prop('required',true);
      });
    }
    else{
        $("[class*='note-form-group']").show();
        $("[class*='task-form-group']").hide();
        $.each($("input.task-form-group"), function(){
        $(this).prop('required',false);
      });       
    }
  }
  $("#addOpportunityBtn").click(function(){
    loadAddTaskAndNote();
  });
  $('#status-field-add-form').change(function(){
      // alert($(this).val());
      if ($("#status-field-add-form").val()=='A faire'){
        $("[class*='note-form-group']").hide();
        $("[class*='task-form-group']").show();
        $.each($("input.task-form-group"), function(){
        $(this).prop('required',true);
      });
      }
      else{
        $("[class*='note-form-group']").show();
        $("[class*='task-form-group']").hide();
        $.each($("input.task-form-group"), function(){
        $(this).prop('required',false);
      });      
      }
    });

 

  // Jquery to make the entire row of a table clickable
  $(".clickable-row").click(function() {
    window.location = $(this).data("href");
  });

  // 
  // Jquery for Toggle Pricing
  let monthlyChoice = $('#monthly-choice');
  let yearlyChoice = $('#yearly-choice');
  let switcher = $('#switcher');
  // div monthly
  let monthlySubs = $("#monthly-subscriptions");
  // div hourly
  let yearlySubs = $("#yearly-subscriptions");

  monthlyChoice.click(function(){
    switcher.prop("checked", false);
    monthlyChoice.addClass("toggler--is-active");
    yearlyChoice.removeClass("toggler--is-active");
    monthlySubs.addClass("hide");
    yearlySubs.removeClass("hide");
  });

  yearlyChoice.click(function(){
    switcher.prop("checked", true);
    yearlyChoice.addClass("toggler--is-active");
    monthlyChoice.removeClass("toggler--is-active");
    yearlySubs.addClass("hide");
    monthlySubs.removeClass("hide");
  });

  switcher.click(function(){
    yearlyChoice.toggleClass("toggler--is-active");
    monthlyChoice.toggleClass("toggler--is-active");
    yearlySubs.toggleClass("hide");
    monthlySubs.toggleClass("hide");
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
// });


// // // JS for Toggle Pricing (in Javascript native)
// let monthlyChoice = document.getElementById("monthly-choice");
// let yearlyChoice = document.getElementById("yearly-choice");
// let switcher = document.getElementById("switcher");
// // div monthly
// let monthlySubs = document.getElementById("monthly-subscriptions");
// // div hourly
// let yearlySubs = document.getElementById("yearly-subscriptions");

// monthlyChoice.addEventListener("click", function(){
//   switcher.checked = false;
//   monthlyChoice.classList.add("toggler--is-active");
//   yearlyChoice.classList.remove("toggler--is-active");
//   monthlySubs.classList.remove("hide");
//   yearlySubs.classList.add("hide");
// });

// yearlyChoice.addEventListener("click", function(){
//   switcher.checked = true;
//   yearlyChoice.classList.add("toggler--is-active");
//   monthlyChoice.classList.remove("toggler--is-active");
//   monthlySubs.classList.add("hide");
//   yearlySubs.classList.remove("hide");
// });

// switcher.addEventListener("click", function(){
//   yearlyChoice.classList.toggle("toggler--is-active");
//   monthlyChoice.classList.toggle("toggler--is-active");
//   monthlySubs.classList.toggle("hide");
//   yearlySubs.classList.toggle("hide");
// })



// //  Monthly Live
// $(document).ready(function(){
//   var stripe = Stripe('pk_live_9Pr3WyeRB8zqyhkbR8cUdCYB00IPEwGuN5');
//   var checkoutButton = document.getElementById('checkout-button-plan_GgreHAs62bMtM8');

//   checkoutButton.addEventListener('click', function () {
//     // When the customer clicks on the button, redirect
//     // them to Checkout.
//     stripe.redirectToCheckout({
//       items: [{plan: 'plan_GgreHAs62bMtM8', quantity: 1}],

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

// // Yearly Live
// $(document).ready(function(){
//   var stripe = Stripe('pk_live_9Pr3WyeRB8zqyhkbR8cUdCYB00IPEwGuN5');

//   var checkoutButton = document.getElementById('checkout-button-plan_GgrfmtKZAV6j1l');
//   checkoutButton.addEventListener('click', function () {
//     // When the customer clicks on the button, redirect
//     // them to Checkout.
//     stripe.redirectToCheckout({
//       items: [{plan: 'plan_GgrfmtKZAV6j1l', quantity: 1}],

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
