#coding=utf-8
import os
import csv
import pickle
import time
import copy
import pylab as pl

#原始采样频率分钟
SAMPLE_FREQUENCE = 5

#特征选取的时间窗口分钟
ATTR_TIME_WINDOW = 120
#合并点的数量
MERGE_NUM = 4
#结果标签的间隔值
LABEL_DISTANCE = 2

#预测点之前的时间点
BEFORE = 30
#之前的原始数据点点个数
ATTR_NUM = 6

#最终特征个数
FEATURE_NUM = 4

ERROR = 10


#1. 读取连续MERGE_NUM个数值点，求平均，然后除以LABEL_DISTANCE得到标签值，合并为这个时间段的值；再读取下一个MERGE_NUM个点进行合并
#2. 保存连续的(ATTR_TIME_WINDOW)/(SAMPLE_FREQUENCE*MERGE_NUM)+1个数值，作为一个新样本写入训练集
#3. 每个样本中，前(ATTR_TIME_WINDOW)/(SAMPLE_FREQUENCE*MERGE_NUM)是特征，最后一个是结果标签
def prepare_data_1(source_path, target_path):
	label_pos = ATTR_NUM #after 120/5/4=6 points, there is a target value
	i_merge = 0
	i_training = 0
	data_set = []
	label_set = []
	merge_list = []
	value_merge = 0
	try:
		fp = open(source_path)
		reader = csv.reader(fp, delimiter = ',')
		reader.next()
		for row in reader:
			if int(row[1]) < 0:
				continue 
			if i_merge == MERGE_NUM:
				merge_list.append(value_merge / MERGE_NUM / LABEL_DISTANCE * LABEL_DISTANCE) #0, 2, 4, 6, ... 98, 100
				value_merge = int(row[1])
				i_merge = 1
			else:
				if int(row[1]) < 0:
					value_merge += 0
				else:
					value_merge += int(row[1])
				i_merge += 1
		fp.close()
	except Exception, e:
		print str(e)

	feature_num = 0
	row = ''
	try:
		fp = open(target_path, "w")
		for i in range(0, len(merge_list) - label_pos - 1):
			#features
			while feature_num < label_pos:
				row += str(merge_list[i + feature_num]) + ','
				feature_num += 1
			#label
			row += str(merge_list[i + feature_num])
			feature_num = 0
			fp.write(row + '\n')
			row = ''
		fp.close()
	except Exception, e:
		print str(e)

#use (raw value) / LABEL_DISTANCE * LABEL_DISTANCE as value
#F0 F1 F2 F3 F4 F5 B0 B1 B2 B3 B4 B5 P
#Fis are feature, Bis are blank points between predict point and feature points 
def prepare_data_2(source_path, target_path):
	before_pos = BEFORE / SAMPLE_FREQUENCE
	try:
		fp = open(source_path)
		reader = csv.reader(fp)
		reader.next()
		data_list = []
		for row in reader:
			if int(row[1]) < 0:
				continue
			data_list.append(int(row[1]) / LABEL_DISTANCE * LABEL_DISTANCE)
		fp.close()
	except Exception, e:
		print str(e)
	try:
		fp = open(target_path, "w")
		for i in range(0, len(data_list) - ATTR_NUM - before_pos):
			row = ''
			feature_num = 0
			#features
			while feature_num < ATTR_NUM:
				row += str(data_list[i + feature_num]) + ','
				feature_num += 1
			#label
			row += str(data_list[i + feature_num + before_pos - 1])	
			fp.write(row + '\n')
		fp.close()
	except Exception, e:
		print str(e)

