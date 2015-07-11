#coding = utf8
import os
import numpy as np
import pylab as pl
import csv 
import re
import time

DATE_PATTERN = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
DATE_PATTERN1 = re.compile('[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}')
DATE_FORMATER = '%Y-%m-%d'
DATE_FORMATER1 = '%Y/%m/%d'
FAILURES_FILE = 'TMP_failures_6-8.csv'
FAIL_IPS_FILE = 'TMP_failures_ips_6-8.csv'
REL_IPS_FPATH= 'TMP_rel_ips'
METRIC = 'cpu_load_5min'

def date_to_stamp(date):
	match = DATE_PATTERN.match(date)
	if not match:
		return None
	else:
		return int(time.mktime(time.strptime(date, DATE_FORMATER)))

def stamp_to_date(stamp):
	return time.strftime(DATE_FORMATER, time.localtime(stamp))

def get_relative_ips(rel_file):
	try:
		fp = open(rel_file)
	except:
		print 'REL_FILE not found'
		return None
	reader = csv.reader(fp)
	ips = []
	for row in reader:
		if row and len(row) > 0:
			ips.append(str(row[0]))
	fp.close()
	return ips

def get_metric_by_date(path, date, ip, metric = METRIC):
	file = path + date + os.sep + metric + '.csv'
	try:
		fp = open(file)
	except:
		print file, 'not found'
		return None
	values = []
	reader = csv.reader(fp)
	for row in reader:
		if str(row[0]) == ip:
			values.append(float(row[1]))
	fp.close()
	return values

def get_metric_prev_day(date, ip, metric = METRIC):
	now_stamp = date_to_stamp(date)
	if now_stamp == None:
		return None
	prev_day_stamp = now_stamp - 24 * 60 * 60
	prev_day = stamp_to_date(prev_day_stamp)
	BASE_PATH = '06-08' + os.sep
	return get_metric_by_date(BASE_PATH, prev_day, ip, metric)

def get_metric_prev_week(date, ip, metric = METRIC):
	now_stamp = date_to_stamp(date)
	if now_stamp == None:
		return None
	prev_day_stamp = now_stamp - 7 * 24 * 60 * 60
	prev_day = stamp_to_date(prev_day_stamp)
	BASE_PATH = '06-08' + os.sep
	return get_metric_by_date(BASE_PATH, prev_day, ip, metric)

def compute_two_list_error(list1, list2):
	if len(list1) != len(list2):
		return None
	return list(map(lambda x: x[0] - x[1], zip(list1, list2)))

def draw_two_lines_(name, line_x, line1_y, line2_y, line3_y):
	if line1_y == None or line2_y == None or line3_y == None:
		return
	line_x = [i for i in range(0, len(line1_y))]
	pl.figure(1)
	data_subplot = pl.subplot(212)
	err_subplot = pl.subplot(211)

	#failure data and normal data
	plot1 = pl.plot(line_x, line1_y, 'r', label='failure day')
	plot2 = pl.plot(line_x, line2_y, 'g', label='prev day')
	plot3 = pl.plot(line_x, line3_y, 'y', label='prev week')
	pl.title(METRIC)
	pl.xlabel('time point')
	pl.ylabel('value')
	pl.xlim(0, 400)
	#pl.ylim(-10, 100)
	pl.legend()
	pl.sca(data_subplot)

	#error between two
	err_line1 = compute_two_list_error(line1_y, line2_y)
	err_line2 = compute_two_list_error(line1_y, line3_y)
	plot4 = pl.plot(line_x, err_line1, 'b', label='prev day error')
	plot4 = pl.plot(line_x, err_line2, 'c', label='prev week error')
	pl.xlabel('time point')
	pl.ylabel('value')
	pl.xlim(0, 400)
	#pl.ylim(-110, 110)
	pl.legend()
	pl.sca(err_subplot)

	if not os.path.exists('images' + os.sep + METRIC):
		os.mkdir('images' + os.sep + METRIC)
	pl.savefig('images' + os.sep + METRIC + os.sep + name + '.png', dpi=120)

	#pl.show()
	pl.clf()

