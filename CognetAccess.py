from pymarc import *
import csv
import os
import urllib
from urllib import request
from urllib import error
import tkinter

root = tkinter.Tk()
root.withdraw()

def writeToLog(recID,url,urlResult):
    """writes a result list to a log file"""
    resultsFile = 'CogNet_Access_Checks_Result.csv'

    import time
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    data = [[now, str(recID), str(url), str(urlResult)]]

    try:
        with open(resultsFile, 'a', newline='') as out:
            a = csv.writer(out, delimiter=',', quoting=csv.QUOTE_ALL)
            a.writerows(data)
    except UnicodeEncodeError:
        print("failed to write "+str(recID))


def checkURL(recID, urlList, debug):

    if debug == '1':
        print('testing record ID: '+str(recID))

    urlResult = True
    for url in urlList:
        if debug == '1':
            print('\ttesting URL: '+str(url))

        urlResult = True
        try:
            r = urllib.request.urlopen(url)
            rcode = r.code
            if rcode != 200:
                urlResult = False
                if debug == '1':
                    print ('\tpage returned an error!')

            rBinary = r.readall()

            #this phrase custom for FAU - input whatever your page says
            if 'Access provided by: <a href="">Florida Atlantic University' not in rBinary.decode():
                urlResult = False
                if debug == '1':
                    print('\tAccess note not found!')

        except urllib.error.HTTPError:
            urlResult = False
            if debug == '1':
                print('\tWe do not have access to this page!')
        except UnicodeEncodeError:
            urlResult = False
            if debug == '1':
                print('\tThis URL is weird and not working!')
                url = 'Cannot write'


        writeToLog(recID, url, urlResult)

    if debug == '1':
        print('\tTest result is '+str(urlResult))
        keepGoing = input("continue?\n")
        if keepGoing == 'n':
            x = 1/0


def getURLs():
    print('running checks for MIT CogNet...\n')
    debug = input("would you like to run in debug mode? Type '1'\n")
    debug = str(debug)

    print("great!")
    marcFile = 'Z:\\GenLoad\\MIT CogNet\\Maintenance\\CogNet_complete_010616.mrc'
    useMarc = input("press '1' to choose a MARC File, otherwise, I'll just use the default...\n")
    useMarc = str (useMarc)

    if useMarc == '1':
        from tkinter import filedialog
        marcPath = tkinter.filedialog.askopenfile()
        marcFile = marcPath.name

    print("okay! running...")

    with open(marcFile, 'rb') as fh:
        reader = MARCReader(fh, to_unicode=True, force_utf8=True)

        for record in reader:
            record.force_utf8 = True

            recID = record['001'].value()

            # # testing a special case with multiple URLs
            # if int(recID) >= 120080 and int(recID) < 120081:
            #     pass
            # else:
            #     continue

            urlList1 = record.get_fields('856')
            if len(urlList1) == 0:
                print('recID: '+str(recID)+' has no URLs!')
                if debug == '1':
                    keepGoing = input("continue?\n")
                    if keepGoing == 'n':
                        x = 1 / 0
            urlList2 = []

            for url in urlList1:
                urlList2.append(url['u'])

            # return urlList2

            #check the found URLs and write to log
            checkURL(recID, urlList2, debug)

    print('...done')
    input('press any key to launch the log file')
    os.system("start " + 'CogNet_Access_Checks_Result.csv')

getURLs()



