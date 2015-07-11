#!/usr/bin/python
#coding=utf-8

class PrivateVarClass():
	'''
	@__doc__
	python没有真正的私有变量
	内部实现上，是将私有变量进行了转化，
	规则是：
	用__yourPrivateVar来定义私有变量，
	在类外部用_yourClassName__yourPrivateVar来访问私有变量。
	子类遵循父类的访问规则，具体可以用dir()查看某个对象所具有的成员

	'''
	def __init__(self):
		#私有变量
		self.__myprivate = 111

	#在类内部可以直接访问私有变量
	def get_myprivate(self):
		return self.__myprivate

class Child(PrivateVarClass):
	pass

if __name__ == "__main__":
	pri = PrivateVarClass()
	#类外部访问私有变量时需要_ClassName__var格式
	print dir(pri)
	print pri._PrivateVarClass__myprivate
	pri._PrivateVarClass__myprivate = 222
	print pri.get_myprivate()
	#类外部不能直接用私有变量名访问私有变量，会引发一个AttributeError: 
	#print pri.__myprivate
	child = Child()
	print dir(child)
	# 子类中访问父类的私有变量，按照父类的访问规则
	print child._PrivateVarClass__myprivate
	print child.get_myprivate()
