from openpyxl import load_workbook
import sys

header = """TERREL.DAT      2.0             Header structure with coordinate parameters                     
   1
Produced by TERREL Version: 3.3  Level: 030402                                  
UTM     
  34N   
WGS-G   10-10-2002  
      40      40     340.000    5504.000       1.000       1.000
KM  M   
W_E N_S
"""

def main(args):
    fname = args[1]
    res = header
    wb = load_workbook(fname)
    ws = wb.active
    m = 61
    n = 41
    counter = 0
    for row in ws.rows:
        v = row[1].value
        if isinstance(v, float):
            res += '{:8.1f}'.format(v)
            counter += 1
            if counter == 61:
                counter = 0
                res += '\n'
    fname0 = args[2] if len(args) > 2 else "res.dat"
    f = open(fname0, 'w')
    f.write(res)
    f.close()

if __name__ == '__main__':
    main(sys.argv)