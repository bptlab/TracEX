function updateTileColor(elementId, ratio, tile) {
    if (ratio >= 0.7) {
      tile.style.backgroundColor = 'green';
    } else if (ratio >= 0.5) {
      tile.style.backgroundColor = 'orange';
    } else {
      tile.style.backgroundColor = 'red';
    }
  }

  function calculateRatio(elementId, totalElementId) {
    const element = document.getElementById(elementId);
    const elementContent = parseFloat(element.textContent);
    const totalElement = document.getElementById(totalElementId);
    const totalElementContent = parseFloat(totalElement.textContent);
    return elementContent / totalElementContent;
  }

  const avgTimeStampCorr = document.getElementById('avgTimeStampCorr');
  const avgTimeStampCorrTile = avgTimeStampCorr.closest('.metric-tile');
  const avgTimeStampCorrContent = parseFloat(avgTimeStampCorr.textContent);
  updateTileColor('avgTimeStampCorr', avgTimeStampCorrContent, avgTimeStampCorrTile);

  const categoryRatio = calculateRatio('most_frequent_category_count', 'total_category');
  const most_frequent_category_countTile = document.getElementById('most_frequent_category_count').closest('.metric-tile');
  updateTileColor('most_frequent_category_count', categoryRatio, most_frequent_category_countTile);

  const timestampCorrectnessRatio = calculateRatio('most_frequent_timestamp_correctness_count', 'total_timestamp_correctness');
  const most_frequent_timestamp_correctness_countTile = document.getElementById('most_frequent_timestamp_correctness_count').closest('.metric-tile');
  updateTileColor('most_frequent_timestamp_correctness_count', timestampCorrectnessRatio, most_frequent_timestamp_correctness_countTile);

  // Trigger a resize event for the plots to adapt to the new size
  setTimeout(function() {
    window.dispatchEvent(new Event('resize'));
  }, 100);
