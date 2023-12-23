from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest
import random
from selenium.webdriver.chrome.options import Options


options = Options()
options.add_argument(
    "--headless"
)  # Ensure GUI is off. Important for running in Jenkins
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")


class ChessverseE2ETest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.driver.quit()

    def test_login_happyPath(self):
        # checks if when the user logs in with correct credentials he is redirected to the options page
        self.driver.get("https://www.chessverse.cloud/login")

        wait = WebDriverWait(self.driver, 10)
        # check if all elements are present
        username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        login_button = self.driver.find_element(By.ID, "Login")

        username.send_keys("ccirone")
        password.send_keys("Ciao1234!")
        login_button.click()

        wait.until(EC.url_changes(self.driver.current_url))
        self.assertEqual(
            self.driver.current_url, "https://www.chessverse.cloud/options"
        )

    def test_login_wrongCredentials(self):
        # checks if when the user logs in with wrong credentials he is redirected to the login page
        self.driver.get("https://www.chessverse.cloud/login")

        wait = WebDriverWait(self.driver, 10)
        # check if all elements are present
        username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        login_button = self.driver.find_element(By.ID, "Login")

        username.send_keys("provaErrore")
        password.send_keys("provaErrore1")
        login_button.click()

        self.assertEqual(self.driver.current_url, "https://www.chessverse.cloud/login")

    def test_signup_happyPath(self):
        # generate a random nickname to avoid conflicts with other users
        nickname = "prova" + str(random.randint(0, 1000000))
        # checks if when the user signs up with correct credentials he is redirected to the login page
        self.driver.get("https://www.chessverse.cloud/signup")

        wait = WebDriverWait(self.driver, 10)
        # check if all elements are present
        username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        eloSelect = wait.until(EC.presence_of_element_located((By.ID, "elo")))
        signup_button = self.driver.find_element(By.ID, "Sign Up")

        # check if with all correct credentials the user is redirected to the login page
        username.send_keys(nickname)
        password.send_keys("Prova1!")
        eloSelect.send_keys("400")
        signup_button.click()

        wait.until(EC.url_changes(self.driver.current_url))
        self.assertEqual(self.driver.current_url, "https://www.chessverse.cloud/login")

    def test_signup_wrongUsername(self):
        # checks if when the user signs up with wrong credentials he is redirected to the signup page
        self.driver.get("https://www.chessverse.cloud/signup")

        wait = WebDriverWait(self.driver, 10)
        # check if all elements are present
        username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        eloSelect = wait.until(EC.presence_of_element_located((By.ID, "elo")))
        signup_button = self.driver.find_element(By.ID, "Sign Up")

        # check if with a nickname already taken the user isn't signed up
        username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        eloSelect = wait.until(EC.presence_of_element_located((By.ID, "elo")))
        username.send_keys("ccirone")
        password.send_keys("Ciao1234!")
        eloSelect.send_keys("400")
        signup_button.click()
        self.assertEqual(self.driver.current_url, "https://www.chessverse.cloud/signup")
    
    def test_signup_invalidPassword(self):
        # generate a random nickname to avoid conflicts with other users
        nickname = "prova" + str(random.randint(0, 1000000))
        # checks if when the user signs up with wrong credentials he is redirected to the signup page
        self.driver.get("https://www.chessverse.cloud/signup")
        
        wait = WebDriverWait(self.driver, 10)
        # check if all elements are present
        username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        eloSelect = wait.until(EC.presence_of_element_located((By.ID, "elo")))
        signup_button = self.driver.find_element(By.ID, "Sign Up")

        username.send_keys(nickname)
        password.send_keys("prova")
        eloSelect.send_keys("400")
        signup_button.click()
        self.assertEqual(self.driver.current_url, "https://www.chessverse.cloud/signup")
        
    def test_signup_invalidElo(self):
        # generate a random nickname to avoid conflicts with other users
        nickname = "prova" + str(random.randint(0, 1000000))
        # checks if when the user signs up with wrong credentials he is redirected to the signup page
        self.driver.get("https://www.chessverse.cloud/signup")
        
        wait = WebDriverWait(self.driver, 10)
        # check if all elements are present
        username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        eloSelect = wait.until(EC.presence_of_element_located((By.ID, "elo")))
        signup_button = self.driver.find_element(By.ID, "Sign Up")

        username.send_keys(nickname)
        password.send_keys("Ciao1234!")
        eloSelect.send_keys("1000")
        signup_button.click()
        self.assertEqual(self.driver.current_url, "https://www.chessverse.cloud/signup")
        

    def test_signout_login(self):
        # checks if when the user signs out he is redirected to the main page
        self.driver.get("https://www.chessverse.cloud/login")
        wait = WebDriverWait(self.driver, 10)
        username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        login_button = self.driver.find_element(By.ID, "Login")

        username.send_keys("ccirone")
        password.send_keys("Ciao1234!")
        login_button.click()
        wait.until(EC.url_changes(self.driver.current_url))
        self.assertEqual(
            self.driver.current_url, "https://www.chessverse.cloud/options"
        )

        button = self.driver.find_element(By.ID, "quit-button")
        self.driver.execute_script("arguments[0].click();", button)
        self.assertEqual(self.driver.current_url, "https://www.chessverse.cloud/")
        session_id = self.driver.execute_script(
            "return window.sessionStorage.getItem('session_id');"
        )
        self.assertEqual(session_id, "undefined")

    def test_signout_guest(self):
        # checks if when the guest signs out he is redirected to the main page
        self.driver.get("https://www.chessverse.cloud/")
        wait = WebDriverWait(self.driver, 10)
        # check if all elements are present
        playAsGuest_button = wait.until(
            EC.presence_of_element_located((By.ID, "play-as-guest"))
        )
        playAsGuest_button.click()
        wait.until(EC.url_changes(self.driver.current_url))
        self.assertEqual(
            self.driver.current_url, "https://www.chessverse.cloud/options"
        )
        wait = WebDriverWait(self.driver, 10)
        button = self.driver.find_element(By.ID, "quit-button")
        self.driver.execute_script("arguments[0].click();", button)
        self.assertEqual(self.driver.current_url, "https://www.chessverse.cloud/")

    def test_main_page_login(self):
        self.driver.get("https://www.chessverse.cloud/")
        wait = WebDriverWait(self.driver, 10)
        # check if all elements are present
        login_button = wait.until(EC.presence_of_element_located((By.ID, "login")))
        login_button.click()
        self.assertEqual(self.driver.current_url, "https://www.chessverse.cloud/login")

    def test_main_page_guest(self):
        self.driver.get("https://www.chessverse.cloud/")
        wait = WebDriverWait(self.driver, 10)
        # check if all elements are present
        playAsGuest_button = wait.until(
            EC.presence_of_element_located((By.ID, "play-as-guest"))
        )
        playAsGuest_button.click()
        wait.until(EC.url_changes(self.driver.current_url))
        self.assertEqual(
            self.driver.current_url, "https://www.chessverse.cloud/options"
        )


if __name__ == "__main__":
    unittest.main()
