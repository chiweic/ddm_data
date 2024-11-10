# enable the infinite scroll with selenium
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import json
import glob
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from supabase import create_client
import datetime


def write_output (page_source, output_file):
    # write out to file
    with open(output_file, "w", encoding="utf-8") as fp:
        fp.write(page_source)


import calendar
from datetime import date

# Function to get start and end date for each month in 2024
def get_month_start_end_dates(year):
    month_dates = []
    for month in range(1, 13):
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)
        month_dates.append((start_date, end_date))
    return month_dates


def waitfor_content_ready():
    try:
        # wait until the content become static 
            # this is the way we wait for content become static 
            WebDriverWait(driver, refresh_wait_time).until (
                    #content.get_attribute('style') == 'position: static; zoom: 1;'
                    EC.text_to_be_present_in_element_attribute(
                        locator = (By.ID, 'Content'), attribute_= 'style', text_='position: static; zoom: 1;'
                    )
            )

    except Exception as err:
        logging.error(err)


if __name__ == '__main__':
    
    # logging options
    logging.basicConfig(level=logging.INFO)

    # load environments
    load_dotenv()
    
    # root event URL from main web site
    event_url = os.getenv('EVENT_URL')
    html_directory=os.getenv('HTML_DIRECTORY')
    refresh_wait_time = int(os.getenv('REFRESH_WAIT_TIME'))
    default_wait_time = int(os.getenv('DEFAULT_WAIT_TIME'))

    use_supabase = False
    if use_supabase:
        # if we are using supabase client SDK
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)



    # try to crawl all months during 2024
    month_dates = get_month_start_end_dates(year=2025)
    
     
    # main loop
    try:
        
        # driver = webdriver.Chrome()
        driver = webdriver.Edge()
        driver.get (url=event_url)
        logging.info('load target URL {}'.format(event_url))
        
        # loop on dates/month
        for month, (start_date, end_date) in enumerate(month_dates, start=1):
            
            logging.info(f"Month {month}: Start Date = {start_date}, End Date = {end_date}")
            datestring='{}_{}'.format(start_date, end_date)

            # initialized parameters
            last_height=0
            region_crawled = 1

            # wait until the content become static 
            # this is the way we wait for content become static 
            waitfor_content_ready()

            # loop until all regions are crawled...
            regions = ['北北基', '桃竹苗', '中彰投','雲嘉南','高屏','宜花東','海外']

            for reg in regions:

                # set up the clicks/choice on region
                # click to begining of page
                driver.execute_script("window.scrollTo(0, 0);")

                # wait for content to be ready
                waitfor_content_ready()

                # clear button
                reset_btn = driver.find_element(By.XPATH, "//div[@class='BtnCommon large']//input[@value='清除重填']")
                reset_btn.click()

                # search/option from the FormTable
                query_section = driver.find_element(By.CLASS_NAME,'FormTable')
                                    
                # form xpath expression
                xpath_exp=".//span[@class='search-span arrow' and text()='{}']".format(reg)
                region_btn = query_section.find_element(By.XPATH, xpath_exp)
                region_btn.click()

                # do nothing on categories, default to '全部'

                # select time
                next_3months_btn = query_section.find_element(By.XPATH, ".//span[@class='search-span reflash' and text()='最近三個月']")
                next_3months_btn.click()

                # self-defined
                self_defined_btn=query_section.find_element(By.XPATH, ".//span[@class='search-span reflash' and text()='自訂']")
                self_defined_btn.click()

                # calendar default confirm
                # enter text box, must be %Y-%M-%D
                start_date_box = query_section.find_element(By.XPATH, ".//span[@class='time_custom_box show']//input[@title='開始日期']")
                start_date_box.send_keys(start_date.strftime("%Y-%m-%d"))

                # confirm on calendar pick
                cal_btn = driver.find_element(By.XPATH, "//td[contains(@class, 'ui-datepicker-current-day')]/a")
                cal_btn.click() 

                end_date_box = query_section.find_element(By.XPATH, ".//span[@class='time_custom_box show']//input[@title='結束日期']")
                end_date_box.send_keys(end_date.strftime("%Y-%m-%d"))

                # confirm on calendar pick
                cal_btn = driver.find_element(By.XPATH, "//td[contains(@class, 'ui-datepicker-current-day')]/a")
                cal_btn.click() 

                # submit
                submit_btn = driver.find_element(By.XPATH, "//div[@class='BtnCommon large']//input[@value='確認送出']")
                submit_btn.click()

                
                # wait until the content become static 
                # this is the way we wait for content become static 
                waitfor_content_ready()

                while True:

                    # scroll to bottom
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    # wait for all content to load
                    waitfor_content_ready()

                    # until we are done...
                    new_height=driver.execute_script('return document.body.scrollHeight')

                    if new_height == last_height:
                        break
                    else:
                        last_height=new_height    

                    #time.sleep(default_wait_time)
                    
                # write output
                directory = '{}/{}'.format(html_directory, datestring)
                html_file = '{}/{}.html'.format(directory, reg)

                # create folder if not already
                if not os.path.exists(directory):
                    os.makedirs(directory)


                # write the html out
                write_output(driver.page_source, html_file)
                logging.info('write {}'.format(html_file))

            
    
    except Exception as e:
        logging.error('error: {}'.format(e))
    
    
    finally:

        # we have the source of the page
        # close the browser
        driver.quit()    
