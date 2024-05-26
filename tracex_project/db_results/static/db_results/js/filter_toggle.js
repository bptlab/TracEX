$(document).ready(function () {
    // Toggle visibility for multiple elements
    setupToggleButton('#toggleButton1', '#contentWrapper1');
    setupToggleButton('#toggleButton2', '#contentWrapper2');

    // Setup age range slider
    setupAgeSlider();

    // Setup checkbox toggles for multiple groups
    setupCheckboxToggle('#toggleAll', '.origin-checkbox input[type="checkbox"]');
    setupCheckboxToggle('#togglesex', 'input[name="sex"]');
    setupCheckboxToggle('#toggleCondition', 'input[name="condition"]');
    setupCheckboxToggle('#togglePreexistingCondition', 'input[name="preexisting_condition"]');
});

function setupToggleButton(buttonSelector, contentSelector) {
    $(buttonSelector).click(function () {
        $(contentSelector).toggle();
    });
}

function setupAgeSlider() {
    const ageSlider = document.getElementById('age-slider');
    const minAgeField = document.getElementById('min-age');
    const maxAgeField = document.getElementById('max-age');

    noUiSlider.create(ageSlider, {
        start: [minAgeField.value || 0, maxAgeField.value || 100],
        connect: true,
        range: {
            'min': 0,
            'max': 100
        }
    });

    ageSlider.noUiSlider.on('update', function (values) {
        minAgeField.value = Math.round(values[0]);
        maxAgeField.value = Math.round(values[1]);
    });

    minAgeField.addEventListener('change', () => ageSlider.noUiSlider.set([minAgeField.value, null]));
    maxAgeField.addEventListener('change', () => ageSlider.noUiSlider.set([null, maxAgeField.value]));
}

function setupCheckboxToggle(toggleSelector, checkboxSelector) {
    document.querySelector(toggleSelector).addEventListener('change', function() {
        document.querySelectorAll(checkboxSelector)
               .forEach(checkbox => checkbox.checked = this.checked);
    });
}
