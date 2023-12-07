import csv

file_path = 'POIsLightshipDevPortal.csv'

with open(file_path, 'r') as infile:
    reader = csv.reader(infile)
    header = next(reader)

    columns_to_remove = ['id', 'img_uri', 'address', 'localizability']
    indices_to_remove = [header.index(col) for col in columns_to_remove if col in header]

    with open('POIdb.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile)


        new_header = [col for col in header if col not in columns_to_remove]
        writer.writerow(new_header)

        for row in reader:
            new_row = [row[i] for i in range(len(row)) if i not in indices_to_remove]
            writer.writerow(new_row)
            #if 'img_uri' in header and header.index('img_uri') < len(row) and row[header.index('img_uri')]:
            #    new_row = [row[i] for i in range(len(row)) if i not in indices_to_remove]
            #    writer.writerow(new_row)

print("Processing is complete")
