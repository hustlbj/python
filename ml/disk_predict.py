from svmutil import *
import csv
import random
import numpy as np
import neurolab as nl
from neurolab import tool
import random

import pickle
import time

from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import SigmoidLayer
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer


ML_TYPE = "neurolab"
#healthy disk
LABEL_1 = 0.9
#failed disk
LABEL_2 = 0.1
#error
ERROR = 0.1
#epochs
EPOCHS = 400

def read_data_from_file(file_name, label_Dim = 1, isDiskID = False, shuffle=False):
	fp = open(file_name)
	label_set = []
	value_set = []
	reader = csv.reader(fp)
	if shuffle:
		print "shuffle"
		all_data = []
		for row in reader:
			row_list = []
			row_list.append(int(row[0]))
			row_list.append(int(row[1]))
			for i in range(2, 14):
				row_list.append(float(row[i]))
			all_data.append(row_list)
		random.shuffle(all_data)
		for row in all_data:
			row_list = []
			#label
			if label_Dim == 1:
				label_set.append(row[1])
			else:
				if row[1] == -1:
					label_set.append([LABEL_2])
				else:
					label_set.append([LABEL_1])
			if isDiskID:
				#ID
				row_list.append(row[0])
			#SMART 
			for i in range(2, 14):
				row_list.append(row[i])
			value_set.append(row_list)
		fp.close()
		return label_set, value_set
	print "sequence"
	for row in reader:
		row_list = []
		#label
		if label_Dim == 1:
			label_set.append(int(row[1]))
		else:
			if int(row[1]) == -1:
				label_set.append([LABEL_2])
			else:
				label_set.append([LABEL_1])
		if isDiskID:
			#ID
			row_list.append(int(row[0]))
		#SMART 
		for i in range(2, 14):
			row_list.append(float(row[i]))
		value_set.append(row_list)
	fp.close()
	return label_set, value_set

def deteRate(realY, preY):
	if len(realY) != len(preY):
		return -1
	else:
		total_failure = realY.count(-1)
		if total_failure == 0:
			return 1
		detect_failure = 0
		for i in range(0, len(realY)):
			if (realY[i] == -1) and (preY[i] == -1):
				detect_failure = detect_failure + 1
		return (detect_failure + 0.0) / total_failure, detect_failure, total_failure

def FAR(realY, preY):
	if len(realY) != len(preY):
		return -1
	else:
		total_good = realY.count(1)
		if total_good == 1:
			return 0
		detect_good_as_failure = 0
		for i in range(0, len(realY)):
			if (realY[i] == 1) and (preY[i] == -1):
				detect_good_as_failure = detect_good_as_failure + 1
		return (detect_good_as_failure + 0.0) / total_good, detect_good_as_failure, total_good

def test(file_name, train_percent = 0.7):
	label_set, data_set = read_data_from_file(file_name)
	train_num = int(len(label_set) * train_percent)

	param = svm_parameter("-c 10")
	prob = svm_problem(label_set[:train_num], data_set[:train_num])
	mod = svm_train(prob, param)
	svm_save_model(file_name[:-4] + ".mod", mod)
	p_labels, p_acc, p_vals = svm_predict(label_set[train_num:], data_set[train_num:], mod)
	print "detection rate:", deteRate(label_set[train_num:], p_labels)
	print "FAR:", FAR(label_set[train_num:], p_labels)

