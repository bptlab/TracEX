/* JS File to display a spinning wheel when the "Generate a Patient Journey" button is pressed. */
const generate_button = document.getElementById('generate_button');
const loader = document.getElementById('loading-spinner');

generate_button.addEventListener('click', () => {
    loader.classList.remove('not_visible');
})