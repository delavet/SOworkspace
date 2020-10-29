import sys
import time
sys.path.append('../util/')

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

browser = webdriver.Chrome()


def prepare_for_crawl():
    global browser
    query = 'soy'
    browser.get('https://www.bing.com/')
    est_en_select_div = browser.find_element_by_id('est_en')
    est_en_select_div.click()
    search_box = browser.find_element_by_class_name('b_searchbox')
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)


def crawl_concept(concept: str):
    global browser
    ret = []
    query = concept + ' explanation'
    '''
    browser.get('https://www.bing.com/')
    est_en_select_div = browser.find_element_by_id('est_en')
    est_en_select_div.click()
    '''
    search_box = browser.find_element_by_class_name('b_searchbox')
    search_box.clear()
    search_box.send_keys(query)
    time.sleep(0.5)
    search_box.send_keys(Keys.ENTER)
    results = browser.find_elements(By.CLASS_NAME, "b_algo")
    for result in results:
        try:
            item = result.find_element(By.XPATH, ".//p").text
        except:
            try:
                item = result.find_element(By.XPATH, ".///span").text
            except:
                item = None
        if item is not None:
            ret.append(item)
    
    return ret
    