def test_neurolab(training_file, test_file):
	
	training_label_set, training_data_set = read_data_from_file(training_file, label_Dim = 2, isDiskID = False, shuffle = True)
	bp_net = nl.net.newff([[-1, 1], [-1, 1], [-1, 1], [-1, 1], [-1, 1], [-1, 1], [-1, 1], \
		[-1, 1], [-1, 1], [-1, 1], [-1, 1], [-1, 1]], [12, 20, 1])
	stamp = int(time.time())

	save_file = "init_neur_model-" + str(stamp) + ".mod"
	bp_net.save(save_file)

	bp_net.train(np.array(training_data_set), np.array(training_label_set), epochs = EPOCHS, show = 1, goal = ERROR)

	save_file = "final_neur_model-" + str(stamp) + ".mod"
	bp_net.save(save_file)

	del training_label_set 
	del training_data_set

	#bp_net = tool.load(save_file)
	testing_label_set, testing_data_set = read_data_from_file(test_file, label_Dim = 2, isDiskID = True, shuffle = False)

	result = {}
	
	#label: [[0.1], [0.1], ..., [0.9], [0.9]]
	for i in range(0, len(testing_label_set)):
		row = []
		disk_id = testing_data_set[i][0]
		if not result.has_key(disk_id):
			result[disk_id] = {}
			result[disk_id]["label"] = testing_label_set[i][0]
			result[disk_id]["len"] = 1
			#tmp_y = testing_label_set[i][0]
			tmp_x = testing_data_set[i][1:]
			row.append(tmp_x)

			predict = bp_net.sim(row)

			result[disk_id]["p_label"] = predict[0][0]
			result[disk_id]["check_num"] = 1
		else:
			result[disk_id]["len"] += 1
			#predict is closer to LABEL_2, falied disk
			if abs(result[disk_id]["p_label"] - LABEL_2) <= ERROR:
				pass
			else:
				#tmp_y = testing_label_set[i][0]
				tmp_x = testing_data_set[i][1:]
				row.append(tmp_x)

				predict = bp_net.sim(row)

				result[disk_id]["check_num"] += 1
				result[disk_id]["p_label"] = predict[0][0]
	del testing_label_set
	del testing_data_set
	return result

def test_pybrain(training_file, testing_file):
	training_label_set, training_data_set = read_data_from_file(training_file, label_Dim = 2, isDiskID = False, shuffle = False)
	net = buildNetwork(12, 20, 1, hiddenclass=SigmoidLayer, outclass=SigmoidLayer)
	stamp = int(time.time())
	dump_file = file("init_pybrain_model-" + str(stamp) + ".mod", "w")
	pickle.dump(net, dump_file)
	dump_file.close()
	ds = SupervisedDataSet(12, 1)
	for i in range(0, len(training_data_set)):
		ds.addSample(training_data_set[i], training_label_set[i])

	trainer = BackpropTrainer(net, ds, learningrate=0.1, verbose=True)
	#trainer.train()
	trainer.trainEpochs(epochs=400)
	dump_file = file("final_pybrain_model-" + str(stamp) + ".mod", "w")
	pickle.dump(net, dump_file)
	dump_file.close()
	#trainer.trainUntilConvergence()
	del training_label_set 
	del training_data_set

	#bp_net = tool.load(save_file)
	testing_label_set, testing_data_set = read_data_from_file(testing_file, label_Dim = 2, isDiskID = True, shuffle = False)

	result = {}
	
	#label: [[0.1], [0.1], ..., [0.9], [0.9]]
	for i in range(0, len(testing_label_set)):
		#row = []
		disk_id = testing_data_set[i][0]
		if not result.has_key(disk_id):
			result[disk_id] = {}
			result[disk_id]["label"] = testing_label_set[i][0]
			result[disk_id]["len"] = 1
			#tmp_y = testing_label_set[i][0]
			tmp_x = testing_data_set[i][1:]
			#row.append(tmp_x)

			predict = net.activate(tmp_x)

			result[disk_id]["p_label"] = predict[0]
			result[disk_id]["check_num"] = 1
		else:
			result[disk_id]["len"] += 1
			#predict is closer to LABEL_2, falied disk
			if abs(result[disk_id]["p_label"] - LABEL_2) <= ERROR:
				pass
			else:
				#tmp_y = testing_label_set[i][0]
				tmp_x = testing_data_set[i][1:]
				#row.append(tmp_x)

				predict = net.activate(tmp_x)

				result[disk_id]["check_num"] += 1
				result[disk_id]["p_label"] = predict[0]
	del testing_label_set
	del testing_data_set
	return result

		
