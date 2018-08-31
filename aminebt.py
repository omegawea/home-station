# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 19:06:19 2018

@author: SF
"""
#%%
import os
import sys
from utility import *
from nas import *
import wikipedia #https://pypi.org/project/wikipedia/
import time
import re
import pandas
#%%   
#filename = 'amine.xlsx'
args = sys.argv[1:]
#%% 
def getwikiseps(filename, index):
    septemplate = r'''\d+\D+\d+\D+(\d+)'''
    
    aminenames = getxlsxtabs(filename, index)
    aminestatuses = {}
    for aminename in aminenames:
#        aminestatuses[aminename] = getwikiseps(aminename)
        
        #septemplate = r'''\d+\" style="text-align:center\">\d+</th><td>(\d+)</td>'''
        #temp = wikipedia.page((wikipedia.search("Tangled.the.Series episodes"))[0])#.html()
        #temp = wikipedia.page((wikipedia.search("Sofia.the.First episodes"))[0]).html()
        #aminename = 'Sofia the First'
        #aminename = 'Tangled the Series'
        #aminename = 'Elena of Avalor'
        urlcode = wikipedia.page((wikipedia.search(aminename + ' episodes'))[0]).html()
        
        #<h3><span id="Season_
        #<table class="
        #<th scope="row" id="ep
        #26" style="text-align:center">26</th><td>1</td>
        
        seasoncodes = urlcode.split('<h3><span id=\"Season_')[1:]
        seps = pandas.DataFrame(columns = ['EP', 'STATE'])
        seps.set_index('EP', inplace=True, drop=True)
        for seasoncode in seasoncodes:    
            season = '0' + str(seasoncode[0])
            tablecodes = seasoncode.split('<table class=\"')
            epcodes = tablecodes[1].split('<th scope=\"row\" id=\"ep')[1:] #1st table only
            for epcode in epcodes:
                episode = re.search(septemplate, epcode).group(1)
                if len(episode) < 2:
                    episode = '0' + episode
                pass
                seps.loc['S' + season + 'E' + episode] = {'STATE' : 'NONE'} #1st match only
    #            seps['S' + season + 'E' + episode] = 
#        return seps
        aminestatuses[aminename] = seps
    return aminestatuses
#%% 
def getxlsxseps(filename, index):
    sheets, tabs = fmxlsx(filename, index)   
    statuses = {}
    for tab in tabs:
        statuses[tab] = sheets[tab]
    return statuses
#%%
#def setxlsx(filename, index, sheet, row, value):
#    return updatexlsx(filename, sheets)
#%%
def setxlsxbyaminecode(filename, index, aminecode, status):    
    # Retrieve Ep & Sheet
    ep = aminecode.split('.')[-1]
    aminename = aminecode.replace('.' + ep, '')
    aminename = aminename.replace('.', ' ')
    
    sheets, tabs = fmxlsx(filename, index)    
    sheets[aminename].loc[sheets[aminename].index.isin([ep]), 'STATE'] = status    
    
    return updatexlsx(filename, index, sheets)
#%%
def getaminetasksbyxlsx(filename, index):
    sheets, tabs = fmxlsx(filename, index)
    # Filter out the relevent items from dict            
    aminestatuses = {}
    for aminename in tabs:
        task = sheets[aminename]
        eps = task[(task['STATE'] == 'NONE') | (task['STATE'] == 'LAST')]
#        for Ep in Eps['EP']:              
        for ep in eps.index:              
#            aminestatuses[(aminename.replace(' ', '.') + '.' + Ep)] = task.loc[task['EP'] == Ep, 'STATE'].values[0]
            aminestatuses[(aminename.replace(' ', '.') + '.' + ep)] = task.loc[task.index.isin([ep]), 'STATE'].values[0]
    return aminestatuses
#%%
prev = 'SEED'
def aminebt(filename): 
    global prev
    index = 'EP'
    hostname = 'https://yourbittorrent.com'
    seedtemplate = r'''<a href=\"(/torrent/\d+/[\w.-]+)\">[\w -]+<font color=\#ccc>[\w-]+</font></a></div><div style=float:right><i class=\"fa fa-check\" style=color:green data-toggle=\"tooltip\" title=\"Torrent Verified\"></i></div></td><td class=s>\d+ MB</td><td class=t>\d+/\d+/\d+</td><td class=u>(\d+)</td><td class=d>(\d+)</td></tr>'''
    dltemplate = r'''(/down/\d+.torrent)'''
    
    if prev == 'SEED':
        prev = 'LIST'
        xprint (prev)
        # Update and Merge status from wiki to xlsx
        newstatuses = getwikiseps(filename, index)
        oldstatuses = getxlsxseps(filename, index)
        joinstatusus(filename, index, oldstatuses, newstatuses)
    else:
        prev = 'SEED'
        xprint (prev)
        # Encode status into tasks
        aminestatuses = getaminetasksbyxlsx(filename, index)    
        match = {}
        for aminecode, aminestatus in aminestatuses.items():
            if 'LAST' not in aminestatuses.values():
                urlcode = urlsource(hostname + '/?q=' + aminecode)
                match[aminecode] = re.findall(seedtemplate, urlcode)
                xprint (aminecode, ' : ', len(match[aminecode]))
                if(len(match[aminecode]) > 0):
                    urlcode = urlsource(hostname + match[aminecode][match[aminecode][3].index(max(match[aminecode][3]))][0])        
                    dlurl = hostname + (re.search(dltemplate, urlcode))[1]
                    dltorrent(dlurl)  
                    xprint (aminecode, 'is downloading...')
                    setxlsxbyaminecode(filename, index, aminecode, 'SENT')
                    aminestatuses[aminecode] = 'SENT'
                else:
                    setxlsxbyaminecode(filename, index, aminecode, 'LAST')
                    aminestatuses[aminecode] = 'LAST'
                return aminestatuses
            elif aminestatus == 'LAST':
                setxlsxbyaminecode(filename, index, aminecode, 'NONE')
                aminestatuses[aminecode] = 'NONE'
        return aminestatuses
#%%
#filename = 'amine.xlsx'
##temp1, temp2 = aminebt(filename)
#temp = aminebt(filename)