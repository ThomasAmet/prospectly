// Get the modals
  var modalEditOpportunity = document.getElementById("editOpportunityModal");
  var modalAddOpportunity = document.getElementById("addOpportunityModal");

  // Get the button that opens the modal
  var btnAddOpportunity = document.getElementById("addOpportunityBtn");
  var btnEditOpportunity = document.getElementById("editOpportunityBtn");

  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName("close")[0];

  // When the user clicks the button, open the modal 
  btnAddOpportunity.onclick = function() {
    modalEditOpportunity.style.display = "block";
  }

  // When the user clicks on <span> (x), close the modal
  span.onclick = function() {
    modalEditOpportunity.style.display = "none";
  }

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function(event) {
    if (event.target == modalEditOpportunity) {
      modalEditOpportunity.style.display = "none";
    }
  }





