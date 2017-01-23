#!/usr/bin/env python

import json
import pytz
from datetime import datetime, timedelta

class Event(object):
    def __init__(self, catg, date, num, topic, defaults = None):
        self.catg = catg

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
                # a time without length indicates a deadline
                self.end = self.start
        else:
            # a date without time indicates whole day event
            self.start = date
            self.end = date + timedelta(1, 0)

        if num == -1:
            self.topic = topic
            self.url = ''
        else:
            numS = "%02d" % num
            self.topic = numS + ' ' + topic
            self.url = catg + numS + '/'

        if defaults != None and 'room' in defaults:
            self.room = defaults['room']
        else:
            self.room = 'UW Seattle'

    def __str__(self):
        kvs = "\n, ".join([ '"catg"  : "%s"' % self.catg
                          , '"start" : "%s"' % self.start.strftime("%Y-%m-%d %H:%M")
                          , '"end"   : "%s"' % self.end.strftime("%Y-%m-%d %H:%M")
                          , '"topic" : "%s"' % self.topic
                          , '"url"   : "%s"' % self.url
                          , '"room"  : "%s"' % self.room
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
            events.append(Event(catg, date, -1, topic, desc))
        else:
            num += 1
            events.append(Event(catg, date, num, topic, desc))

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
        if topic.startswith("--"):
            events.append(Event(catg, date, -1, topic, e))
        else:
            num += 1
            events.append(Event(catg, date, num, topic, e))
    return events

def main():
    with open('sched.json') as f:
        sched = json.load(f)

    events = []
    for k in sched:
        if hasRepTopics(sched[k]):
            es = expandRepTopics(k, sched[k])
        else:
            es = expandEventList(k, sched[k])
        events.extend(es)

    with open('sched-expanded.json', 'w') as f:
        js = '\n,\n'.join([str(e) for e in events])
        f.write('{ "sched" : [\n%s\n]}' % js)

main()
