var modal = document.getElementById("downloadModal");
var btn = document.getElementById("downloadBtn");
var span = document.getElementsByClassName("close")[0];

var checkboxes = document.querySelectorAll('.trace-checkbox');
var downloadForm = document.getElementById("downloadForm");

var errorDisplay = document.createElement('p');
errorDisplay.style.color = 'red';
errorDisplay.style.fontWeight = 'bold';  // Make the text bold
errorDisplay.textContent = 'Please select at least one type of XES file to download.';
errorDisplay.style.display = 'none';

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
        errorDisplay.style.display = 'block';
        event.preventDefault();
    }
};
