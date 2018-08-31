# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 09:29:39 2018

@author: SF
https://global.download.synology.com/download/Document/DeveloperGuide/Synology_Download_Station_Web_API.pdf

nas.application.service.request(method, [params])

video/TEMPERORY
"""
#%%
import sys
from utility import *
from aminebt import *
from radiodl import *
#%%
filename = 'amine.xlsx'
#%% 
def initHome(args):
    HomeProcesses = {}
    HomeProcesses['aminebt'] = HomeProcess(aminebt, datetime.time(00, 00, 00), 1800, filename)
    HomeProcesses['radiodl'] = HomeProcess(radiodl, datetime.time(10, 00, 00), 3600 * 12, args[1])
#    HomeProcesses['radiodl'] = HomeProcess(radiodl, 60, args[1])
    return HomeProcesses
#%%
def startHome(HomeProcesses):
    for key, func in HomeProcesses.items():
        func.start()
    return HomeProcesses
#%%
def stopHome(HomeProcesses):
    for key, func in HomeProcesses.items():
        func.stop()
    return HomeProcesses
#%%
def main():
    HomeProcesses = initHome(sys.argv)    
    while True:
        command = input()
        if command == 'killall':
            HomeProcesses = stopHome(HomeProcesses)
        elif command == 'runall':
            HomeProcesses = startHome(HomeProcesses)
        elif command == 'bye' or command == 'exit':
            HomeProcesses = stopHome(HomeProcesses)
            return 0
    
#%%
if __name__ == '__main__':
  main()
#xlsx = main()
#%%
#import pygsheets
#
#gc = pygsheets.authorize()
#
## Open spreadsheet and then workseet
#sh = gc.open('my new ssheet')
#wks = sh.sheet1
#
## Update a cell with value (just to let him know values is updated ;) )
#wks.update_cell('A1', "Hey yank this numpy array")
#
## update the sheet with array
#wks.update_cells('A2', my_nparray.to_list())
#
## share the sheet with your friend
#sh.share("myFriend@gmail.com")