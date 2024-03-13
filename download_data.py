from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import glob
import shutil
import pandas as pd


def download_data(download_directory):
    try:
        driver = webdriver.Edge()
        driver.get('https://tasks.office.com/usiglobal.com/en-US/Home/Planner/#/plantaskboard?groupId=eaa399f6-8dc4-4269-9bbc-939174f45a14&planId=uhV1stNjdUSw7Dr40HyjJskAA4G4')
        time.sleep(5)  # Wait for the page to load
        # Click on the More Options button
        driver.find_element(By.CSS_SELECTOR, '#headerMoreOptionButton > i > svg').click()
        time.sleep(2)  # Wait for the dropdown to load
        # Click on the Export to Excel button
        driver.find_element(By.CSS_SELECTOR, '#fluent-default-layer-host > div > div > div > div > div > div > div > ul > li:nth-child(9) > button').click()
        time.sleep(5)  # Wait for the download to complete

        # Get the latest file
        files = glob.glob(f'{download_directory}\\2024 HPH IT Tasks*.xlsx')
        latest_file = max(files, key=os.path.getctime)
        # Remove the old file if it exists
        if os.path.exists('data\\%B_data.csv'):
            os.remove('data\\%B_data.csv')
        # Move the latest file to the data folder
        shutil.move(latest_file, time.strftime('data\\%B_data.csv'))

        # Save as CSV
        df = pd.read_excel(time.strftime('data\\%B_data.csv'))
        df.to_csv(time.strftime('data\\%B_data.csv'), index=False)
        driver.quit()
        print('Downloaded data successfully')
    except Exception as e:
        print('Error downloading data')
        print(e)
