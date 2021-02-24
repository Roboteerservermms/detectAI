import csv
start_eui = 0x1f9eb7
end_eui = 0x1f9f10
start_latitude, start_longitude = 37.540166, 127.056670
f = open('eui_table.csv','w', encoding='utf-8', newline='')
wr = csv.writer(f)
wr.writerow([hex(i),start_latitude, start_longitude,0,False])
for i in range(start_eui, end_eui):
    wr.writerow([hex(i),start_latitude, start_longitude,0,False])
f.close()