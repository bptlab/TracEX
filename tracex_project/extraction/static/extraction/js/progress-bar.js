const execute_button = document.getElementById('execute_button');
const progress_box = document.getElementById('progress_box');
const loader = document.getElementById('loading-spinner');

function updateProgressBar() {
    $.ajax({
        url: '/extraction/filter/',
        method: "GET",
        success: function(data) {
            // Update the progress bar element with the received progress data
            const percentage = data.progress !== null ? data.progress + "%" : "0%";
            const current_module = data.status;
            progress_box.innerHTML = `
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-primary" role="progressbar" style="width: ${percentage};" aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100">${percentage}</div>
            </div>
            ${current_module ? `<div class="progress-container"><p>${current_module} is currently running</p></div>` : '<div class="progress-container"><p>Execute Extraction Pipeline</p></div>'}
        `;

            // If the task is not complete, continue checking for progress // hier muss data.progress rein
            if (data.progress === 100) {
                // Hide the progress bar and show the result button
                execute_button.classList.add('not_visible');

            } else {
                // If progress is not 100, continue fetching progress
                setTimeout(updateProgressBar, 1000); // Fetch progress again after 1 second
            }
        },
        error: function() {
            console.log("Error occurred while fetching progress. Alternatively, a spinning loading wheel will be displayed.");
            progress_box.classList.add('not_visible');
            loader.classList.remove('not_visible');
        }
    });
}

execute_button.addEventListener('click', () => {
    progress_box.classList.remove('not_visible');
    progress_box.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    updateProgressBar();
})