import csv

csv_A = 'ITXLowGain.csv'
csv_B = 'QNbroken.csv'

dict_A = []
dict_B = []
with open(csv_A) as file_obj:
    reader_obj = csv.reader(file_obj)
    for row in (list(reader_obj)):
        dict_A.append([row[0],int(row[1])])
        # print(dict_A[-1])

with open(csv_B) as file_obj:
    reader_obj = csv.reader(file_obj)
    for row in (list(reader_obj)):
        dict_B.append([row[0], int(row[1])])

name_str = 'Signal'
val_A = 'Val_A'
val_B = 'Val_B'
print(f'{name_str:>25},{val_A:>4},{val_B}')
for row in dict_B:
    row_A = next((obj for obj in dict_A if obj[0] == row[0]), None)
    if not row[1] == row_A[1]:
        print(f'{row[0]:>25}, { row_A[1]:>4}, { row[1]:>4}')