import csv

csv_name = 'cobrascanstuff/LO.csv'
# Open the CSV file in read mode
with open(csv_name) as file_obj:
    reader_obj = csv.reader(file_obj)
    i = 0
    for row in reversed(list(reader_obj)):
        # i += 1
        # if i < 2:
        #     continue
        var_name = row[3]
        width = int(row[0])
        val = int(row[5])
        # print('['+row[0]+':'+str(int(row[0])+width-1)+'] SCAN_LIST.append(ScanBit(\''+var_name+'\', '+str(width)+', 0b'+'{:0{width}b}'.format(val, width=width)+'))')
        print('SCAN_LIST.append(ScanBit(\'' + var_name + '\', ' + str(
            width) + ', 0b' + '{:0{width}b}'.format(val, width=width) + '))')