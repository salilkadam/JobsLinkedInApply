import random
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from loguru import logger


class LinkedInAuthenticator:

    def __init__(self, driver=None):
        self.driver = driver
        self.email = ""
        self.password = ""
        logger.debug(f"LinkedInAuthenticator initialized with driver: {driver}")

    def set_secrets(self, email, password):
        self.email = email
        self.password = password
        logger.debug(f"Secrets set with email: {email}")

    def start(self):
        logger.info("Starting Chrome browser to log in to LinkedIn.")
        self.driver.get('https://www.linkedin.com/feed')
        self.wait_for_page_load()

        time.sleep(3)

        if self.is_logged_in():
            logger.info("User is already logged in. Skipping login process.")
            return
        else:
            logger.info("User is not logged in. Proceeding with login.")
            self.handle_login()

    def handle_login(self):
        logger.info("Navigating to the LinkedIn login page...")
        self.driver.get("https://www.linkedin.com/login")
        if 'feed' in self.driver.current_url:
            logger.debug("User is already logged in.")
            return
        try:
            self.enter_credentials()
            self.submit_login_form()
        except NoSuchElementException as e:
            logger.error(f"Could not log in to LinkedIn. Element not found: {e}")
        time.sleep(random.uniform(3, 5))
        self.handle_security_check()

    def enter_credentials(self):
        try:
            logger.debug("Entering credentials...")
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(self.email)
            logger.debug(f"Email entered: {self.email}")
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            logger.debug("Password entered.")
        except TimeoutException:
            logger.error("Login form not found. Aborting login.")
            logger.error("Login form not found. Aborting login.")

    def submit_login_form(self):
        try:
            logger.debug("Submitting login form...")
            login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            login_button.click()
            logger.debug("Login form submitted.")
        except NoSuchElementException:
            logger.error("Login button not found. Please verify the page structure.")

    def handle_security_check(self):
        try:
            logger.debug("Handling security check...")
            WebDriverWait(self.driver, 10).until(
                EC.url_contains('https://www.linkedin.com/checkpoint/challengesV2/')
            )
            logger.warning("Security checkpoint detected. Please complete the challenge.")
            WebDriverWait(self.driver, 300).until(
                EC.url_contains('https://www.linkedin.com/feed/')
            )
            logger.info("Security check completed")
        except TimeoutException:
            logger.error("Security check not completed. Please try again later.")

    def is_logged_in(self):
        # target_url = 'https://www.linkedin.com/feed'
        #
        # # Navigate to the target URL if not already there
        # if self.driver.current_url != target_url:
        #     logger.debug(f"Navigating to target URL: {target_url}")
        #     self.driver.get(target_url)

        try:
            # Increase the wait time for the page elements to load
            logger.debug("Checking if user is logged in...")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'share-box-feed-entry__trigger'))
            )

            # Check for the presence of the "Start a post" button
            buttons = self.driver.find_elements(By.CLASS_NAME, 'share-box-feed-entry__trigger')
            logger.debug(f"Found {len(buttons)} 'Start a post' buttons")

            for i, button in enumerate(buttons):
                logger.debug(f"Button {i + 1} text: {button.text.strip()}")

            if any(button.text.strip().lower() == 'start a post' for button in buttons):
                logger.info("Found 'Start a post' button indicating user is logged in.")
                return True

            profile_img_elements = self.driver.find_elements(By.XPATH, "//img[contains(@alt, 'Photo of')]")
            if profile_img_elements:
                logger.info("Profile image found. Assuming user is logged in.")
                return True

            logger.info("Did not find 'Start a post' button or profile image. User might not be logged in.")
            return False

        except TimeoutException:
            logger.error("Page elements took too long to load or were not found.")
            return False

    def wait_for_page_load(self, timeout=10):
        try:
            logger.debug(f"Waiting for page to load with timeout: {timeout} seconds")
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            logger.debug("Page load completed.")
        except TimeoutException:
            logger.error("Page load timed out.")
