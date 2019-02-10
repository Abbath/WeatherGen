import requests
from html.parser import HTMLParser
import re
from tabulate import tabulate
import datetime
import sys
import argparse
import csv
from io import StringIO
import locale

def parse_float(text):
    try:
        float(text)
        return True
    except:
        return False

def parse_int(text):
    try:
        int(text)
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

def parse_nw(text):
    return re.fullmatch('[NWSECAL]{1,3}', text)

def diff_link(link):
    if re.findall("weather\.uwyo\.edu", link):
        return 2
    elif re.findall("www\.ogimet\.com", link):
        return 1
    else:
        return 0

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
        self.station_number = -1
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
        if self.td_found and (parse_float(data) 
            or parse_date(data) 
            or parse_time(data) 
            or parse_crap(data) 
            or parse_filler(data)
            or parse_nw(data)):
            if parse_date(data):
                if self.curr_row:
                    self.table.append(self.curr_row)
                self.curr_row = [data]
            elif not self.curr_row:
                if parse_int(data) and self.station_number == -1:
                    self.station_number = int(data)
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

def parse_height_2(text):
    return re.match('\d+\sm', text)
    
def parse_direction(text):
    # print(text)
    return re.fullmatch('(\d{1,3}°\s–\s\d{1,3}°|Calm)', text)

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
        if parse_height(data) or parse_direction(data) or parse_wind(data) or parse_height_2(data):
            self.curr_row.append(data)
        if parse_unknown(data):
            self.curr_row.append('Unknown')

def parse_day(text):
    x = re.findall('\d\dZ \d\d \w\w\w \d\d\d\d', text)
    date = datetime.datetime.strptime(x[0], '%HZ %d %b %Y')
    return date

def parse_sn(text):
    x = re.match('\d\d\d\d\d', text).group()
    return int(x)

