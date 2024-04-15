// Get the modal
var modal = document.getElementById("downloadModal");

// Get the button that opens the modal
var btn = document.getElementById("downloadBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// Get checkboxes
var checkboxes = document.querySelectorAll('.trace-checkbox');

// Get the download form
var downloadForm = document.getElementById("downloadForm");

// Create an error display element and configure it
var errorDisplay = document.createElement('p');
errorDisplay.style.color = 'red';
errorDisplay.style.fontWeight = 'bold';  // Make the text bold
errorDisplay.textContent = 'Please select at least one type of XES file to download.';
errorDisplay.style.display = 'none';

// Insert the error display at the top of the form
downloadForm.insertBefore(errorDisplay, downloadForm.firstChild);

// When the user clicks the button, open the modal and hide any error
btn.onclick = function() {
    modal.style.display = "block";
    errorDisplay.style.display = 'none';  // Hide error on button click
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Check if at least one checkbox is checked and handle the form submission
downloadForm.onsubmit = function(event) {
    var anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
    if (!anyChecked) {
        errorDisplay.style.display = 'block';  // Show error message
        event.preventDefault();  // Prevent form submission
    }
};
