import requests
import time
import sys
import datetime
import sqlite3
import hashlib
import sched
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class website:
    def __init__(self, url, lastHash, lastUpdate):
        self.url = url
        self.hash = lastHash
        self.lastUpdate = lastUpdate
    def __eq__(self, other):
        return self.url == other.url
    def fetch(self):
        try:
            self.con = sqlite3.connect(r"./database.db")
        except:
            print()
            print("[WA] Error creating database file, make sure you have the right permissions and create a dev/changeWebsiteAlerts folder")
            print()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options= managerObject.chrome_options)
        time.sleep(0.5)
        driver.get("about:blank")
        driver.delete_all_cookies()
        time.sleep(0.5)
        driver.get(self.url)
        time.sleep(4)
        try:
            text = driver.find_element(by = By.TAG_NAME, value = 'body')
        except:
            pass
        newHash = hashlib.sha256(text.text.encode('utf-8')).hexdigest()
        if self.hash != newHash and self.hash != None and self.hash != "Never monitored":
            #Change detected.
            self.alert()
        self.hash = newHash
        self.lastUpdate = str(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        self.updateDb()
        driver.quit()

    def alert(self):
        url = 'https://api.pushover.net/1/messages.json'
        title = '[WA] Detected website change'
        myobj = {'token': managerObject.apiToken, 'user': managerObject.userToken, 'title': title,
                 'message': 'Website: '+str(self.url)+' has got 1 new change'}
        requests.post(url, data=myobj)

    def updateDb(self):
        query = 'UPDATE websiteData SET hash = ?, lastUpdate = ? WHERE url = ?'
        queryTuple = (self.hash, self.lastUpdate, self.url)
        cursor = self.con.cursor()
        cursor.execute(query, queryTuple)
        self.con.commit()

class manager:
    def __init__(self):
        self.queue = []
        self.freq = 600 #10 mins by default, unless updated
        self.userToken = ""
        self.apiToken = ""
        self.chrome_options = Options()
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--remote-debugging-port=9222")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.headless = True

        try:
            self.con = sqlite3.connect(r"C:\Users\pro\OneDrive\Dev\changeWebsiteAlerts\dev\database.db")
        except:
            print()
            print("[WA] Error creating database file, make sure you have the right permissions and create a dev/changeWebsiteAlerts folder")
            print()
        self.c = self.con.cursor()

        self.checkSettings()

    def checkSettings(self):
        # settings Table
        query = """CREATE TABLE IF NOT EXISTS settings (
        name TEXT NOT NULL,
        value TEXT,
        UNIQUE(name)
        )"""
        self.c.execute(query.replace('\n', ' '))

        insertFreq = 'INSERT OR IGNORE INTO settings(name, value) VALUES(?,?)'
        tupleFreq = ('frequency', str(self.freq))
        self.c.execute(insertFreq, tupleFreq)
        
        pushover_user = 'INSERT OR IGNORE INTO settings(name, value) VALUES(?,?)'
        tuplePushover_user = ('pushover_user', str(self.userToken))
        self.c.execute(pushover_user, tuplePushover_user)
        pushover_api = 'INSERT OR IGNORE INTO settings(name, value) VALUES(?,?)'
        tuplePushover_api = ('pushover_api', str(self.apiToken))
        self.c.execute(pushover_user, tuplePushover_user)
        self.c.execute(pushover_api, tuplePushover_api)

        self.con.commit()
        query = 'SELECT * FROM settings'
        self.c.execute(query)
        rows = self.c.fetchall()
        for settingRow in rows:
            if(settingRow[0] == "frequency"):
                self.freq = int(settingRow[1])
            elif(settingRow[0] == "pushover_user"):
                self.userToken = settingRow[1]
            elif (settingRow[0] == "pushover_api"):
                self.apiToken = settingRow[1]
    def fetchDatabase(self):
        # websiteData table
        query = """CREATE TABLE IF NOT EXISTS websiteData (
        url TEXT NOT NULL,
        hash TEXT,
        lastUpdate TEXT,
        PRIMARY KEY(url)
        )"""
        self.c.execute(query.replace('\n', ' '))
        self.con.commit()

        query = 'SELECT * FROM websiteData'
        self.c.execute(query)
        rows = self.c.fetchall()
        #Look for duplicates in the queue            
        for webRow in rows:
            if(webRow[0] != None):
                web = website(webRow[0], webRow[1], webRow[2])
                if(web not in self.queue):
                    self.queue.append(web)

        self.checkSettings()

    def check(self):
        self.fetchDatabase()
        #Current queue objects
        print("[WA] Checking websites")
        print("Current queue length:"+str(len(self.queue)))
        print("---------------------------------")
        for web in self.queue:
            try:
                print("Monitoring started for "+str(web.url))
                web.fetch()
            except Exception as e: 
                print(e)
                print("Error accessing website: "+str(web.url))
                pass
        print("[WA] Finished checking queue")
        self.s.enter(self.freq, 1, self.check, ())
    def start(self):
        self.s = sched.scheduler(time.time, time.sleep)
        self.s.enter(self.freq, 1, self.check, ())
        self.s.run()
        print("[WA] Next check in "+str(self.freq)+" seconds")

    def setFrequency(self, seconds):
        self.fetchDatabase()
        self.freq = seconds
        query = 'UPDATE settings SET value = ? WHERE name = ?'
        queryTuple = (str(self.freq), 'frequency')
        self.c.execute(query, queryTuple)
        self.con.commit()
        print("[WA] Successfully set frequency at "+str(self.freq)+" seconds")

    def setPushoverAuth(self, userToken, apiToken ):
        self.fetchDatabase()
        self.userToken = userToken
        self.apiToken = apiToken
        query = 'UPDATE settings SET value = ? WHERE name = ?'
        queryTuple = (self.userToken, 'pushover_user')
        query2 = 'UPDATE settings SET value = ? WHERE name = ?'
        queryTuple2 = (self.apiToken, 'pushover_api')
        self.c.execute(query, queryTuple)
        self.c.execute(query2, queryTuple2)
        self.con.commit()
        print("[WA] Successfully set Pushover auth")
        

    def addWebsite(self, url):
        self.fetchDatabase()
        #Parse URL into HTTPS format
        if not url.startswith("https://") and not url.startswith("http://"):
            url = "https://"+url
        try:
            query = "INSERT INTO websiteData(url, hash, lastUpdate) VALUES(?,?,?)"
            tupleWebsite = (url, "Never monitored", "Never monitored")
            self.c.execute(query, tupleWebsite)
            self.con.commit()
            print("[WA] Successfully added website: "+str(url))
        except:
            print("[WA] Error adding website url: "+str(url))
    def removeWebsite(self, url):
        self.fetchDatabase()
        if not url.startswith("https://") and not url.startswith("http://"):
            url = "https://"+url
        try:
            query = "DELETE FROM websiteData WHERE url = '"+str(url)+"'"
            self.c.execute(query)
            self.con.commit()
            print("[WA] Successfully removed website: "+str(url))
        except Exception as e: 
            print(e)
            print("[WA] Error removing website url: "+str(url))

def printHelp():
    print("####### Website Alerts #######")
    print("-------------------------------------")
    print("Available commands:")
    print("start                  Starts to monitor websites for new changes")
    print("frequency <mins>     Change the frequency interval in which it looks for changes")
    print("pushover <user> <api>  Sets the pushover user token & the api token to send alerts with")
    print("add <url_name>         Adds a new website to monitor")
    print("remove <url_name>      Remove an existing website from the queue")
    print("list                   Lists active websites which are being monitored")
    print("help                   Prints this help dialog")
    print("-------------------------------------")


global managerObject
managerObject = manager()

if (len(sys.argv) == 1):
    printHelp()
elif (sys.argv[1] == "help"):
    printHelp()
elif(sys.argv[1] == "start"):
    managerObject.start()
elif (sys.argv[1] == "pushover"):
    if (len(sys.argv) == 2):
        print("[WA] Too few arguments. Provide the user token and the token api.")
        print("USAGE: pushover <user> <api>  Sets the pushover user token & the api token to send alerts with")
    elif(len(sys.argv) == 4):
        managerObject.setPushoverAuth(sys.argv[2], sys.argv[3])
elif (sys.argv[1] == "frequency"):
    if (len(sys.argv) == 2):
        print("[WA] Too few arguments. Provide the desired frequency in minutes (example: 10m).")
        print("USAGE: frequency <m>  Change the frequency interval in which it looks for changes, it must be greater than 1 minute")
    elif (len(sys.argv) == 3):
        seconds = 60 * int(''.join(filter(str.isdigit, sys.argv[2])))
        managerObject.setFrequency(seconds)
    else:
        print("[WA] Too many arguments. Provide the desired frequency in minutes (example: 10).")
        print("USAGE: frequency <m>  Change the frequency interval in which it looks for changes")
elif (sys.argv[1] == "list"):
    print("[WA] Generating list of websites which are currently being monitored...")
    print()
    print("---------------------")
    print("Active websites:")
    query = 'SELECT * FROM websiteData'
    managerObject.c.execute(query)
    rows = managerObject.c.fetchall()
    for row in rows:
        if(row[0] != None):
            print("URL: "+str(row[0]))
            print("Hash: "+str(row[1]))
            print("Last update: "+str(row[2]))
            print("---------------------")
elif (sys.argv[1] == "add"):
    if (len(sys.argv) == 2):
        print("[WA] Too few arguments. Provide the url to monitor.")
        print("USAGE: add <url_name>  Adds a new website to monitor")
    elif (len(sys.argv) == 3):
        managerObject.addWebsite(sys.argv[2])
    else:
        print("[WA] Too many arguments. Provide the url to monitor.")
        print("USAGE: add <url_name>  Adds a new website to monitor")
elif (sys.argv[1] == "remove"):
    if (len(sys.argv) == 2):
        print("[WA] Too few arguments. Provide the url to remove.")
        print("USAGE: remove <url_name>  Removes an existing website from the queue")
    elif (len(sys.argv) == 3):
        managerObject.removeWebsite(sys.argv[2])
    else:
        print("[WA] Too many arguments. Provide the url to remove.")
        print("USAGE: remove <url_name>  Removes an existing website from the queue")
else:
    print("[WA] Unknown command.")
    print()
    printHelp()
