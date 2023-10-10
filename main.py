from time import sleep
from pandas import DataFrame
from datetime import datetime
import requests
import urllib3
import re

lineApiUrl = 'https://notify-api.line.me/api/notify'
lineApiToken = 'you line api token here.'
lineApiHeaders = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Bearer ' + lineApiToken
}

serverStatusUrl = 'https://stathub.nso.go.th/server-status?auto'

reportDirectory = './stathub_linenotify_reports/'

def sendLineNotification(connsTotal):
    try:
        message = urllib3.parse.urlencode({ 'message': 'Stathub พบการใช้งานผิดปกติ: ' + connsTotal })
        response = requests.post(url = lineApiUrl, headers = lineApiHeaders, data = message)
        print(response.text)
    except Exception as ex:
        print(ex)

def writeToFile(connsTotal, idleWorkers, busyWorkers):
    fileName = reportDirectory + datetime.now().strftime('%Y-%B-%d') + '.csv'
    with open(fileName, 'a') as file:
        df = DataFrame({'ConnsTotal': connsTotal, 'IdleWorkers': idleWorkers, 'BusyWorkers': busyWorkers}, index = [datetime.now().strftime('%I:%M %p')])
        df.to_csv(file, mode = 'a', header = file.tell() == 0)
        file.flush()
        file.close()

def fetchServerStatus(connsThreshold = 100):
    try:
        response = requests.get(url = serverStatusUrl)
        connsTotal = 0
        idleWorkers = 0
        busyWorkers = 0
        for line in response.text.splitlines():
            rConnsTotal = re.search('ConnsTotal: ([0-9]+)', line)
            if rConnsTotal is not None:
                connsTotal = int(rConnsTotal.group(1))

            rIdleWorkers = re.search('IdleWorkers: ([0-9]+)', line)
            if rIdleWorkers is not None:
                idleWorkers = int(rIdleWorkers.group(1))

            rBusyWorkers = re.search('BusyWorkers: ([0-9]+)', line)
            if rBusyWorkers is not None:
                busyWorkers = int(rBusyWorkers.group(1))

        print('ConnsTotal: ', connsTotal, 'IdleWorkers: ', idleWorkers, 'BusyWorkers: ', busyWorkers)
        writeToFile(connsTotal, idleWorkers, busyWorkers)
        if connsTotal >= connsThreshold:
            sendLineNotification(connsTotal)
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    while True:
        fetchServerStatus(connsThreshold = 20)
        
        # Sleep for 15 minutes
        sleep(15*60)
