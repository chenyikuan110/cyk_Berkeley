import csv

csv_name = 'Tx_Scan_bits_unfolded_newTX.csv'
# Open the CSV file in read mode
with open(csv_name) as file_obj:
    reader_obj = csv.reader(file_obj)
    var_name = ''
    bits = []
    count = 0
    for row in reversed(list(reader_obj)):
        temp = row[2].split('[')
        if temp[0] == 'Bit_Name':
            continue
        temp2 = temp[1].split(']')[0]

        if var_name != temp[0]:

            if bits != []:
                val = 0
                # print(var_name, bits, count)
                for i in range(count):
                    # print(i, bits[i], 2**(count-i-1))
                    val += bits[i] * (2 ** (count-i-1))
                # print(var_name, count, val, '{:0{width}b}'.format(val, width=count))
                # SCAN_LIST.append(ScanBit('DCOC_SN_QE', 1, 0b0))
                print('SCAN_LIST.append(ScanBit(\''+var_name+'\','+str(count)+',0b'+'{:0{width}b}'.format(val, width=count)+'))')
            var_name = temp[0]

            count = 0
            bits = []

        bits.append(int(row[3]))
        count += 1

    # last one
    if bits != []:
        val = 0
        # print(var_name, bits, count)
        for i in range(count):
            # print(i, bits[i], 2**(count-i-1))
            val += bits[i] * (2 ** (count - i - 1))
        # print(var_name, count, val, '{:0{width}b}'.format(val, width=count))
        print('SCAN_LIST.append(ScanBit(\''+var_name+'\','+str(count)+',0b'+'{:0{width}b}'.format(val, width=count)+'))')

