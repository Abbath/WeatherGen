import csv
import datetime

def parse_float(text):
    try:
        float(text)
        return True
    except:
        return False

f = open('p.dat','r')
r = csv.reader(f)

ff = open('d.dat','w')
w = csv.writer(ff)

current_hour = -1
current_avg = 0
counter = 0
for row in r:
    if not parse_float(row[-1]):
        continue
    date = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
    if current_hour == -1:
        current_hour = date.hour
        current_avg = float(row[-2])
        counter += 1
    elif current_hour != date.hour:
        rr = [date.strftime("%Y-%m-%d %H:00"), current_avg / counter]
        w.writerow(rr)
        current_hour = date.hour
        current_avg = float(row[-2])
        counter = 1
    else:
        current_avg += float(row[-2])
        counter += 1
    # print(date)
    