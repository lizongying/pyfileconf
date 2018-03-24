#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import logging
import os
import socket
import sys
import threading
import xmlrpclib

from apscheduler.schedulers.blocking import BlockingScheduler
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_CREATE, IN_MODIFY, NotifierError

logger = logging.getLogger()
handler = logging.FileHandler('/var/log/pyfileconf/pyfileconf.log', mode='a', encoding=None, delay=False)
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

myname = socket.getfqdn(socket.gethostname())
myaddr = socket.gethostbyname(myname)


class EventHandler(ProcessEvent):
    @staticmethod
    def do_client(obj):
        for addr in obj['servers'].keys():
            if obj['is_client']:
                if addr != myaddr:
                    continue
                server_addr = 'localhost'
            else:
                server_addr = addr
            server = xmlrpclib.Server(
                'http://%s%s:%d/RPC2' % (obj['supervisor_authorize'], server_addr, obj['supervisor_port']))
            info = server.supervisor.getAllProcessInfo()
            jobs = {}
            for i in info:
                jobs[i['group']] = i['statename']
            if 'supervisor' in obj['servers'][addr]:
                for i in obj['servers'][addr]['supervisor'].keys():
                    if i not in jobs:
                        continue
                    status_now = jobs[i]
                    res = ''
                    if obj['servers'][addr]['supervisor'][i] == 'run':
                        if status_now == 'RUNNING':
                            pass
                        else:
                            res = server.supervisor.startProcessGroup(i)
                    elif obj['servers'][addr]['supervisor'][i] == 'stop':
                        if status_now == 'RUNNING':
                            res = server.supervisor.stopProcessGroup(i)
                        else:
                            pass
                    else:
                        pass
                    print i, res

    def do_work(self, event):
        if event and event.pathname != conf_path:
            return
        with open(conf_path) as f:
            try:
                obj = json.loads(f.read())
                self.do_client(obj)
            except:
                pass

    def process_IN_MODIFY(self, event):
        self.do_work(event)

    def process_IN_CREATE(self, event):
        self.do_work(event)


def interval_check():
    scheduler = BlockingScheduler()
    scheduler.add_job(EventHandler().do_work, 'interval', minutes=10, args=[''])
    scheduler.start()


def change_check():
    wm = WatchManager()
    mask = IN_CREATE | IN_MODIFY
    notifier = Notifier(wm, EventHandler())
    wm.add_watch(conf_dir, mask, rec=True)
    try:
        notifier.loop()
    except NotifierError, err:
        print err


def file_conf():
    t1 = threading.Thread(target=interval_check)
    t2 = threading.Thread(target=change_check)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print 'no config file'
        exit()
    conf_path = sys.argv[1]
    if not os.path.isfile(conf_path):
        print 'no config file'
        exit()

    conf_dir = os.path.dirname(conf_path)
    file_conf()
