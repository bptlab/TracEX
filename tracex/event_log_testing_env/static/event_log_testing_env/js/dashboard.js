const numberMetrics = document.querySelectorAll('.number-metric');
console.log("TEST");
numberMetrics.forEach(metric => {
  const content = parseInt(metric.textContent);
  const metricTile = metric.closest('.metric-tile');

  console.log(typeof content);
  console.log(content);

  if (content >= 0 && content <= 3) {
    metricTile.style.backgroundColor = 'green';
  } else if (content >= 4 && content <= 6) {
    metricTile.style.backgroundColor = 'orange';
  } else {
    metricTile.style.backgroundColor = 'red';
  }
});
