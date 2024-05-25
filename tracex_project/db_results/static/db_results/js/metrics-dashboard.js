// Constants for color thresholds and descriptions
const GREEN_THRESHOLD = 0.7;
const ORANGE_THRESHOLD = 0.5;
const COLORS = {
  GREEN: 'green',
  ORANGE: 'orange',
  RED: 'red'
};

// Constants for content matching
const CONTENT_MATCH = {
  HIGH_RELEVANCE: 'High Relevance',
  TRUE: 'True',
  LOW_RELEVANCE: 'Low Relevance',
  FALSE: 'False'
};

// Helper function to set the tile color based on predefined color rules.
function setTileColor(tile, color) {
  tile.style.backgroundColor = color;
}

// Updates the tile color based on the average time correctness ratio.
function updateAvgTimeCorrTileColor(ratio, tile) {
  if (ratio >= GREEN_THRESHOLD) {
    setTileColor(tile, COLORS.GREEN);
  } else if (ratio >= ORANGE_THRESHOLD) {
    setTileColor(tile, COLORS.ORANGE);
  } else {
    setTileColor(tile, COLORS.RED);
  }
}

// Updates the tile color based on the frequency metric's content.
function updateFrequentMetricTileColor(content, tile) {
  switch (content) {
    case CONTENT_MATCH.HIGH_RELEVANCE:
    case CONTENT_MATCH.TRUE:
      setTileColor(tile, COLORS.GREEN);
      break;
    case CONTENT_MATCH.LOW_RELEVANCE:
    case CONTENT_MATCH.FALSE:
      setTileColor(tile, COLORS.RED);
      break;
    default:
      setTileColor(tile, COLORS.ORANGE);
  }
}

// Utility function to get tile and content from a given element id.
function getTileAndContent(id) {
  const element = document.getElementById(id);
  const tile = element.closest('.metric-tile');
  const content = element.textContent.trim();
  return { tile, content };
}

// Update tile color for average timestamp correctness.
const avgTimeStampCorr = getTileAndContent('avgTimeStampCorr');
const avgTimeStampCorrContent = parseFloat(avgTimeStampCorr.content);
updateAvgTimeCorrTileColor(avgTimeStampCorrContent, avgTimeStampCorr.tile);

// Update tile color for the most frequent timestamp correctness.
const mostFreqTimestampCorr = getTileAndContent('most_frequent_timestamp_correctness');
updateFrequentMetricTileColor(mostFreqTimestampCorr.content, mostFreqTimestampCorr.tile);

// Update tile color for the most frequent category.
const mostFreqCategory = getTileAndContent('most_frequent_category');
updateFrequentMetricTileColor(mostFreqCategory.content, mostFreqCategory.tile);

// Trigger a resize event for the plots to adapt to the new size.
setTimeout(() => window.dispatchEvent(new Event('resize')), 0);
