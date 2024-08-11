import csv

csv_name = 'Cobra_Full_Scan_bits_unfolded.csv'
# Open the CSV file in read mode

rows = []
header = ''
with open(csv_name) as file_obj:
    reader_obj = csv.reader(file_obj)
    i = 0
    for row in reader_obj:
        i += 1
        if i < 2:
            header = row
            continue
        rows.append(row)

csv_name = 'Cobra_Full_Scan_bits_unfolded_reversed.csv'
# Open the CSV file in read mode
print(header)
with open(csv_name, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    csv_writer.writerow(header)
    for row in reversed(list(rows)):
        csv_writer.writerow(row)
