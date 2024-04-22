from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize the Firefox driver
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

# Navigate to the subreddit page
driver.get(
    "https://www.reddit.com/r/COVID19positive/comments/1c9mh4h/severe_periods_every_23_months_since_first/"
)
time.sleep(1)

read_more_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "t3_1c9mh4h-read-more-button"))
)
if read_more_button:
    read_more_button.click()
    time.sleep(0.5)

# Scrape the top posts
content = driver.find_element(By.CSS_SELECTOR, ".mb-sm.mb-xs.px-md.xs\:px-0")
with open(BASE_DIR / "extraction/content/inputs/scraped_patient_journey.txt", "w") as f:
    f.write(content.text)

# Scrape the comments
# comments = driver.find_elements(By.CSS_SELECTOR, ".py-0.xs\:mx-xs.mx-2xs.inline-block.max-w-full")
# for comment in comments:
#    print(comment.text)

# Quit the driver
driver.quit()
