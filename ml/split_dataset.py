import csv

FROM_FILE = r"F:\QMDownload\libsvm_packs\dataset\Disk_SMART_dataset.txt"
TO_FILE = r"points_data/part_before_"
data_set = []

def get_xh_data(from_file, x = 12):
	data_set = []
	fp = open(from_file, "r")
	reader = csv.reader(fp)
	one_disk_set = []
	i = 1
	for row in reader:
		if int(row[0]) == i:
			one_disk_set.append(row)
		else:
			one_disk_set.reverse()
			if len(one_disk_set) >= x:
				data_set.append(one_disk_set[x - 1])
			else :
				pass
				#data_set.append(one_disk_set[len(one_disk_set) - 1])
			one_disk_set = []
			i += 1
			one_disk_set.append(row)
	one_disk_set.reverse()
	data_set.append(one_disk_set[x - 1])
	one_disk_set = []
	fp.close()
	print len(data_set)
	return data_set

def write_to_file(data_set, to_file):
	fp = open(to_file, "w")
	split_char = ","
	for row in data_set:
		tmp_str = split_char.join(row)
		fp.write(tmp_str)
		fp.write("\n")
	fp.close()


if __name__ == "__main__":
	for h in [1, 2, 4, 6, 8, 10, 12, 24, 48, 96]:
		write_to_file(get_xh_data(FROM_FILE, h), TO_FILE + str(h) + r"h.txt")