#use (raw value) / LABEL_DISTANCE * LABEL_DISTANCE as value
#FT0 FT1 FT2 FT3 FT4 FT5 B0 B1 B2 B3 B4 B5 P
#FTis are temp features which final features are from them
#Features are: first, last, aver, minus...
def prepare_data_3(source_path, target_path):
	before_pos = BEFORE / SAMPLE_FREQUENCE
	try:
		fp = open(source_path)
		reader = csv.reader(fp)
		reader.next()
		data_list = []
		for row in reader:
			if int(row[1]) < 0:
				continue
			data_list.append(int(row[1]) / LABEL_DISTANCE * LABEL_DISTANCE)
		fp.close()
	except Exception, e:
		print str(e)
	try:
		fp = open(target_path, "w")
		for i in range(0, len(data_list) - ATTR_NUM - before_pos):
			tmp_num = 0
			max_ = 0
			min_ = 100
			aver = 0
			minus = 0
			total = 0
			prev = data_list[i]
			first = data_list[i]
			last = data_list[i + ATTR_NUM - 1]
			while  tmp_num < ATTR_NUM:
				if max_ < data_list[i + tmp_num]:
					max_ = data_list[i + tmp_num]
				if min_ > data_list[i + tmp_num]:
					min_ = data_list[i + tmp_num]
				total += data_list[i + tmp_num]
				minus = data_list[i + tmp_num] - prev
				prev = data_list[i + tmp_num]
				tmp_num += 1
			aver = total / ATTR_NUM
			row = str(first) + ',' + str(last) + ',' + str(aver) + \
			',' + str(minus) + ',' + str(data_list[i + tmp_num + before_pos - 1]) + '\n'
			fp.write(row)
		fp.close()
	except Exception, e:
		print str(e)

def train(data_file, Ai_list, Y_list, size):
	'''
		a1  													                   a2  a3  a4  ...
	y1  {num: n, 'pro': 0.0, 'ais': {'a1': {0:n, 2:n, 4:n, ...}, 'a2': {}, ... }}  {}  {}  {}  ...
	y2  ...
	y3  ...
	y4  ...
	...

	'''
	try:
		fp = open(data_file)
	except Exception, e:
		print str(e)
		return 0, None
	else:
		train_dict = {}
		ai_dict = {}
		total_num = 0
		#ai_dict = {'a0':{0:0, 2:0, 4:0, ...}, 'a1': {}, ...}
		for a in range(0, size):
			ai_dict['a' + str(a)] = {}
			for i in Ai_list:
				ai_dict['a' + str(a)][i] = 0
		#train_dict = {0: {'num': n, 'ais': {'a0':{0:0, 2:0, 4:0, ...}, 'a1':{}, ...}}, 2: {}, 4: {}}
		for i in Y_list:
			train_dict[i] = {}
			train_dict[i]['nums'] = 0
			#*********must use deepcopy, otherwise every key 'ai' would refer to same object and alter the value******#
			train_dict[i]['ais'] = copy.deepcopy(ai_dict)
		reader = csv.reader(fp, delimiter = ',')
		data_set = []
		for row in reader:
			#******************FOR (1) AND (2)***********************************#
			#if row and len(row) > 0 and row.count('-' + str(LABEL_DISTANCE)) == 0:
			#******************FOR (1) AND (2)***********************************#
			#******************FOR (3)***********************************#
			if row and len(row) >= size :
				tmp_row = []
			#******************FOR (3)***********************************#
				total_num += 1
				#statistics the number of Yj
				train_dict[int(row[size])]['nums'] += 1
				#0, 1, 2, 3, 4, 5 
				for i in range(0, size):
					tmp_row.append(int(row[i]))
					#statistics the number of Ai@Yj
					train_dict[int(row[size])]['ais']['a' + str(i)][int(row[i])] += 1
				data_set.append(tmp_row)
		fp.close()
		compute(total_num, train_dict)

		#corrcoef
		cor_matrix = pl.corrcoef(data_set, rowvar = 0)

		return train_dict, cor_matrix

#P(Yi)
def compute(total_num, train_dict):
	if total_num > 0:
		for key in train_dict.keys():
			#*****************maybe can fix this equation by (+1) / (+M)************#
			train_dict[key]['pro'] = float(train_dict[key]['nums']) / (total_num)

def save(train_dict, save_file):
	dump_file = file(save_file, "w")
	pickle.dump(train_dict, dump_file)
	dump_file.close()
			
