const generate_button = document.getElementById('generate_button');
const loader = document.getElementById('loading-spinner');

generate_button.addEventListener('click', () => {
    loader.classList.remove('not_visible');
})