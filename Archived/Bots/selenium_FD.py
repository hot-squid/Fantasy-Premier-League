import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Creates a useragent without having to login
# These get views up. Not necessarily reads -- check.

# Generate a random User-Agent
ua = UserAgent()
options = Options()
options.set_preference("general.useragent.override", ua.random)  # Set User-Agent for Firefox

# Set up WebDriver
driver = webdriver.Firefox(options=options)
driver.get("https://medium.com/@hotsquid/improved-fixture-difficulty-rating-opponents-to-target-and-avoid-9a38c7f8228b")

# Pause to allow the page to load
time.sleep(1)

# Scroll down to ensure elements are visible (if necessary)
driver.execute_script("window.scrollTo(0, 100);")
time.sleep(4)

# Scroll down to ensure elements are visible (if necessary)
driver.execute_script("window.scrollTo(100, 200);")
time.sleep(8)

# Scroll down to ensure elements are visible (if necessary)
driver.execute_script("window.scrollTo(100, 0);")
time.sleep(7)

# Scroll down to ensure elements are visible (if necessary)
driver.execute_script("window.scrollTo(0, 200);")
time.sleep(10)

# Scroll down to ensure elements are visible (if necessary)
driver.execute_script("window.scrollTo(200, 150);")
time.sleep(10)

# Scroll down to ensure elements are visible (if necessary)
driver.execute_script("window.scrollTo(150, 300);")
time.sleep(15)

# Locate and click the clap button (using pw-multi-vote-icon class)
try:
    # Adjust the XPath to use the correct class
    like_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'pw-multi-vote-icon')]"))
    )
    ActionChains(driver).move_to_element(like_button).click().perform()
    print("Liked the article!")
except Exception as e:
    print(f"Unable to like the article: {e}")

# Locate the comment box, enter a comment, and submit it
try:
    # Locate the comment box using class and role
    comment_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'avg x') and @role='textbox']"))
    )
    comment_box.click()
    time.sleep(2)  # Pause for interaction

    # Type a comment (using ActionChains for contenteditable divs)
    comment_text = "Great insights, thanks for sharing!"
    ActionChains(driver).move_to_element(comment_box).click().send_keys(comment_text).perform()
    
    # Locate the submit button and click
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Respond')]"))
    )
    submit_button.click()
    print("Comment submitted!")
except Exception as e:
    print(f"Unable to comment: {e}")

# Pause to observe the action
time.sleep(4)

# Close the browser
driver.quit()
