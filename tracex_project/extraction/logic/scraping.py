"""This module contains the PoC for web scraping using Selenium."""
### Run "pip install selenium, webdriver_manager" before running this script ###
# pylint: disable=anomalous-backslash-in-string, bare-except, pointless-statement
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

input_path = Path(__file__).resolve().parent.parent / "content/inputs"

# Initialize the Firefox driver
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

# Navigate to the reddit page
driver.get(
    "https://www.reddit.com/r/COVID19positive/comments/1caz5sn/my_second_positive_has_been_a_nightmare/"
)

# Find an click the "read more" button if there is one
try:
    # As this button is found by id, it's only working for this and short enough posts.
    # Finding the button by calss isn't possible, due to the naming...
    read_more_button = WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.ID, "t3_1caz5sn-read-more-button"))
    )
    read_more_button.click()
except:
    pass

# Scrape the top posts
title = driver.find_element(
    By.CSS_SELECTOR,
    ".font-semibold.text-neutral-content-strong.m-0.text-18.xs\:text-24.mb-xs.px-md.xs\:px-0.xs\:mb-md",
)
content = driver.find_element(By.CSS_SELECTOR, ".mb-sm.mb-xs.px-md.xs\:px-0")
with open(input_path / "scraped_patient_journey.txt", "w") as f:
    f.write(f"{title.text}\n\n{content.text}")

# Scrape the comments
comments = driver.find_elements(
    By.CSS_SELECTOR, ".py-0.xs\:mx-xs.mx-2xs.inline-block.max-w-full"
)
for comment in comments:
    print(f"-----\n{comment.text}")

# Quit the driver
driver.quit()
