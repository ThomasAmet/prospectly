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