def test_svm(training_file, test_file):
	print int(C_SVC), int(RBF)
	#params: svm_type=C_SVC, kernel_type=RBF, C=10, weight_label=[+1, -1], weight=[1, 2]
	param = svm_parameter("-s 0 -t 2 -c 10 -w+1 4 -w-1 1")
	training_label_set, training_data_set = read_data_from_file(training_file)
	prob = svm_problem(training_label_set, training_data_set)
	mod = svm_train(prob, param)
	svm_save_model(training_file[10:-4] + ".mod", mod)

	testing_label_set, testing_data_set = read_data_from_file(test_file, label_Dim = 1, isDiskID = True)
	result = {}
	for i in range(0, len(testing_label_set)):
		tmp_y = []
		tmp_x = []
		disk_id = testing_data_set[i][0]
		if not result.has_key(disk_id):
			result[disk_id] = {}
			result[disk_id]["label"] = testing_label_set[i]
			result[disk_id]["len"] = 1
			tmp_y.append(testing_label_set[i])
			tmp_x.append(testing_data_set[i][1:])
			p_label, p_acc, p_val = svm_predict(tmp_y, tmp_x, mod)
			result[disk_id]["p_label"] = p_label[0]
			result[disk_id]["check_num"] = 1
		else:
			result[disk_id]["len"] += 1
			if result[disk_id]["p_label"] == -1:
				pass
			else:
				tmp_y.append(testing_label_set[i])
				tmp_x.append(testing_data_set[i][1:])
				p_label, p_acc, p_val = svm_predict(tmp_y, tmp_x, mod)
				result[disk_id]["check_num"] += 1
				result[disk_id]["p_label"] = p_label[0]
	return result

def stat_result_svm(result):
	failed_disk_num = 0
	good_disk_num = 0
	p_failed_true = 0
	p_failed_false = 0
	aver_check_num = 0
	aver_lead_time = 0
	lead_time_list = []
	for key in result.keys():
		if result[key]["label"] == 1:
			good_disk_num += 1
			if result[key]["p_label"] == -1:
				p_failed_false += 1
		else:
			failed_disk_num += 1
			if result[key]["p_label"] == -1:
				p_failed_true += 1
				aver_check_num += result[key]["check_num"]
				lead_time_list.append(result[key]["len"] - result[key]["check_num"])
				aver_lead_time += result[key]["len"] - result[key]["check_num"]
	if p_failed_true != 0:	
		aver_check_num = (aver_check_num + 0.0) / p_failed_true
		aver_lead_time = (aver_lead_time + 0.0) / p_failed_true
	else:
		aver_check_num = -1
		aver_lead_time = -1

	return failed_disk_num, good_disk_num, p_failed_true, p_failed_false, aver_check_num, aver_lead_time, lead_time_list

def stat_result_neuro(result):
	failed_disk_num = 0
	good_disk_num = 0
	p_failed_true = 0
	p_failed_false = 0
	aver_check_num = 0
	aver_lead_time = 0
	lead_time_list = []
	for key in result.keys():
		if abs(result[key]["label"] - LABEL_1) <= ERROR:
			good_disk_num += 1
			#good disk is predicted as failed disk
			if abs(result[key]["p_label"] - LABEL_2) <= ERROR:
				p_failed_false += 1
		else:
			failed_disk_num += 1
			#failed disk is predicted as failed disk
			if abs(result[key]["p_label"] - LABEL_2) <= ERROR:
				p_failed_true += 1
				aver_check_num += result[key]["check_num"]
				lead_time_list.append(result[key]["len"] - result[key]["check_num"])
				aver_lead_time += result[key]["len"] - result[key]["check_num"]
	if p_failed_true != 0:
		aver_check_num = (aver_check_num + 0.0) / p_failed_true
		aver_lead_time = (aver_lead_time + 0.0) / p_failed_true
	else:
		aver_check_num = -1
		aver_lead_time = -1

	return failed_disk_num, good_disk_num, p_failed_true, p_failed_false, aver_check_num, aver_lead_time, lead_time_list

