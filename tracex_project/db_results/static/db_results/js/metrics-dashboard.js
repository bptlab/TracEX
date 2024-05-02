function updateAvgTimeCorrTileColor(ratio, tile) {
    if (ratio >= 0.7) {
      tile.style.backgroundColor = 'green';
    } else if (ratio >= 0.5) {
      tile.style.backgroundColor = 'orange';
    } else {
      tile.style.backgroundColor = 'red';
    }
  }

function updateFrequentMetricTileColor(content, tile) {
  if (content === 'High Relevance' || content === 'True') {
    tile.style.backgroundColor = 'green';
  } else if  (content === 'Low Relevance' || content === 'False') {
    tile.style.backgroundColor = 'red';
  } else {
    tile.style.backgroundColor = 'orange';
  }
}


const avgTimeStampCorr = document.getElementById('avgTimeStampCorr');
const avgTimeStampCorrTile = avgTimeStampCorr.closest('.metric-tile');
const avgTimeStampCorrContent = parseFloat(avgTimeStampCorr.textContent);
updateAvgTimeCorrTileColor(avgTimeStampCorrContent, avgTimeStampCorrTile);

const most_frequent_timestamp_correctness = document.getElementById('most_frequent_timestamp_correctness');
const most_frequent_timestamp_correctness_tile = most_frequent_timestamp_correctness.closest('.metric-tile');
const most_frequent_timestamp_correctness_content = most_frequent_timestamp_correctness.textContent.trim();
updateFrequentMetricTileColor(most_frequent_timestamp_correctness_content, most_frequent_timestamp_correctness_tile);

const most_frequent_category = document.getElementById('most_frequent_category');
const most_frequent_category_tile = most_frequent_category.closest('.metric-tile');
const most_frequent_category_content = most_frequent_category.textContent.trim();
updateFrequentMetricTileColor(most_frequent_category_content, most_frequent_category_tile);

// Trigger a resize event for the plots to adapt to the new size
setTimeout(function() {
  window.dispatchEvent(new Event('resize'));
}, 0);