def draw_one_line(name, line_y):
	if line_y == None or len(line_y) == 0:
		return
	line_x = [i for i in range(0, len(line_y))]
	pl.figure(1)
	pl.plot(line_x, line_y, 'b', label='CPU')
	pl.xlabel('Time')
	pl.ylabel('Host Load')
	pl.xticks([i for i in range(0, len(line_x), 288)])
	pl.grid(True)
	pl.legend()

	path = 'images' + os.sep + 'single'
	if not os.path.exists(path):
		os.mkdir(path)
	pl.savefig(path + os.sep + name + '.png', dpi = 320)
	pl.clf()

def read_values_by_ip(ip, metric = 'cpu_total_utili'):
	start_date = '2014-08-21'
	end_date = '2014-08-24'
	day_stamp = 24 * 60 * 60
	base_dir = '06-08' + os.sep
	found = False
	value = []
	start_stamp = date_to_stamp(start_date)
	end_stamp = date_to_stamp(end_date)
	for i in range(start_stamp, end_stamp, day_stamp):
		day = stamp_to_date(i)
		try:
			fp = open(base_dir + day + os.sep + metric + '.csv')
			reader = csv.reader(fp)
			for row in reader:
				if row and len(row) > 1:
					if row[0] == ip:
						value.append(int(row[1]))
						found = True
					elif found:
						break
					else:
						pass
				else:
					pass
			fp.close()
		except Exception, e:
			print str(e)
		found = False
	return value

if __name__ == "__main__":
	x = [i for i in range(0, 288)]
	'''
	ip = '10.226.134.164'
	date = '2014-08-22'
	BASE_PATH = date[5:7] + os.sep
	y1 = get_metric_by_date(BASE_PATH, date, ip)
	y2 = get_metric_prev_day(date, ip)
	y3 = get_metric_prev_week(date, ip)
	
	draw_two_lines_(ip + '_' + date, x, y1, y2, y3)
	'''
	'''
	fp = open(FAILURES_FILE)
	reader = csv.reader(fp)
	failure_ips = []
	for row in reader:
		ip = row[1]
		match = DATE_PATTERN1.match(row[6])
		if match:
			stamp = int(time.mktime(time.strptime(match.group(), DATE_FORMATER1)))
			date = time.strftime(DATE_FORMATER, time.localtime(stamp))
			print ip, date
			BASE_PATH = '06-08' + os.sep
			y1 = get_metric_by_date(BASE_PATH, date, ip)
			y2 = get_metric_prev_day(date, ip)
			y3 = get_metric_prev_week(date, ip)
			if y1 != None and y2 != None and y3 !=None:
				failure_ips.append(ip)
	 			draw_two_lines_(ip + '_' + date, x, y1, y2, y3)
	 			rel_file = REL_IPS_FPATH + os.sep + ip + '_rel_ips.csv'
	 			rel_ips = get_relative_ips(rel_file)
	 			for ip_i in rel_ips:
	 				y1 = get_metric_by_date(BASE_PATH, date, ip_i)
					y2 = get_metric_prev_day(date, ip_i)
					y3 = get_metric_prev_week(date, ip_i)
					if y1 != None and y2 != None and y3 !=None:
						draw_two_lines_(ip + '_' + ip_i + '_' + date, x, y1, y2, y3)
		else:
			pass

	fp.close()
	'''
	fp = open('TMP.csv')
	reader = csv.reader(fp)
	for row in reader:
		if row and len(row) > 0:
			ip = row[0]
			value = read_values_by_ip(ip)
			draw_one_line(ip, value)
	fp.close
'''
	fp = open(FAIL_IPS_FILE, 'w')
	for ip in failure_ips:
		fp.write(ip + '\n')
	fp.close()
'''


