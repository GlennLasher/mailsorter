#!/usr/bin/python

import sqlite3
import imaplib
import time
import os

class NoDatabase(Exception):
    pass

class Log:
    def __init__(self, dbi):
        self.dbi = dbi

    def addentry(self, logtext, account_id = None, rule_id = None):
        cursor = self.dbi.cursor()
        cursor.execute ("INSERT INTO log (logtime, account_id, rule_id, logtext) values (?, ?, ?, ?)", (time.time(), account_id, rule_id, logtext))
        self.dbi.commit()

class Rule:
    def __init__(self, ruleid = None, accountid = None, priority = 10,
                 field = None, searchstring = None, destination = None, 
                 M = None, logger = None):
        self.id = ruleid
        self.accountid = accountid
        self.priority = priority
        self.field = field
        self.searchstring = searchstring
        self.destination = destination
        self.M = M
        self.logger = logger

    def execute(self):
        #Logs were too verbose.
        #TODO: Make this configurable
        #self.logger.addentry ("Applying rule: if %s contains %s, move to %s." %
        #                      (self.field, self.searchstring, self.destination), 
        #                      account_id = self.accountid, rule_id = self.id)
        status, detail = self.M.select ("Inbox")
        status, result = self.M.search (None, self.field, self.searchstring)
        for msgid in result[0].split():
            status, detail = self.M.copy(msgid, self.destination)
            if (status == 'OK'):
                self.M.store(msgid, '+FLAGS', '\\Deleted')
            self.logger.addentry("Moving message %s to %s." % (msgid, self.destination),
                                 account_id = self.accountid, rule_id = self.ruleid)
        self.M.expunge()

class Account:
    def __init__(self, conid = None, host = None, port = None, 
                 contype = None, username = None, password = None, dbi = None,
                 logger = None):
        self.id = conid
        self.host = host
        self.port = port
        self.type = type
        self.username = username
        self.password = password
        self.dbi = dbi
        self.M = None
        self.logger = logger
    
    def connect(self):
        if (self.type == "ssl"):
            if (self.port is None):
                self.M = imaplib.IMAP4_SSL(self.host)
                self.logger.addentry ("Securely connected to %s." % (self.host), 
                                      account_id = self.id)
            else:
                self.M = imaplib.IMAP4_SSL(self.host, self.port)
                self.logger.addentry ("Securely connected to %s on port %s." % 
                                      (self.host, self.port), account_id = self.id)
        else:
            if (self.port is None):
                self.M = imaplib.IMAP4(self.host)
                self.logger.addentry ("Connected to %s." % (self.host), 
                                      account_id = self.id)
            else:
                self.M = imaplib.IMAP4(self.host, self.port)
                self.logger.addentry ("Connected to %s on port %s." % 
                                      (self.host, self.port), account_id = self.id)
        
        status, detail = self.M.login(self.username, self.password)
        if (status == "OK"):
            self.logger.addentry ("Logged in as %s." % (self.username), 
                                  account_id = self.id)
        else:
            self.logger.addentry ("Login as %s failed." % (self.username), 
                                  account_id = self.id)
        self.logger.addentry("Login result: {0} {1}".format(status, detail), 
	                     account_id = self.id)
        return status, detail

    def disconnect(self):
        self.logger.addentry ("Logging out of %s on %s." %(self.username, self.host), 
                         account_id = self.id)
        self.M.logout()

    def getrules(self):
        cursor = self.dbi.cursor()
        cursor.execute ("SELECT id, priority, field, searchstring, destination FROM rule WHERE account_id = ? ORDER BY priority", (self.id,))
        for result in cursor:
            (ruleid, priority, field, searchstring, destination) = result
            yield Rule(ruleid, self.id, priority, field, searchstring, 
                       destination, self.M, self.logger) 
    
    def processrules(self):
        self.connect()
        self.logger.addentry("Processing rules for %s on %s." % 
                             (self.username, self.host), account_id = self.id)
        for rule in self.getrules():
            rule.execute()
        self.disconnect()

class Mailsort:
    def __init__(self, db = None):
        self.db = db

        self.dbi = None

        if (db is not None):
            self.dbi = sqlite3.connect(db)

        if (self.dbi is not None):
            self.logger = Log(self.dbi)
        else:
            self.logger = None

    def getaccounts(self):
        if (self.dbi is None):
            raise NoDatabase()
        
        cursor = self.dbi.cursor()
        cursor.execute("SELECT id, host, port, type, username, password from account", 
                       [])
        for result in cursor:
            (conid, host, port, contype, username, password) = result
            yield Account(conid, host, port, contype, username, password, self.dbi, self.logger)

    def run(self):
        self.logger.addentry("Starting Mailsort loop.")
        for account in self.getaccounts():
            account.processrules()
        self.logger.addentry("Ending Mailsort loop.")

def main():
    sorter = Mailsort(os.path.join(os.path.expanduser("~"), ".mailsort", 'mailsort.db'))
    sorter.run()

if (__name__ == "__main__"):
    main()

