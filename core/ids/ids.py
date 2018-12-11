import time
import re

class Error(Exception):
    pass

class AlertReader:
    def __init__(self, alert_file_path):

        self.alert_file_path = alert_file_path

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
            else:
                yield line

class AlertParser:
    def __init__(self, generator, server_ip_address):
        self.generator = generator
        self.server_ip_address = server_ip_address
        self.black_dict = {}
    def parse(self):
        look_ahead_re = '(?=\s\-\>\s' + self.server_ip_address + ')'
        for line in self.generator:
            ip = re.search('[0-9]+?.[0-9]+?.[0-9]+?.[0-9]+?'+look_ahead_re, line).group(0)
            priority = re.search('(?<=\[Priority:\s)[0-9]', line).group(0)
            date = re.search('[0-9]+?/[0-9]+?(?=-)', line).group(0)
            time_ = re.search('(?<=-)[0-9]+?:[0-9]+?:[0-9]+?.[0-9]+', line).group(0)
            class_ = re.search('(?<=\[Classification:\s)[^\]]+?(?=\])', line).group(0)
            #if ip != None and priority != None and class_ != None:
            #    print(ip.group(0), priority.group(0), class_.group(0))
            if not ip in self.black_dict:
                self.black_dict[ip] = [{'attempt':class_, 'priority':priority, 'date':date, 'time':time_}]
            else:
                self.black_dict[ip].append({'attempt':class_, 'priority':priority, 'date':date, 'time':time_})

            #print(self.black_dict)
        #print(black_dict)

al = AlertReader("/var/log/snort/alert")
an = AlertParser(al.tail_f(), "239.255.255.250")
#al = AlertReader("/home/boeing/Desktop/alert", "239.255.255.250")
#lookahead = '(?=\s\-\>\s'+"239.255.255.250)"
an.parse()

