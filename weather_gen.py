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
import numpy as np
from scipy.stats import linregress

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
    return re.fullmatch('(\d{1,3}°\s–\s\d{1,3}°|Calm)', text)

def parse_wind(text):
    return re.fullmatch('\d+\sm/s\s\(\d+\.\d+\sKm/h,\s\d+\.\d+\sKt\)', text)

def parse_unknown(text):
    return re.fullmatch('Unknown cloud base, or cloud base below and cloud top above the station level', text)

def parse_imgs(text):
    if 'sol' in text:
        return 0
    elif 'cubierto_noche' in text:
        return 1
    elif 'cubierto' in text:
        return 2
    elif 'lluvia_noche' in text:
        return 3
    elif 'lluvia' in text:
        return 4
    elif 'llovizna_noche' in text:
        return 5
    elif 'llovizna' in text:
        return 6
    elif 'lunanub' in text:
        return 7
    elif 'luna' in text:
        return 8
    elif 'nuboso' in text:
        return 9
    elif 'nieve_noche' in text:
        return 10
    elif 'nieve' in text:
        return 11
    elif 'humo' in text:
        return 12
    elif 'bruma_noche' in text:
        return 13
    elif 'bruma' in text:
        return 14
    elif 'niebla_noche' in text:
        return 15
    elif 'niebla' in text:
        return 16
    else:
        return -1

class MyHTMLParser2(HTMLParser):
    def __init__(self):
        super().__init__()
        self.curr_row = []
        self.pre = False
  
    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.pre = True

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if self.pre:
            six, _ = parse_magic_numbers(data)
            self.curr_row.append(six)
            self.pre = False
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

class MyHTMLParser4(HTMLParser):
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
        if tag == 'img':
            img = dict(attrs)
            ref = img['src']
            self.curr_row.append(parse_imgs(ref))

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
                    self.table.append(self.curr_row[:18])
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

def parse_dew(text):
    return 'Dew' in text

def parse_celsius(text):
    x = text.split()
    if len(x) < 2:
        return False
    num = x[0]
    c = x[1]
    if c != 'C':
        return False
    return float(num)

def parse_magic_numbers(text):
    first_line = text.split('\n')[0]
    x = re.findall('\s[56][\d|/]{4}', first_line)
    y = re.findall('\s7[\d|/]{4}', first_line)
    six = 0
    if x:
        x[-1] = x[-1][1:]
        if x[-1][0] == '5':
            pass
        else:
            try:
                six_tmp = int(x[-1][1:3])
                if six_tmp == 99:
                    six = int(x[-1][3:4]) / 10
                else:
                    six = int(x[-1][1:4])
            except ValueError:
                six = 0
    w1 = 0
    ww = 0
    if y:
        y[-1] = y[-1][1:]
        try:
            w1 = int(y[-1][3:4])
            ww = int(y[-1][1:3])
        except ValueError:
            ww = 0
    return (six, (ww, w1))

class MyHTMLParser5(HTMLParser):
    def __init__(self):
        super().__init__()
        self.curr_row = []
        self.dew = False
        self.pre = False
  
    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.pre = True

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if self.pre:
            six, seven = parse_magic_numbers(data)
            self.curr_row.append(six)
            self.curr_row.append(seven[0])
            self.curr_row.append(seven[1])
            self.pre = False
        if self.dew and isinstance(parse_celsius(data), float):
            self.curr_row.append(parse_celsius(data))
            self.dew = False
        if parse_dew(data):
            self.dew = True
        if parse_height(data) or parse_direction(data) or parse_wind(data) or parse_height_2(data):
            self.curr_row.append(data)
        if parse_unknown(data):
            self.curr_row.append('Unknown')

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

