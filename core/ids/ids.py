#!/usr/bin/python
import time
import re
import json
import os
import sys
import subprocess
from subprocess import Popen, PIPE

class Error(Exception):
    pass

class AlertParser:
    def __init__(self, config):
        #self.generator = generator
        self.server_ip_address = config['server_ip_address']
        self.black_list_file_path = config['black_list_file_path']
        self.alert_file_path = config['alert_file_path']
        self.black_dict = {}
        self.dump_time = time.time()
        self.dump_interval = 15

    def tail_f(self):
        interval = 1.0
        try:
            file = open(self.alert_file_path)
        except Exception:
            raise Error('Alert file does not exist')
        while True:
            where = file.tell()
            line = file.readline()
            if not line:
                time.sleep(interval)
                file.seek(where)
                yield "stuck"
            else:
                yield line

    def empty_black_list(self):
        self.black_dict = {}
        open(self.black_list_file_path, 'w').close()

    def load_dump(self):

        try:
            black_list_file = open(self.black_list_file_path, "r")
        except Exception:
            raise Error('Black list file does not exist')

        try:
            dump_dict = json.load(black_list_file)
        except Exception:
            raise Error('Json structure corrupt')
        black_list_file.close()
        return dump_dict

    def start(self):
        p = Popen(["sudo", "snort", "-A", "fast", "-c", "/etc/snort/snort.conf", "-q"], stdout=PIPE)
        #print(p.communicate())

        if not os.path.isfile(self.black_list_file_path):
            open(self.black_list_file_path, 'w').close()
        if os.stat(self.black_list_file_path).st_size != 0:
            self.black_dict = self.load_dump()

        #open(self.alert_file_path, 'w').close()

        look_ahead_re = '(?=:[0-9]+?\s\-\>\s' + self.server_ip_address + ')'
        for line in self.tail_f():
            #print(line)
            if line != 'stuck':
                ip = re.search('[0-9]+?\.[0-9]+?\.[0-9]+?\.[0-9]+?'+look_ahead_re, line)
                priority = re.search('(?<=\[Priority:\s)[0-9]', line)
                date = re.search('[0-9]+?/[0-9]+?(?=-)', line)
                time_ = re.search('(?<=-)[0-9]+?:[0-9]+?:[0-9]+?.[0-9]+', line)
                class_ = re.search('(?<=\[Classification:\s)[^\]]+?(?=\])', line)

                if ip != None and priority != None and class_ != None and date != None and time_ != None:
                    if not ip.group(0) in self.black_dict:
                        self.black_dict[ip.group(0)] = [{'attempt':class_.group(0), 'priority':priority.group(0),
                                                'date':date.group(0), 'time':time_.group(0)}]
                        #print(ip.group(0))
                    else:
                        if {'attempt':class_.group(0), 'priority':priority.group(0),
                                                    'date':date.group(0), 'time':time_.group(0)} not in self.black_dict[ip.group(0)]:
                            self.black_dict[ip.group(0)].append({'attempt':class_.group(0), 'priority':priority.group(0),
                                                        'date':date.group(0), 'time':time_.group(0)})
                            #print(ip.group(0))
                        #else:
                            #print("there")

            if time.time() - self.dump_time >= self.dump_interval and len(self.black_dict) > 0:
                #check if dump has to be rewritten:
                dumped_black_list = {}
                if os.stat(self.black_list_file_path).st_size != 0:
                    dumped_black_list = self.load_dump()

                #if has:
                if dumped_black_list != self.black_dict:
                    json_dump = json.dumps(self.black_dict)
                    try:
                        black_list_file = open(self.black_list_file_path, "w")
                    except Exception:
                        raise Error('Black list file does not exist')
                    black_list_file.write(json_dump)
                    black_list_file.close()
                    self.dump_time = time.time()
                #else:
                    #print('same!')
#from core.common import load_config

#config = load_config('/home/boeing/bicycle/config/ids.json')
#AlertParser(config).start()