# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 19:09:19 2018

@author: SF
"""
#%%
from threading import Event
from threading import Thread
import pandas
import datetime
import threading 
import time
import requests
#%%
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
#%%
STATUS = {
        'FAIL': -1,
        'NONE': 0,
        'RUN': 1,
        'STOP': 2,
        }

#%%
def xprint(*text):
    now = datetime.datetime.now()
    print (now.strftime("%Y-%m-%d %H:%M:%S: "), *text)

#%% https://yourbittorrent.com/?q=Tangled.The.Series.S02E09
def urlsource(url):
    r = requests.get(url)
    return r.text
#%%
def fmxlsx(filename, index):
    xlsx = pandas.read_excel(filename, None)
    # Extract aminenames into dict
    sheets = {}
    tabs = []
    for tab, sheet in xlsx.items():
        sheets[tab] = sheet
        sheets[tab].set_index(index, inplace=True, drop=True)
        tabs.append(tab)
    return sheets, tabs  
#%%
def getxlsxtabs(filename, index):        
    sheets, tabs = fmxlsx(filename, index)
    return tabs
#%%
def getxlsxsheets(filename, index):        
    sheets, tabs = fmxlsx(filename, index)
    return sheets  
#%%
def updatexlsx(filename, index, sheets):     
    temp, aminenames = fmxlsx(filename, index)       
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pandas.ExcelWriter(filename, engine='xlsxwriter')
    for tab, sheet in sheets.items():                    
        sheet.to_excel(writer, sheet_name = tab)
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()    
    return sheets  
#%%
def joinstatusus(filename, index, f_status, *statuses):
    if len(statuses) == 1:
        for key, sheet in f_status.items(): 
            f_status[key] = f_status[key].combine_first(statuses[0][key])
    return updatexlsx(filename, index, f_status)
#%%
class Future(object):
    def __init__(self):
        self._ev = Event()

    def set_result(self, result):
        self._result = result
        self._ev.set()

    def set_exception(self, exc):
        self._exc = exc
        self._ev.set()

    def result(self):
        self._ev.wait()
        if hasattr(self, '_exc'):
            raise self._exc
        return self._result
#%%
class HomeProcess(object):
    def __init__(self, function, begin, interval, *args, **kwargs):
        self._timer = None
        self.begin = begin
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
    #    self.next_call = time.time()
        self.next_call = None
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
              if self.next_call is None:
                  today = datetime.datetime.now()
                  self.next_call = datetime.datetime(today.year, today.month, today.day, self.begin.hour, self.begin.minute, 0)
                  if self.next_call.timestamp() < time.time():
                      self.next_call = datetime.datetime.now() + datetime.timedelta(seconds = 10)
                  self.next_call = self.next_call.timestamp()
                  self._timer = threading.Timer(self.next_call - time.time(), self._run)
              else:
                  self.next_call += self.interval
                  self._timer = threading.Timer(self.next_call - time.time(), self._run)
              self._timer.start()
              self.is_running = True
              
    def reset(self, begin):
        self._timer.cancel()
        self.next_call = None
        self.begin = begin
        self.is_running = False
        self.start()
        
    def stop(self):
        self._timer.cancel()
        self.is_running = False
#%%  
class Chrome():    
    def __init__(self,):
        # Killing until not found
        while (os.system("taskkill /f /im  chrome.exe") != 128): pass
        while (os.system("taskkill /f /im  chromedriver.exe") != 128): pass
        # Target to .py folder
        self.options = Options()        
        self.options.add_argument("user-data-dir=C:\\Users\\%s\\AppData\\Local\\Google\\Chrome\\User Data"%(os.getlogin()))
        #                options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')                
        #                options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--start-maximized")    
        #                options.add_argument(r('download.default_directory=' + pydir))        
        self.options.add_experimental_option("prefs", {
          "download.default_directory": (os.getcwd() + '\\'),
          "download.prompt_for_download": False,
          "download.directory_upgrade": True,
          "safebrowsing.enabled": True
        })
        self.driver = webdriver.Chrome(chrome_options=self.options)

    def _run(self):
        pass

    def browse(self, link):
        self.link = link        
        self.driver.get(self.link)

    def click_by_xpath(self, _xpath):
#        time.sleep(10)
        while True:
            try:
#                self.driver.find_element_by_xpath(_xpath).click()
                self.element = WebDriverWait(self.driver, 10).until(
                             EC.presence_of_element_located((By.XPATH, _xpath)))
                self.element.click()
                break
            except Exception as e:
                print (e)
        
    def click_by_id(self, _id):
#        time.sleep(10)
        while True:
            try:
#                self.driver.find_element_by_id(_id).click()
                self.element = WebDriverWait(self.driver, 10).until(
                             EC.presence_of_element_located((By.ID, _id)))
                self.element.click()
                break
            except Exception as e:
                print (e)       
        
    def kill(self):
        self.driver.quit()                  
    