def predict(test_row, train_dict, size):
	if len(test_row) == size:
		max_pro = 0
		label = -1
		probability = []
		#0 2 4 6 ...
		for Yi in train_dict.keys():
			yi_probability = []
			total_pro = train_dict[Yi]['pro'] #Yi_pro
			yi_probability.append(total_pro)
			#'a0' 'a1' 'a2' ...
			for aj in train_dict[Yi]['ais'].keys():
				aj_total = 0
				#0 2 4 6 ...
				for key in train_dict[Yi]['ais'][aj].keys():
					aj_total += train_dict[Yi]['ais'][aj][key]
				#P(aj | Yi)
				#fixed this equation with (+1) / (+M)
				aj_pro = float(train_dict[Yi]['ais'][aj][int(test_row[int(aj[1:])])] + 1) / (aj_total + len(train_dict[Yi]['ais'][aj].keys()))
				yi_probability.append(aj_pro)
				#P(Yi) * ||P(aj | Yi)
				total_pro *= aj_pro
				if total_pro > max_pro:
					max_pro = total_pro
					label = Yi
			probability.append(yi_probability)
		#print probability
		return label
	else:
		return -1

def test(data_set, train_dict, size):
	result = []
	n = 0
	mse = 0.0
	if data_set and len(data_set) > 0:
		for row in data_set:
			if len(row) < size:
				continue
			one_predict = predict(row[0:-1], train_dict, size)
			n += 1
			minus = one_predict - int(row[size])
			mse += (float(minus) / 100) ** 2
			if abs(minus) < ERROR:
				result.append(1)
			else:
				result.append(-1)
	mse /= n
	return result, mse

if __name__ == '__main__':
	#data_file = 'data' + os.sep + '10.152.9.165_bayes_' + str(ATTR_TIME_WINDOW) + '_' + str(MERGE_NUM) + '_' + str(LABEL_DISTANCE) + '.csv'
	#prepare_data_1('10.152.9.165.csv', data_file)
	#data_file = 'data' + os.sep + '10.152.9.165_bayes_' + str(BEFORE) + '_' + str(LABEL_DISTANCE) + '_' + str(ATTR_NUM) + '_1.csv'
	#prepare_data_2('10.152.9.165.csv', data_file)
	data_file = 'data' + os.sep + '10.152.9.165_bayes_' + str(BEFORE) + '_' + str(LABEL_DISTANCE) + '_1.csv'
	prepare_data_3('10.152.9.165.csv', data_file)
	
	Ai_list = []
	Yi_list = []
	#**************FOR (1) AND (2)**************************#
	for i in range(0, 100 + LABEL_DISTANCE, LABEL_DISTANCE):
	#	Ai_list.append(i)
		Yi_list.append(i)
	#**************FOR (1) AND (2)**************************#

	#**************FOR (3)**************************#
	for i in range(-100, 100 + LABEL_DISTANCE):
		Ai_list.append(i)
	#**************FOR (3)**************************#

	train_dict, cor_matrix = train(data_file, Ai_list, Yi_list, FEATURE_NUM)
	stamp = time.time()
	#save(train_dict, "bayes_" + str(stamp) + ".mod")
	
	data_set = []
	fp = open(data_file)
	reader = csv.reader(fp)
	for row in reader:
		#**************FOR (1) AND (2)**************************#
		#if row and len(row) > 0 and row.count('-' + str(LABEL_DISTANCE)) == 0:
		#**************FOR (1) AND (2)**************************#
		#**************FOR (3)**************************#
		if row and len(row) > 0:
		#**************FOR (3)**************************#
			data_set.append(row)
	fp.close()
	result, mse = test(data_set, train_dict, FEATURE_NUM)
	print "Corrcoef:"
	print cor_matrix
	print "Precision within the error:", float(result.count(1)) / len(result)
	print "MSE:", mse

	#write the result to file
	#fp = open("bayes_result" + os.sep + "result_" + str(time) + ".txt", "w")
	#fp.write("Features: first last aver minus")
	#fp.close()
	