import csv
import textwrap
csv_name = 'Full_Scan_bits_newTX_unfolded.csv'

with open(csv_name) as file_obj:
    reader_obj = csv.reader(file_obj)
    bits = []
    for row in reader_obj:
        temp = row[2].split('[')
        if temp[0] == 'Bit_Name':
            continue
        if int(row[0]) <= 147:
            bits.append(int(row[4]))

    # bits_string = "".join(map(lambda x: str(int(x)), bits))
    # print(textwrap.fill(bits_string, width=8))
    print(bits[::-1])
    for i in range(148):
        if i % 64 == 0:
            print('')
        if i % 8 == 0:
            bits_string = "".join(map(lambda x: str(int(x)), bits[i:i+8]))
            print(f'{i % 64} to {(i+7) % 64}: {bits_string}')
