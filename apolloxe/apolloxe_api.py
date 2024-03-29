from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import date, datetime, timedelta
from typing import Optional, Tuple
from random import randrange

import asyncio
import re


class ApolloXeApi:
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self.chrome_driver = None
        self.loop = loop if loop else asyncio.get_running_loop()

    async def init_driver(self):
        chrome_driver = await self.loop.run_in_executor(None, ChromeDriverManager)
        excutable_path = await self.loop.run_in_executor(None, chrome_driver.install)
        self.chrome_driver = await self.loop.run_in_executor(None, webdriver.Chrome, excutable_path)

    async def destroy_driver(self):
        await self.loop.run_in_executor(None, self.chrome_driver.close)

    async def get_view(self, url):
        await self.loop.run_in_executor(None, self.chrome_driver.get, url)

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

    async def check_out_click(self, *, time_out: int = 20):
        wait = WebDriverWait(self.chrome_driver, timeout=time_out)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//div[@class=\'new-window-body clearfix\']//button[@class=\'ta_btn_cancel\']')))
        print('-----')
        print(button)
        button.click()

    async def wait_check_out_done(self, time_out: int = 20) -> bool:
        result: bool = False

        wait = WebDriverWait(self.chrome_driver, timeout=time_out)
        wait.until(EC.element_to_be_clickable((By.XPATH, f'//span[text()=\'上班\']')))
        button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[contains(@class, \'btn new-window-title-button\')]')))
        button.click()

        # wait.until(EC.invisibility_of_element_located((By.XPATH, f'//span[text()=\'下班\']')))
        await self.find_button_2_click('打卡紀錄')
        try:
            n: str = datetime.now().strftime('%Y/%m/%d')
            # wait.until(lambda d: d.find_element(by=By.XPATH, value=f'//td[text()=\'{n}\']'))
            xpath_string = f'//div[contains(@class, \'ta-scrollbar_wrapper ta_grid_table\')]//td[text()=\'{n}\']/following::td[3]'
            check_out = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_string)))
            if check_out.text:
                result = True
        except TimeoutException as e:
            result = False

        return result

    async def get_check_in_time(self) -> datetime:
        wait = WebDriverWait(self.chrome_driver, timeout=20)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[contains(@class, \'btn new-window-title-button\')]')))
        button.click()
        await self.find_button_2_click('打卡紀錄')

        n: str = datetime.now().strftime('%Y/%m/%d')
        xpath_string = f'//div[contains(@class, \'ta-scrollbar_wrapper ta_grid_table\')]//td[text()=\'{n}\']/following-sibling::td'

        result: datetime = None
        try:
            check_in = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_string)))
            print(check_in.text)

            m = re.match(r'^[0-9]{2}:[0-9]{2}(?=\/)', check_in.text)
            result = datetime.strptime(m.group(0), '%H:%M')
        except TimeoutException as e:
            print("Get Time Error")
            result = None

        return result

    def random_punch_out_time_with_checkin(self, checkin: datetime) -> Tuple[int, int]:
        punch_out: datetime = datetime(year=1900, month=1, day=1, hour=checkin.hour + 9, minute=checkin.minute)

        available_time = datetime(year=1900, month=1, day=1, hour=9, minute=30) - checkin
        if available_time < timedelta(minutes=0):
            available_time = timedelta(seconds=0)
            punch_out: datetime = datetime(year=1900, month=1, day=1, hour=18, minute=30)
            # return punch_out.hour, punch_out.minute
        elif available_time > timedelta(minutes=60):
            available_time = timedelta(minutes=60)
            punch_out: datetime = datetime(year=1900, month=1, day=1, hour=17, minute=30)

        stop = int(available_time.total_seconds() / 60) + 1
        minute = randrange(0, stop)

        punch_out += timedelta(minutes=minute)
        return punch_out.hour, punch_out.minute

    """
    TODO: rando punch in times
    """
    async def random_punch_in_time(self) -> datetime:
        hour = randrange(8, 9)
        minute = randrange(30, 60) if hour == 8 else randrange(0, 31)
        return datetime(hour=hour, minute=minute)
