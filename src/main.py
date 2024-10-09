import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchWindowException

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

extension_path = 'gradient_extension/gradient.crx'
profile_path = os.path.expanduser('/opt/data')

if not os.path.exists(extension_path):
    logger.error(f'Extension file not found at {extension_path}. Exiting...')
    exit()

USER = os.getenv('GRADIENT_USER', '')
PASSW = os.getenv('GRADIENT_PASS', '')

# Set Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--no-sandbox')
options.add_argument(f'--user-data-dir={profile_path}')
options.add_extension(extension_path)

logger.info('Installing extension and driver manager...')
try:
    driver = webdriver.Chrome(options=options)
except WebDriverException as e:
    try:
        driver_path = "/usr/bin/chromedriver"
        service = ChromeService(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
    except WebDriverException as e:
        logger.error('Could not start with chromedriver! Exiting...')
        exit()

driver.get('chrome-extension://caacbgbklghmpodbdafajbgdnegacfmo/popup.html')
driver.switch_to.window(driver.window_handles[-1])

rewards_found = False

try:
    rewards_element = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "Helvetica") and contains(text(), "Today\'s Rewards")]'))
    )
    logger.info('Already Logged In!.')
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

for handle in driver.window_handles[1:]:
    try:
        driver.switch_to.window(handle)
        driver.close()
    except (NoSuchWindowException, WebDriverException) as e:
        logger.warning(f'Failed to close tab {handle}: {e}')

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

    WebDriverWait(driver, 600)