class MyHTMLParser3(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h2_found = False
        self.h2_inside = False
        self.pre_found = False
        self.table = []
        self.tables = []
        self.curdate = ''
        self.sn = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'h2':
            self.h2_found = True
            self.h2_inside = True
        elif tag == 'h3':
            self.h2_found = False
        elif tag == 'pre':
            self.pre_found = True

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.pre_found = False
        elif tag == 'h2':
            self.h2_inside = False

    def handle_data(self, data):
        if self.h2_inside:
            self.curdate = parse_day(data)
            self.sn = parse_sn(data)
        elif self.pre_found and self.h2_found:
            x = '\n'.join(data.split('\n')[6:-1])
            f = StringIO(x)
            r = csv.reader(f, delimiter=' ', skipinitialspace=True)
            self.table = []
            for row in r:
                if float(row[0]) >= 500:
                    self.table.append(row[0:3]+row[6:8])
            self.tables.append((self.curdate, self.table))
            

header = "Produced by METEREOLOGIA Version: 5.3 Level: 0.704\nNONE"

humidities = {}
first = True

def parse_dat(dt, filename):
    global first
    global humidities
    if first:
        first = False
        f = open(filename, 'r')
        r = csv.reader(f)
        for row in r:
            date = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M")
            humidities[date] = row[1]
    return float(humidities[dt])

def parse_precipitation(text):
    x = re.match('\d+\.\d+', text)
    if x:
        return x.group()
    else:
        return '0.0'

def parse_cloud_base(text):
    x = re.match('\d+', text)
    if x:
        return x.group()
    else:
        return '100'

def parse_wind_direction(text):
    x = re.match('\d+', text)
    if x:
        return x.group()
    else:
        return None

def generate(table1, table2, sn, output, dat):
    data = header
    table1.reverse()
    table2.reverse()
    startdate = datetime.datetime.strptime(table1[0][0]+"T"+table1[0][1],'%m/%d/%YT%H:%M')
    enddate = datetime.datetime.strptime(table1[-1][0]+"T"+table1[-1][1],'%m/%d/%YT%H:%M')
    data += '\n{:>6}  {}{:>4}{:>6}  {}{:>4}    5    1'.format(startdate.year, startdate.timetuple().tm_yday, startdate.hour, 
    enddate.year, enddate.timetuple().tm_yday, enddate.hour)
    data += '\n   {}'.format(sn)
    for i in range(len(table1)):
        datet = datetime.datetime.strptime(table1[i][0]+"T"+table1[i][1],'%m/%d/%YT%H:%M')
        data += '\n{}{:>4}{:>4}'.format(datet.year, datet.timetuple().tm_yday, datet.hour)
        wdir = parse_wind_direction(table2[i][1])
        data += '\n{:9.3f}{:9.3f}    {}    {}{:9.3f}{:5.0f}{:9.3f}    {}'.format(
            float(re.match('\d+', table2[i][2]).group()),
            float(wdir if wdir else 0),
            parse_cloud_base(table2[i][0]),
            table1[i][13],
            float(table1[i][2]) + 273.16,
            parse_dat(datet, dat),
            float(table1[i][9]),
            parse_precipitation(table1[i][11]))
    if output:
        with open(output, 'w') as f:
            f.write(data)
    else:
        print(data)

link = "https://www.ogimet.com/cgi-bin/gsynres?ind=10444&lang=en&decoded=yes&ndays=2&ano=2017&mes=04&day=07&hora=23"

header2 = """UP.DAT          2.0             Header structure with coordinate parameters                     
   1
Produced by READ62 Version: 5.5  Level: 030402                                  
NONE    """

def generate2(tables, sn, output):
    data = header2
    startdate = tables[0][0]
    enddate = tables[-1][0]
    data += '\n {:5}{:5}{:5}{:5}{:5}{:5}{:>5}    2    1'.format(startdate.year, startdate.timetuple().tm_yday, startdate.hour, enddate.year, enddate.timetuple().tm_yday, enddate.hour, tables[0][1][-1][0].rstrip("0"))
    data += '\n     F    F    F    F'
    for t in tables:
        date = t[0]
        data += '\n   6201{:>10}{:7}{:2}{:2}{:2}     12                                4\n'.format(sn, date.year, date.month, date.day, date.hour)
        table = t[1]
        counter = 0
        for row in table:
            data += ('\n' if counter == 4 else '')+'{:9.1f}/{:>5}/{:5.1f}/{:3}/{:3}'.format(
                float(row[0]), 
                row[1]+'.',
                float(row[2])+273.16,
                int(row[3]),
                int(row[4]))
            if counter == 4:
                counter = 0
            counter += 1           
    if output:
        with open(output, 'w') as f:
            f.write(data)
    else:
        print(data)

def process(link, output, dat, handler=print, verbose=False):
    # locale.setlocale(locale.LC_TIME, "en-US")
    if diff_link(link) == 2:
        if verbose:
            handler('Start page processing...')
        r = requests.get(link)
        t = r.text
        parser = MyHTMLParser3()
        parser.feed(t)
        if verbose:
            for table in parser.tables:
                handler(str(table[0]))
                handler(tabulate(table[1]))
                handler('Generating report...')
        generate2(parser.tables, parser.sn, output)
        if verbose:
            handler('Report generated.')
        return

    if verbose:
        handler('Start main page processing...')
    r = requests.get(link)
    t = r.text
    parser1 = MyHTMLParser()
    parser1.feed(t)
    if verbose:
        handler(tabulate(parser1.table))
        handler('Start link processing...')
    table = []
    counter = 1
    for link in parser1.links[::2]:
        if verbose:
            handler('Processing link {}/{} ...'.format(counter, len(parser1.links[::2])))
        counter += 1
        link = 'https://www.ogimet.com' + link
        r = requests.get(link)
        parser = MyHTMLParser2()
        parser.feed(r.text.encode(encoding=r.encoding).decode(encoding='utf-8'))
        table.append(parser.curr_row)
    if verbose:
        handler(tabulate(table))
        handler('Generating report...')
    generate(parser1.table, table, parser1.station_number, output, dat)
    if verbose:
        handler('Report generated.')

def main():
    input_parser = argparse.ArgumentParser(
        description="""""",
        epilog="""\
        In case of any questions, feel free to write: pitongogi@gmail.com
        """
    )

    input_parser.add_argument("-i", "--input", help="Input link", action="store")
    input_parser.add_argument("-o", "--output", help="Output file", action="store")
    input_parser.add_argument("-d", "--dat", help="Dat file", action="store")
    input_parser.add_argument("-v", "--verbose", help="VErbose output", action="store_true")

    arguments = input_parser.parse_args(sys.argv[1:])

    if isinstance(arguments.input, type(None)):
        link = input('Enter link: ')
    else:
        link = arguments.input
    
    if isinstance(arguments.output, type(None)):
        output = None
    else:
        output = arguments.output

    if diff_link(link) == 2:
        dat = ''
    elif isinstance(arguments.dat, type(None)):
        dat = input('Enter dat: ')
    else:
        dat = arguments.dat

    process(link, output, dat, verbose=arguments.verbose)

if __name__ == '__main__':
    main()