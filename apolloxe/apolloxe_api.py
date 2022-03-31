from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime

import asyncio
import concurrent.futures


class ApolloXeApi:
    def __init__(self) -> None:
        self.chrome_driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
        self.loop = asyncio.get_running_loop()

    async def get_view(self, url):
        await self.loop.run_in_executor(None, self.chrome_driver.get, url),

    async def login(self, username: str, password: str, time_out: int = 20):
        wait = WebDriverWait(self.chrome_driver, timeout=time_out)

        u = wait.until(EC.presence_of_element_located((By.NAME, 'userName')))
        p = wait.until(EC.presence_of_element_located((By.NAME, 'password')))

        # u = self.chrome_driver.find_element(by=By.NAME, value='userName')
        # p = self.chrome_driver.find_element(by=By.NAME, value='password')

        await asyncio.gather(
            self.loop.run_in_executor(None, u.send_keys, username),
            self.loop.run_in_executor(None, p.send_keys, password),
        )

    async def find_button_2_click(self, target, time_out: int = 20):
        wait = WebDriverWait(self.chrome_driver, timeout=time_out)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//span[text()=\'{target}\']')))
        # button = self.chrome_driver.find_element(by=By.XPATH, value=f'//span[text()=\'{target}\']')
        button.click()

    async def wait_check_in_done(self, time_out: int = 20):
        wait = WebDriverWait(self.chrome_driver, timeout=time_out)
        wait.until(EC.element_to_be_clickable((By.XPATH, f'//span[text()=\'下班\']')))
        button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[contains(@class, \'btn new-window-title-button\')]')))
        button.click()

        # wait.until(EC.invisibility_of_element_located((By.XPATH, f'//span[text()=\'下班\']')))
        await self.find_button_2_click('打卡紀錄')
        try:
            n: str = datetime.now().strftime('%Y/%m/%d')
            wait.until(lambda d: d.find_element(by=By.XPATH, value=f'//td[text()=\'{n}\']'))
            print('Check in success')
        except TimeoutException as e:
            print('Check in fail')

