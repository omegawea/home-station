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
import base64

import zipfile
import shutil

from ffmpy import FFmpeg   

from library.utility import *
from library.youtubes import *
from library.endecrytion import *
#%%
pydir = os.getcwd() + '\\'

radiocodes = ['十八樓C座', '光明頂']
zipsuffixes = {
        '十八樓C座'    : '-1230-1300.zip',
        '光明頂'       : '-2300-0000.zip',
        }

RadioProcesses = None
rplist = [
        'radioconv',
        'radiounziprename',
        'radioul',
        'radiodl',
        ]
rpstatus = {
        }
def setrpstatus(name, status):
    if name in rpstatus:
        rpstatus[name] = status
    return 0
def getrpstatus(name):
    if name in rpstatus:
        return rpstatus[name]
    return None
#%%            
def radiounziprename():
    radiostitles = {
        '1300.wma' : '18F.Block.C.',
        '0000.mp3' : 'Summit.',
        }
    xprint ('Radio Unzip and Rename Process...')
    zfiles = os.listdir('.')
    time.sleep(3)
    # loop target radio codes
    for radiocode in radiocodes:
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
#%%
def radioconv():
    xprint ('Radio Conversion Process...')
    radiounziprename()
    # Convert mp3 to x2 mp3
    files = os.listdir('.')
    for file in files:
        if file.startswith('Summit.') and file.endswith('.mp3') and not file.endswith('x2.mp3'):
            #for %a in (Summit.*.mp3) do ffmpeg -i %a -filter:a "atempo=2.0" %a".mp3"           
            string = file.split('-')
            ff = FFmpeg(
                    inputs={file: None},
                    outputs={file[:-4] +'x2.mp3': '-filter:a \"atempo=2.0\"'}
                    )
            ff.cmd
            try:
                ff.run()
            except Exception as e:
                xprint (e)
            try:
                shutil.move(file, '\\\\GBE_NAS\\music')
            except Exception as e:
                xprint (e)
            try:
                os.remove(file)
            except Exception as e:
                xprint (e)
#            os.rename(file[:-4] +'x2.mp3', file[:-4] +'.mp3')
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
            try:
                ff.run()
            except Exception as e:
                xprint (e)
            try:
                os.remove(file)
            except Exception as e:
                xprint (e)
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
            try:
                ff.run()
            except Exception as e:
                xprint (e)
            try:
                os.remove(file)
            except Exception as e:
                xprint (e)
#%%
def radioul():
    xprint ('Radio Upload Process...')
    
    global RadioProcesses
#if True:
    now = datetime.datetime.now()
#    nexttime = now + datetime.timedelta(hours = 3)
#    RadioProcesses['radioconv'].reset(datetime.time(nexttime.hour, nexttime.minute, nexttime.second))
#    nexttime = now + datetime.timedelta(hours = 5)
#    RadioProcesses['radiodl'].reset(datetime.time(nexttime.hour, nexttime.minute, nexttime.second))
    nexttime = now + datetime.timedelta(hours = 3)
    RadioProcesses['radioconv'].reset(datetime.time(nexttime.hour, nexttime.minute, nexttime.second))
    nexttime = now + datetime.timedelta(hours = 1)
    RadioProcesses['radiodl'].reset(datetime.time(nexttime.hour, nexttime.minute, nexttime.second))
    # load playlist from youtube
    try:
        playlist = listvdos()
    except Exception as e:
        xprint (e)
        return
    # Upload mp4 to youtube
    files = os.listdir('.')
    for file in files:
        if file.endswith('.mp4'):
            if file not in playlist:
                try:
                    uploadvdo(['--file=%s'%(file), '--title=%s'%(file)])
                except Exception as e:
                    xprint (e)
            try:
                os.remove(file)
            except Exception as e:
                xprint (e)
    # Remove oauth json
    files = os.listdir(".")
    for file in files:
        if file.startswith('--file=') and file.endswith('-oauth2.json'):
            try:
                os.remove(file)
            except Exception as e:
                xprint (e)         