def generate_row(i, table1, table2, dat):
    datet = datetime.datetime.strptime(table1[i][0]+"T"+table1[i][1],'%m/%d/%YT%H:%M')
    wdir = parse_wind_direction(table2[i][2])
    stuff = np.array([float(re.match('\d+', table2[i][3]).group()),
        float(wdir if wdir else 0),
        float(parse_cloud_base(table2[i][1])),
        float(table1[i][13]),
        float(table1[i][2]) + 273.16,
        float(parse_dat(datet, dat)),
        float(table1[i][9]),
        float(table2[i][0])])
    return datet, stuff

def time_delta(d1, d2):
    return int((d2 - d1).total_seconds() // 3600)

def f(x, y):
    s,c,_,_,_ = linregress(x, y)
    return s, c

def generate_missing_rows(i, delta, datet, dates, stuff):
    start = max(0, i - 4)
    finish = i + 5
    a = stuff[start:finish+1, :]
    d = dates[start:finish+1]
    d1 = d[0]
    x = [0]
    for dd in d[1:]:
        x.append(time_delta(d1, dd))
    missing = []
    for i in range(delta-1):
        missing.append( time_delta(d1, datet) + 1 + i)
    x = np.array(x)
    s, c  = np.apply_along_axis(lambda xx : f(x, xx), 0, a)
    res = np.zeros((len(missing), stuff.shape[1]))
    for i, m in enumerate(missing):
        res[i, :] = s * m + c
    resdates = []
    for m in missing:
        resdates.append(d1 + datetime.timedelta(hours=m))
    return resdates, res

def generate(table1, table2, sn, output, dat):
    data = header
    table1.reverse()
    table2.reverse()
    all_shit = np.zeros((len(table1), 8))
    startdate = datetime.datetime.strptime(table1[0][0]+"T"+table1[0][1],'%m/%d/%YT%H:%M')
    enddate = datetime.datetime.strptime(table1[-1][0]+"T"+table1[-1][1],'%m/%d/%YT%H:%M')
    data += '\n{:>6}  {}{:>4}{:>6}  {}{:>4}    5    1'.format(startdate.year, startdate.timetuple().tm_yday, startdate.hour, 
    enddate.year, enddate.timetuple().tm_yday, enddate.hour)
    data += '\n   {}'.format(sn)
    dates = []
    for i in range(len(table1)):
        datet, stuff = generate_row(i, table1, table2, dat)
        dates.append(datet)
        all_shit[i, :] = stuff

    for i in range(len(table1)):
        datet = dates[i]
        stuff = all_shit[i,:]

        data += '\n{}{:>4}{:>4}'.format(datet.year, datet.timetuple().tm_yday, datet.hour)
        data += '\n{:9.3f}{:9.3f}    {}    {}{:9.3f}{:5.0f}{:9.3f}    {}'.format(*stuff)

        if i < len(table1) - 1:
            delta = time_delta(datet, dates[i+1])
            if delta != 1:
                dates1, all_shit1 = generate_missing_rows(i, delta, datet, dates, all_shit)
                for i in range(delta-1):
                    datet1 = dates1[i]
                    stuff1 = all_shit1[i, :]
                    data += '\n{}{:>4}{:>4}'.format(datet1.year, datet1.timetuple().tm_yday, datet1.hour)
                    data += '\n{:9.3f}{:9.3f}    {}    {}{:9.3f}{:5.0f}{:9.3f}    {}'.format(*stuff1)

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

def process(link, output, dat, handler=print, verbose=False, second=False, remtags=False):
    # locale.setlocale(locale.LC_TIME, "en-US")
    if diff_link(link) == 2:
        if verbose:
            handler('Start page processing...')
        r = requests.get(link)
        t = r.text
        if remtags:
            parser_a = MyHTMLParser6()
            parser_a.feed(t)
            if verbose:
                handler('Removing tags...')
            with open(output, 'w') as f:
                f.write(parser_a.res)
        else:
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
    parser1 = MyHTMLParser4() if second else MyHTMLParser()
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
        parser = MyHTMLParser5() if second else MyHTMLParser2()
        parser.feed(r.text.encode(encoding=r.encoding).decode(encoding='utf-8'))
        table.append(parser.curr_row)
    if verbose:
        handler(tabulate(table))
        handler('Generating report...')
    if second:
        generate3(parser1.table, table, output, dat)
    else:
        generate(parser1.table, table, parser1.station_number, output, dat) 
    if verbose:
        handler('Report generated.')

header3 = """	Local				UTC	(GMT)		Temp	DewP	RH	P, stn	P, sea	Cloud	CloudH	Weather,	Code	WD	WS	Precipitation
Year	Month	Day	Time	Year	Month	Day	Time	C	C	%	hPa	hPa	0-10	M	W	WW	degree	m/s	mm"""

def parse_clouds(num):
    if num in [3,4]:
        return 0.1
    elif num in [5,6]:
        return 0.05
    else:
        return 0

def generate_row3(i, table1, table2, dat):
    datet = datetime.datetime.strptime(str(table1[i][0])+"T"+str(table1[i][1]),'%m/%d/%YT%H:%M')
    wdir = parse_wind_direction(table2[i][4])
    stuff = np.array([
        float(table1[i][2]),
        float(table2[i][6]),
        float(parse_dat(datet, dat)),
        float(table1[i][9]),
        float(table1[i][10]),
        float(table1[i][13]),
        float(parse_cloud_base(table2[i][3])),
        float(table2[i][2]),
        float(table2[i][1]),
        float(wdir if wdir else 0),
        float(re.match('\d+', table2[i][5]).group()),
        float(table2[i][0])])
    return datet, stuff

def generate3(table1, table2, output, dat):
    data = header3
    table1.reverse()
    table2.reverse()
    all_shit = np.zeros((len(table1), 12))
    dates = []
    for i in range(len(table1)-1):
        datet, stuff = generate_row3(i, table1, table2, dat)
        dates.append(datet)
        all_shit[i, :] = stuff

    for i in range(len(table1)-1):
        datet = dates[i]
        stuff = all_shit[i,:]

        data += '\n{}{:>4}{:>4}{:>4} '.format(datet.year, datet.month, datet.day, datet.hour)
        data += '{}{:>4}{:>4}{:>4}'.format(datet.year, datet.month, datet.day, datet.hour+0)
        data += '{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}'.format(*stuff)
            
        if i < len(table1) - 2:
            delta = time_delta(datet, dates[i+1])
            if delta != 1:
                dates1, all_shit1 = generate_missing_rows(i, delta, datet, dates, all_shit)
                for i in range(delta-1):
                    datet1 = dates1[i]
                    stuff1 = all_shit1[i, :]
                    data += '\n{}{:>4}{:>4}{:>4} '.format(datet1.year, datet1.month, datet1.day, datet1.hour)
                    data += '{}{:>4}{:>4}{:>4}'.format(datet1.year, datet.month, datet1.day, datet1.hour+0)
                    data += '{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}'.format(*stuff1)

    if output:
        with open(output, 'w') as f:
            f.write(data)
    else:
        print(data)

class MyHTMLParser6(HTMLParser):
    def __init__(self):
        super().__init__()
        self.res = ""
        self.h2 = False
        self.h3 = False
  
    def handle_starttag(self, tag, attrs):
        if tag == 'h2':
            self.h2 = True
        if tag == 'h3':
            self.h3 = True

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if data != '\n':
            self.res += data
            if self.h2:
                self.res += '\n'
                self.h2 = False
            if self.h3:
                self.res += '\n'
                self.h3 = False

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
    input_parser.add_argument("-s", "--second", help="Second version", action="store_true")
    input_parser.add_argument("-r", "--remtags", help="Remove tags", action="store_true")

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

    process(link, output, dat, verbose=arguments.verbose, second=arguments.second, remtags=arguments.remtags)

if __name__ == '__main__':
    main()
