import os
import logging
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchWindowException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Define paths, URLs, and credentials
extension_id = "caacbgbklghmpodbdafajbgdnegacfmo"
CRX_URL = f"https://clients2.google.com/service/update2/crx?response=redirect&prodversion=98.0.4758.102&acceptformat=crx2,crx3&x=id%3D{extension_id}%26uc&nacl_arch=x86-64"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
USER = os.getenv('GRADIENT_USER', '')
PASSW = os.getenv('GRADIENT_PASS', '')

# Download the extension if not already present
extension_path = "gradient_extension.crx"
if not os.path.exists(extension_path):
    logger.info('Downloading extension...')
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(CRX_URL, headers=headers)
        response.raise_for_status()
        with open(extension_path, 'wb') as f:
            f.write(response.content)
        logger.info('Extension downloaded successfully.')
    except requests.RequestException as e:
        logger.error(f'Failed to download extension: {e}')
        exit()

# Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_extension(extension_path)

# Initialize driver
logger.info('Installing extension and driver manager...')
try:
    driver = webdriver.Chrome(service=ChromeService("/usr/bin/chromedriver"), options=options)
except WebDriverException:
    logger.error('Could not start with chromedriver! Exiting...')
    exit()

# Load extension popup page and check login status
driver.get(f'chrome-extension://{extension_id}/popup.html')
driver.switch_to.window(driver.window_handles[-1])

# Check for rewards and login if needed
rewards_found = False
try:
    rewards_element = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "Helvetica") and contains(text(), "Today\'s Rewards")]'))
    )
    logger.info('Already Logged In!')
    rewards_found = True 
except TimeoutException:
    logger.info('Not Logged In. Proceeding with login.')
    try:
        wait = WebDriverWait(driver, 60)
        user = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Enter Email"]')))
        passw = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Enter Password"]')))
        submit = wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Log In")]')))

        user.send_keys(USER)
        passw.send_keys(PASSW)
        submit.click()

        wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Dashboard")]')))
        logger.info('Logged in successfully!')
    except TimeoutException:
        logger.error('Login failed or took too long. Exiting...')
        driver.quit()
        exit()

# Switch back to main extension page and handle any post-login popup
driver.switch_to.window(driver.window_handles[0])
logger.info('Loading Extension....')
driver.refresh()

try:
    button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "I got it")]'))
    )
    button.click()
    logger.info('Extension Loaded!')
except TimeoutException:
    pass

# Close any extra tabs that might have opened
for handle in driver.window_handles[1:]:
    try:
        driver.switch_to.window(handle)
        driver.close()
    except (NoSuchWindowException, WebDriverException) as e:
        logger.warning(f'Failed to close tab {handle}: {e}')

# Monitor connection status
connection_successful = False
while True:
    try:
        driver.switch_to.window(driver.window_handles[0])
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "Helvetica") and contains(text(), "Good")]'))
        )

        if not connection_successful:
            logger.info('Connection Successful!')
            connection_successful = True
    except TimeoutException:
        if connection_successful:
            logger.warning('Connection Error!')
            connection_successful = False

        driver.execute_script("location.reload();")

    
    time.sleep(21600)
