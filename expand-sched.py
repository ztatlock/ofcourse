#!/usr/bin/env python

import json
from datetime import datetime, timedelta
import pytz

class Event(object):
    def __init__(self, catg, date, topic, numS = None, defaults = None):
        self.catg = catg

        if numS == None or numS == '--':
            self.topic = topic
            self.url   = ''
        else:
            self.topic = numS + ' ' + topic
            self.url   = catg + numS + '/'

        if defaults != None and 'room' in defaults:
            self.room = defaults['room']
        else:
            self.room = 'UW Seattle'

        if defaults != None and 'time' in defaults:
            time = datetime.strptime(defaults['time'], '%H:%M')
            self.start = \
              datetime( date.year
                      , date.month
                      , date.day
                      , time.hour
                      , time.minute
                      , 0
                      , 0
                      , tzinfo=pytz.timezone('America/Los_Angeles')
                      )
            if 'length' in defaults:
                mins = int(defaults['length'])
                self.end = self.start + timedelta(0, mins * 60)
            else:
                self.end = self.start
        else:
            # a date without time indicates whole day event
            self.start = date
            self.end  = date + timedelta(1, 0)

    def __str__(self):
        kvs = "\n, ".join([ '"catg"  : "%s"' % self.catg
                          , '"topic" : "%s"' % self.topic
                          , '"url"   : "%s"' % self.url
                          , '"room"  : "%s"' % self.room
                          , '"start" : "%s"' % self.start.strftime("%Y-%m-%d %H:%M")
                          , '"end"   : "%s"' % self.end.strftime("%Y-%m-%d %H:%M")
                          ])
        return "{ %s\n}" % kvs

def hasRepTopics(desc):
    return 'first'  in desc \
       and 'repeat' in desc \
       and 'topics' in desc

def expandRepTopics(catg, desc):
    events = []
    num = 0
    date = datetime.strptime(desc['first'], '%Y-%m-%d')
    for topic in desc['topics']:
        if topic.startswith("--"):
            numS = "--"
        else:
            num += 1
            numS = "%02d" % num
        events.append(Event(catg, date, topic, numS, desc))

        # get next date
        date = date + timedelta(1, 0)
        while not date.strftime("%a") in desc['repeat'] \
          and not date.strftime("%a") == desc['repeat'] :
            date = date + timedelta(1, 0)
    return events

def expandEventList(catg, desc):
    events = []
    num = 0
    for e in desc:
        date = datetime.strptime(e['date'], '%Y-%m-%d')
        topic = e['topic']
        num += 1
        numS = "%02d" % num
        events.append(Event(catg, date, topic, numS, e))
    return events

def expand(catg, desc):
    if hasRepTopics(desc):
        return expandRepTopics(catg, desc)
    else:
        return expandEventList(catg, desc)

def main():
    with open('sched.json') as f:
        sched = json.load(f)

    events = []
    for k in sched:
        events.extend(expand(k, sched[k]))

    for e in events:
        print e

main()