#%%
def radiodl():
    xprint ('Radio Download Process...')
    hostname = 'http://' + decrypt('ggx.hfsytsjxj.fxnf/')
    topic = 'forum-118-1.html'
    urlcode = urlsource(hostname + topic)
    
    topictemplate = r'''a href=\"(\S+)\" onclick=\"atarget\(this\)\" class=\"s xst\">\w+\s+%s\s+(\w+)-(\w+)-(\w+)</a>'''
    posttemplate = r'''<a href=\"(https://u\d+.pipipan.com/fs/\d+-\d+)\"'''
    
    code2list = {
            '十八樓C座': '18F.Block.C.', 
            '光明頂'   : 'Summit.',
                 }
    
    global RadioProcesses
#if True:
    now = datetime.datetime.now()
#    nexttime = now + datetime.timedelta(hours = 3)
#    RadioProcesses['radioconv'].reset(datetime.time(nexttime.hour, nexttime.minute, nexttime.second))
#    nexttime = now + datetime.timedelta(hours = 5)
#    RadioProcesses['radioul'].reset(datetime.time(nexttime.hour, nexttime.minute, nexttime.second))
    nexttime = now + datetime.timedelta(hours = 3)
    RadioProcesses['radioconv'].reset(datetime.time(nexttime.hour, nexttime.minute, nexttime.second))
    nexttime = now + datetime.timedelta(hours = 1)
    RadioProcesses['radioul'].reset(datetime.time(nexttime.hour, nexttime.minute, nexttime.second))
    
    # load playlist from youtube
    try:
        playlist = listvdos()
    except Exception as e:
        xprint (e)
        return
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
                postlink = re.search(posttemplate, urlsource(match[0])).group(1)
                explorer = Chrome()
                explorer.browse(postlink)
                explorer.click_by_id('''free_down_link''')
                while not any(file.endswith(zipsuffixes[radiocode]) for file in os.listdir('.')):            
                    pass # Wait until file is downloaded
                explorer.kill()     
    # Delete Unconfirmed....crdownload files if any
    files = os.listdir('.')
    for file in files:
        if file.startswith('Unconfirmed ') and file.endswith('.crdownload'):      
            try:
                os.remove(file)   
            except Exception as e:
                xprint (e)
#%%
def radioeps(youtubeacc):
    global RadioProcesses
    try:        
        setyoutubeacc(youtubeacc)
        xprint ('Selected Youtube Account.')
    except Exception as e:
        xprint (e)
        return
    RadioProcesses = {}
#    print (globals())
    for rpname in rplist:
        rpstatus = getrpstatus(rpname)
        if rpstatus == None:
            setrpstatus(rpname, STATUS['RUN'])
#            RadioProcesses[rpname] = HomeProcess(globals()[rpname](), datetime.time(00, 00, 00), 300)
#            if rpname == 'radioconv':
#                RadioProcesses['radioconv'] = HomeProcess(radioconv, datetime.time(8, 0, 0), 300)
#            elif rpname == 'radioul':
#                RadioProcesses['radioul'] = HomeProcess(radioul, datetime.time(10, 0, 0), 3600)
#            elif rpname == 'radiodl':
#                RadioProcesses['radiodl'] = HomeProcess(radiodl, datetime.time(0, 0, 0), 3600 * 24)
            if rpname == 'radioconv':
                RadioProcesses['radioconv'] = HomeProcess(radioconv, datetime.time(8, 0, 0), 3600 * 6)
            elif rpname == 'radioul':
                RadioProcesses['radioul'] = HomeProcess(radioul, datetime.time(10, 0, 0), 3600 * 24)
            elif rpname == 'radiodl':
                RadioProcesses['radiodl'] = HomeProcess(radiodl, datetime.time(0, 0, 0), 300)
