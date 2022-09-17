# import
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs
from facebook_scraper import get_posts
import csv

import time
import urllib.request
import pandas as pd
import json
import re
import datetime


      
def openSeeMore(browser):
    readMore = browser.find_elements(By.XPATH, "//div[text()='See more']")
    if len(readMore) > 0:    
        count = 0
        for i in readMore:
            action=ActionChains(browser)
            try:
                action.move_to_element(i).click().perform()
                count += 1
            except:
                try:
                    browser.execute_script("arguments[0].click();", i)
                    count += 1
                except:
                    continue
        if len(readMore) - count > 0:
            print('readMore issue:', len(readMore) - count)
        time.sleep(1)
    else:
        pass

def getBack(browser):
    if not browser.current_url.endswith('reviews'):
        print('redirected!!!')
        browser.back()
        print('got back!!!')

def archiveAtEnd(browser, reviewList):
    browser.execute_script("window.scrollTo(0, -document.body.scrollHeight);") # scroll back to the top
    time.sleep(10)
        
    for idx, l in enumerate(reviewList):
        if idx % 10 == 0:
            if idx < 15:
                browser.execute_script("arguments[0].scrollIntoView();", reviewList[0])
            else:
                browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx-15])
            
            time.sleep(1)
            try:
                browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx+15])
            except:
                browser.execute_script("arguments[0].scrollIntoView();", reviewList[-1])

            time.sleep(1)
            browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx])
            
            for r in range(2):
                time.sleep(3)
                try:
                    browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx+5])
                    time.sleep(3)
                except:
                    browser.execute_script("arguments[0].scrollIntoView();", reviewList[-1])
                browser.execute_script("arguments[0].scrollIntoView();", reviewList[idx+r*3])
                time.sleep(3)
                with open(f'./PATH/{str(idx)}_{r}.html',"w", encoding="utf-8") as file:
                    source_data = browser.page_source
                    bs_data = bs(source_data, 'html.parser')
                    file.write(str(bs_data.prettify()))
                    print(f'written: {idx}_{r}')

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)

driver = webdriver.Chrome('/Users/qianzihou/Downloads/chromedriver', chrome_options=chrome_options)

driver.get("http://www.facebook.com")

username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))

username.clear()
username.send_keys("airsocosal@gmail.com")
password.clear()
password.send_keys("Air20010423")

# log in
button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()



#wait 5 seconds to allow your new page to load
time.sleep(5)
images = [] 

search = driver.find_element(By.XPATH, "//input[@aria-label='Search Facebook']")
search.send_keys("Illegal alien Latino")
search.send_keys(Keys.RETURN)

time.sleep(2)

search = driver.find_element(By.XPATH, '//span[text()="Posts"]').click()
time.sleep(5)
rec = driver.find_element(By.XPATH, "//input[@aria-label='Recent Posts']").click()

now = driver.current_url
print("now", now)

# # posts = get_posts(post_urls=now)

# print([now])

# for post in get_posts('nintendo', pages=1):
#     print(post['post_url'])

mobile = now[:8] + "m." + now[12:]
print("mobv", mobile)
driver.get(mobile)


count = 0
switch = True
old_numReviews = 0
specifiedNumber = 3 # number of reviews to get
url = []

while switch:
    count += 1

    # openSeeMore(driver)

    # wait = WebDriverWait(driver, 10)
    # element = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@class="rrjlc0n4 jwegzro5 jyk7a11d om3e55n1 szd3m19j htg95q9y"]'))).click()

    result = []
    links_l = []

    links = driver.find_elements(By.XPATH, '//a[@class="_26yo"]')
    texts = [el.text for el in driver.find_elements(By.XPATH, '//div[@class="_5rgt _5nk5 _5msi"]/div/span/span/p')]
    names = [el.text for el in driver.find_elements(By.XPATH, '//h3[@class="_52jd _52jb _52jh _5qc3 _4vc- _3rc4 _4vc-"]/span/strong/a')]
    

    for pos in texts:
        pos = pos.replace("\n", " ")
        # pos = pos.text
        pos = pos[:30]

    print(links)
    print(texts)
  
    for i in links:
        try:
            ActionChains(driver).move_to_element(i).perform()
            url = i.get_attribute('href')
            if url in links_l:
                continue
            else:
                links_l.append(url)
        except:
            pass

    print(links_l)

    # scroll to the bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    # reviewList = driver.find_elements(By.XPATH, "//div[@class='du4w35lb k4urcfbm l9j0dhe7 sjgh65i0']")
    
    # termination condition
    if count >= specifiedNumber:
        # archiveAtEnd(driver, reviewList)
        switch = False

result = zip(names,texts, links_l)

# result.append(texts)
# result.append(links_l)

with open('some.csv', 'w', newline='', encoding='utf-8') as f:
    header = ['names','text','links_l']
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(result) 

time.sleep(5)

