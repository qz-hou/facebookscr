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


keywords = ["Latino Drug dealers", 
            "Latino Invasion"]

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

for keyword in keywords:
    k_word = keyword.split(" ")
    for word in k_word:
        word = word.lower()

    driver.get("http://www.facebook.com")
    search = driver.find_element(By.XPATH, "//input[@aria-label='Search Facebook']")
    search.send_keys(keyword)
    search.send_keys(Keys.RETURN)

    time.sleep(2)

    search = driver.find_element(By.XPATH, '//span[text()="Posts"]').click()
    time.sleep(5)
    # rec = driver.find_element(By.XPATH, "//input[@aria-label='Recent Posts']").click()
    last_2 = driver.find_element(By.XPATH, '//div[@class="aglvbi8b b7mnygb8 iec8yc8l"]').click()
    time.sleep(1)
    cont = driver.find_element(By.XPATH, '(//div[@class="i85zmo3j alzwoclg jl2a5g8c cgu29s5g sl27f92c aeinzg81"])[3]').click()


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
    specifiedNumber = 8 # number of reviews to get
    url = []

    while switch:
        count += 1

        # openSeeMore(driver)

        # wait = WebDriverWait(driver, 10)
        # element = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@class="rrjlc0n4 jwegzro5 jyk7a11d om3e55n1 szd3m19j htg95q9y"]'))).click()

        result = []
        dates = []

        dates = [el.text for el in driver.find_elements(By.XPATH, '//div[@class="_52jc _5qc4 _78cz _24u0 _36xo"]/a[@class="_26yo"]')]
        links_l = [el.get_attribute('href') for el in driver.find_elements(By.XPATH, '//div[@class="_52jc _5qc4 _78cz _24u0 _36xo"]/a[@class="_26yo"]')]
        # links = driver.find_elements(By.XPATH, '//div[@class="_52jc _5qc4 _78cz _24u0 _36xo"]/a[@class="_26yo"]')
        texts = [el.text for el in driver.find_elements(By.XPATH, '//div[@class="story_body_container"]/div/div/span/span[@data-sigil="more"]')]
        names = [el.text for el in driver.find_elements(By.XPATH, '//div[@class="_4g34"]/h3')]
        

        # for i in range(len(texts)-1):
        #     texts[i] = texts[i].replace("\n", " ")
        #     # pos = pos.text
        #     texts[i] = texts[i][:20]

        actualPosts = driver.find_elements(By.XPATH, '//div[@class="story_body_container"]/div[@class="_5rgt _5nk5 _5msi"]')
        texts = []
        if actualPosts:
            for posts in actualPosts:
                text = ""
                ActionChains(driver).move_to_element(posts).perform()
                paragraphs = posts.text
                text += paragraphs
                texts.append(text)

        # print(links)

    
        # for i in links:
        #     try:
        #         ActionChains(driver).move_to_element(i).perform()
        #         date = i.text
        #         url = i.get_attribute('href')
        #         if url in links_l:
        #             continue
        #         else:
        #             links_l.append(url)
        #     except:
        #         pass




        # scroll to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # reviewList = driver.find_elements(By.XPATH, "//div[@class='du4w35lb k4urcfbm l9j0dhe7 sjgh65i0']")
        
        # termination condition
        if count >= specifiedNumber:
            # archiveAtEnd(driver, reviewList)
            switch = False

    for text in texts:
        pos = text
        pos1 = pos.lower()
        for j in range(len(k_word)-1):
            if k_word[j] not in pos1:
                i = texts.index(text)
                del texts[i]
                del links_l[i]
                del names[i]
                del dates[i]
                break
        if text in texts:
            i = texts.index(text)
            texts[i] = texts[i][:30]
            print(texts[i][:30])

    result = zip(names,dates,texts, links_l)

    # result.append(texts)
    # result.append(links_l)

    filename = keyword+".csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        header = ['names','dates','text','links_l']
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(result) 

    time.sleep(5)

