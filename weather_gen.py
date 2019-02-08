import requests
from html.parser import HTMLParser
import re
from tabulate import tabulate

def parse_float(text):
    try:
        float(text)
        return True
    except:
        return False

def parse_date(text):
    return re.fullmatch('\d\d/\d\d/\d\d\d\d', text)

def parse_time(text):
    return re.fullmatch('\d\d:\d\d', text)

def parse_crap(text):
    return re.fullmatch('([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?/\d{1,2}h){1,2}', text)

def parse_filler(text):
    return re.fullmatch('-+', text)

def parse_link(text):
    return re.fullmatch('/cgi-bin/decomet\?ind=\d\d\d\d\d&ano=\d\d\d\d&mes=\d\d&day=\d\d&hora=\d\d&min=\d\d&single=yes&lang=en', text)

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.td_found = False
        self.crap_found = False
        self.table = []
        self.curr_row = []
        self.headers = []
        self.headers_found = False
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self.td_found = True
        if tag == 'a':
            a = dict(attrs)
            ref = a['href']
            if parse_link(ref):
                self.links.append(ref)

    def handle_endtag(self, tag):
        if tag == "td":
            self.td_found = False

    def handle_data(self, data):
        if self.td_found and (parse_float(data) or parse_date(data) or parse_time(data) or parse_crap(data) or parse_filler(data)):
            if data == 'Date':
                self.headers_found = True
                self.headers.append(data)

            if parse_date(data):
                if self.curr_row:
                    self.table.append(self.curr_row)
                self.curr_row = [data]
            elif not self.curr_row:
                pass
            else:
                if parse_crap(data):
                    if self.crap_found:
                        self.curr_row[-1] += '\n' + data
                        self.crap_found = False
                    else:
                        self.crap_found = True
                        self.curr_row.append(data)
                else:
                    self.crap_found = False
                    self.curr_row.append(data)

def parse_height(text):
    return re.fullmatch('\d+\sto\s\d+\sm', text)
    
def parse_direction(text):
    # print(text)
    return re.fullmatch('\d{1,3}°\s–\s\d{1,3}°', text)

def parse_wind(text):
    return re.fullmatch('\d+\sm/s\s\(\d+\.\d+\sKm/h,\s\d+\.\d+\sKt\)', text)

def parse_unknown(text):
    return re.fullmatch('Unknown cloud base, or cloud base below and cloud top above the station level', text)

class MyHTMLParser2(HTMLParser):
    def __init__(self):
        super().__init__()
        self.curr_row = []
  
    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if parse_height(data) or parse_direction(data) or parse_wind(data):
            self.curr_row.append(data)
        if parse_unknown(data):
            self.curr_row.append('Unknown')

link = "https://www.ogimet.com/cgi-bin/gsynres?ind=10444&lang=en&decoded=yes&ndays=2&ano=2017&mes=04&day=07&hora=23"

r = requests.get(link)
t = r.text
parser = MyHTMLParser()
parser.feed(t)
print(tabulate(parser.table))

table = []
for link in parser.links:
    link = 'https://www.ogimet.com' + link
    r = requests.get(link)
    parser = MyHTMLParser2()
    parser.feed(r.text.encode(encoding=r.encoding).decode(encoding='utf-8'))
    table.append(parser.curr_row)
print(tabulate(table))