def stat_lead_time(lead_time_list):
	lead_time_dict = {"0-50":0, "50-100":0, "100-150":0, "150-200":0, "200-250":0, "250-300":0, \
		"300-350":0, "350-400":0, "400-450":0, "450-500":0, "500-":0}
	for item in lead_time_list:
		if item >= 0 and item < 50:
			lead_time_dict["0-50"] += 1
		elif item >= 50 and item < 100:
			lead_time_dict["50-100"] += 1
		elif item >= 100 and item < 150:
			lead_time_dict["100-150"] += 1
		elif item >= 150 and item < 200:
			lead_time_dict["150-200"] += 1
		elif item >= 200 and item < 250:
			lead_time_dict["200-250"] += 1	
		elif item >= 250 and item < 300:
			lead_time_dict["250-300"] += 1
		elif item >= 300 and item < 350:
			lead_time_dict["300-350"] += 1
		elif item >= 350 and item < 400:
			lead_time_dict["350-400"] += 1
		elif item >= 400 and item < 450:
			lead_time_dict["400-450"] += 1
		elif item >= 450 and item < 500:
			lead_time_dict["450-500"] += 1
		else:
			lead_time_dict["500-"] += 1
	return lead_time_dict

if  __name__ == "__main__":
	training_file = r"trainging_part_before_12h_to_now_choose.txt"
	testing_file = r"testing_part_before_12h_to_now_all.txt"

	#svm method
	'''
	result = test_svm(training_file, testing_file)
	failed_disk_num, good_disk_num, p_failed_true, p_failed_false, aver_check_num, aver_lead_time, lead_time_list = stat_result_svm(result)
	lead_time_dict = stat_lead_time(lead_time_list)
	print "failed_disk_num:", failed_disk_num, "good_disk_num:", good_disk_num
	print "p_failed_true:", p_failed_true, "p_failed_false:", p_failed_false
	print "Detection Rate:", (p_failed_true + 0.0) / failed_disk_num
	print "False Alarm Rate:", (p_failed_false + 0.0) / good_disk_num
	print "Aver leading time:", aver_lead_time, "aver check num:", aver_check_num
	print "Detail lead time:", lead_time_dict
	'''
	#neuro method
	'''
	result = test_neurolab(training_file, testing_file)
	failed_disk_num, good_disk_num, p_failed_true, p_failed_false, aver_check_num, aver_lead_time, lead_time_list = stat_result_neuro(result)
	lead_time_dict = stat_lead_time(lead_time_list)
	print "failed_disk_num:", failed_disk_num, "good_disk_num:", good_disk_num
	print "p_failed_true:", p_failed_true, "p_failed_false:", p_failed_false
	print "Detection Rate:", (p_failed_true + 0.0) / failed_disk_num
	print "False Alarm Rate:", (p_failed_false + 0.0) / good_disk_num
	print "Aver leading time:", aver_lead_time, "aver check num:", aver_check_num
	print "Detail lead time:", lead_time_dict
	'''
	#pybrain
	result = test_pybrain(training_file, testing_file)
	failed_disk_num, good_disk_num, p_failed_true, p_failed_false, aver_check_num, aver_lead_time, lead_time_list = stat_result_neuro(result)
	lead_time_dict = stat_lead_time(lead_time_list)
	print "failed_disk_num:", failed_disk_num, "good_disk_num:", good_disk_num
	print "p_failed_true:", p_failed_true, "p_failed_false:", p_failed_false
	print "Detection Rate:", (p_failed_true + 0.0) / failed_disk_num
	print "False Alarm Rate:", (p_failed_false + 0.0) / good_disk_num
	print "Aver leading time:", aver_lead_time, "aver check num:", aver_check_num
	print "Detail lead time:", lead_time_dict