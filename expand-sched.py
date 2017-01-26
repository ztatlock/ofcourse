#!/usr/bin/env python

import json
import pytz
import copy
from datetime import datetime, timedelta

TZ = pytz.timezone('America/Los_Angeles')
ROOM = 'UW Seattle'

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
                      , tzinfo = TZ
                      )
            if 'length' in defaults:
                mins = int(defaults['length'])
                self.end = self.start + timedelta(0, mins * 60)
            else:
                # a time without length indicates a deadline
                self.end = self.start
        else:
            # a date without time indicates whole day event
            # construct date explicitly to include timezone
            self.start = \
              datetime( date.year
                      , date.month
                      , date.day
                      , 0
                      , 0
                      , 0
                      , 0
                      , tzinfo = TZ
                      )

            self.end = date + timedelta(1, 0)

        if num == -1:
            self.topic = topic
            self.url = ''
        else:
            self.topic = '%02d %s' % (num, topic)
            self.url = '%s%02d/' % (catg, num)

        if defaults != None and 'room' in defaults:
            self.room = defaults['room']
        else:
            self.room = ROOM

    def __str__(self):
        kvs = "\n, ".join([ '"catg"  : "%s"' % self.catg
                          , '"start" : "%s"' % self.start.isoformat()
                          , '"end"   : "%s"' % self.end.isoformat()
                          , '"topic" : "%s"' % self.topic
                          , '"url"   : "%s"' % self.url
                          , '"room"  : "%s"' % self.room
                          ])
        return "{ %s\n}" % kvs

def hasRepTopics(desc):
    return 'first'  in desc \
       and 'repeat' in desc \
       and 'topics' in desc

def repeatTopics(desc):
    es = []
    date = datetime.strptime(desc['first'], '%Y-%m-%d')
    for topic in desc['topics']:
        e = copy.deepcopy(desc)
        e['topic'] = topic
        e['date'] = date.strftime('%Y-%m-%d')
        es.append(e)

        # get next date
        date = date + timedelta(1, 0)
        while not date.strftime("%a") in desc['repeat'] \
          and not date.strftime("%a") == desc['repeat'] :
            date = date + timedelta(1, 0)
    return es

def expandEvents(catg, desc):
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
        es = sched[k]
        if hasRepTopics(es):
            es = repeatTopics(es)
        es = expandEvents(k, es)
        events.extend(es)

    with open('sched-expanded.json', 'w') as f:
        eobjs = '\n,\n'.join([str(e) for e in events])
        f.write('{ "events" : [\n%s\n]}' % eobjs)

main()
