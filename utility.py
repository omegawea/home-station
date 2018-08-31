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
                      self.next_call = datetime.datetime.now() + datetime.timedelta(seconds = 1)
                  self.next_call = self.next_call.timestamp()
                  self._timer = threading.Timer(self.next_call - time.time(), self._run)
              else:
                  self.next_call += self.interval
                  self._timer = threading.Timer(self.next_call - time.time(), self._run)
              self._timer.start()
              self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
#%%
    