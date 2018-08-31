# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 13:52:29 2018

http://bbs.cantonese.asia/forum-118-1.html
881 881 十八樓C座  2018-08-27
881 光明頂  2018-08-27
@author: SF
"""
import os
import sys
import time
import re
import pandas

import zipfile
import shutil

from ffmpy import FFmpeg   

from utility import *
from youtubes import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

#youtubeacc = 'omegawea@gmail.com'
#setyoutubeacc(youtubeacc)
#playlists = listvdos()
#%%
hostname = 'http://bbs.cantonese.asia/'
topic = 'forum-118-1.html'
urlcode = urlsource(hostname + topic)
topictemplate = r'''a href=\"(\S+)\" onclick=\"atarget\(this\)\" class=\"s xst\">\w+\s+%s\s+(\w+)-(\w+)-(\w+)</a>'''
posttemplate = r'''<a href=\"(https://u\d+.pipipan.com/fs/\d+-\d+)\"'''
pydir = os.getcwd() + '\\'

radiocodes = ['十八樓C座', '光明頂']
code2list = {
        '十八樓C座': '18F.Block.C.', 
        '光明頂'   : 'Summit.',
             }
zipsuffixes = {
        '十八樓C座'    : '-1230-1300.zip',
        '光明頂'       : '-2300-0000.zip',
        }
radiostitles = {
    '1300.wma' : '18F.Block.C.',
    '0000.mp3' : 'Summit.',
    }
#%%
def radiodl(youtubeacc):
#if True:
#    youtubeacc = 'omegawea@gmail.com'
    setyoutubeacc(youtubeacc)
    # load playlist from youtube
    playlist = listvdos()
    # Initialize source address and matches
    matches = {}
    # loop target radio codes
    for radiocode in radiocodes:
        # find all matches on radio codes
        matches[radiocode] = re.findall(topictemplate%radiocode, urlcode)
        # Retrieve link and datetime from matches
        radioposts = {}
        # loop matches per code
        for match in matches[radiocode]:
            # check if radio ep exists in youtube
            ep = (code2list[radiocode] + '-'.join(match[1:4]) + '.mp4')
            if ep not in playlist:
                xprint ('Downloading %s'%ep)                
#                postlink = re.search(posttemplate, urlsource(max(radioposts.items())[0])).group(1)
                postlink = re.search(posttemplate, urlsource(match[0])).group(1)
                # Target to .py folder
                options = Options()        
                options.add_argument("user-data-dir=C:\\Users\\%s\\AppData\\Local\\Google\\Chrome\\User Data"%(os.getlogin()))
#                options.add_argument(r('download.default_directory=' + pydir))        
                options.add_experimental_option("prefs", {
                  "download.default_directory": pydir,
                  "download.prompt_for_download": False,
                  "download.directory_upgrade": True,
                  "safebrowsing.enabled": True
                })
                driver = webdriver.Chrome(chrome_options=options)
                driver.get(postlink)
                element = driver.find_element_by_id("free_down_link").click()
                # Target to downloads folder
                while not any(file.endswith(zipsuffixes[radiocode]) for file in os.listdir('.')):            
                    pass # Wait until file is downloaded            
                # Unzip and Move Files
                time.sleep(3)
                zfiles = os.listdir('.')
                for zfile in zfiles:
                    if zfile.endswith(zipsuffixes[radiocode]):
                        # Unzip and Del
                        zref = zipfile.ZipFile(zfile, 'r')
                        zref.extractall()
                        zref.close()
                        # Move and Del
                        radiofilespath = zfile.replace('.zip', '') + '\\'
                        radiofiles = os.listdir(radiofilespath)
                        for radiofile in radiofiles:
                            string = radiofile.split('-')
                            title = radiostitles[string[-1]]
                            date = string[1][:4] + '-' + string[1][4:6] + '-' + string[1][6:]   
                            newname = title + date + radiofile[-4:]
                            try:
                                os.rename(radiofilespath + radiofile, radiofilespath + newname)                        
                                shutil.move(radiofilespath + newname, pydir)
                            except Exception as e:
                                xprint (e)
                                os.remove(radiofilespath + newname)  
                        os.remove(zfile)
                        shutil.rmtree(radiofilespath)
                driver.quit()                
    #Delete Unconfirmed....crdownload files if any
    files = os.listdir('.')
    for file in files:
        if file.startswith('Unconfirmed ') and file.endswith('.crdownload'):      
            try:
                os.remove(file)   
            except Exception as e:
                xprint (e)
#%%
    # Convert mp3 to x2 mp4
    files = os.listdir('.')
    for file in files:
        if file.endswith('.mp3'):
            #for %a in (Summit.*.mp3) do ffmpeg -i %a -filter:a "atempo=2.0" %a".mp3"           
            string = file.split('-')
            ff = FFmpeg(
                    inputs={file: None},
                    outputs={file[:-4] +'x2.mp3': '-filter:a \"atempo=2.0\"'}
                    )
            ff.cmd
            ff.run()
            try:
                shutil.move(file, '\\\\GBE_NAS\\music')
            except Exception as e:
                xprint (e)
                os.remove(file)
            os.rename(file[:-4] +'x2.mp3', file[:-4] +'.mp3')
#%%
    # Convert wma to mp3
    files = os.listdir('.')
    for file in files:
        if file.endswith('.wma'):
            #for %a in (*.wma) do ffmpeg -i %a -ab 32 %a".mp3"  
            ff = FFmpeg(
                    inputs={file: None},
                    outputs={file[:-4] +'.mp3': '-ab 32'}
                    )
            ff.cmd
            ff.run()
            os.remove(file)
#%%
    # Convert mp3 to mp4
    files = os.listdir('.')
    for file in files:
        if file.endswith('.mp3'):
#            #for %a in (*.mp3) do "ffmpeg" -loop 1 -r 1 -i "image.jpg" -vcodec mpeg4 -i %a -shortest -acodec copy %a".mp4"
            ff = FFmpeg(
                    inputs={'image.jpg': '-loop 1 -r 1', file: '-vcodec mpeg4'},
                    outputs={file[:-4] +'.mp4': '-shortest -acodec copy'}
                    )
            ff.cmd
            ff.run()    
            os.remove(file)
#%%
    # Upload mp4 to youtube
    files = os.listdir('.')
    for file in files:
        if file.endswith('.mp4'):
            uploadvdo(['--file=%s'%(file), '--title=%s'%(file)])
            os.remove(file)
#            shutil.rmtree(pydir + '\\' + file)
#%%
    # Remove oauth json
    files = os.listdir(".")
    for file in files:
        if file.startswith('--file=') and file.endswith('-oauth2.json'):
            os.remove(file)
#            shutil.rmtree(pydir + '\\' + file)