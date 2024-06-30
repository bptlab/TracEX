const numberMetrics = document.querySelectorAll('.number-metric');
var togglePipelineButton = document.getElementById('togglePipelineTable');
var contentPipeline = document.getElementById('contentPipeline');



numberMetrics.forEach(metric => {
  const content = parseInt(metric.textContent);
  const metricTile = metric.closest('.metric-tile');
  if (content >= 0 && content <= 3) {
    metricTile.style.backgroundColor = 'green';
  } else if (content >= 4 && content <= 6) {
    metricTile.style.backgroundColor = 'orange';
  } else {
    metricTile.style.backgroundColor = 'red';
  }
});


document.getElementById("togglePipelineTable").addEventListener("click", function() {
  var content = document.getElementById("contentPipeline");
  if (content.style.display === "none") {
    content.style.display = "block";
  } else {
    content.style.display = "none";
  }
});

document.getElementById("toggleGroundTruthTable").addEventListener("click", function() {
  var content = document.getElementById("contentGroundTruth");
  if (content.style.display === "none") {
    content.style.display = "block";
  } else {
    content.style.display = "none";
  }
});
