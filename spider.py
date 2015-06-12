#!/usr/bin/python
#coding=utf-8
# python 2.7

from abc import ABCMeta, abstractmethod
import urllib2
import re
import pickle

class Spider():
	'''
	@__doc__
	定义抽象类 __metaclass__ = ABCMeta
	不能被实例化，如果试图实例化，则会报出TypeError: Can't instantiate abstract class
	子类必须实现的抽象方法fetch()和parse()
	'''
	__metaclass__ = ABCMeta

	def __init__(self, url, decoding, regex = ""):
		self.__url = url
		self.__regex = regex
		self.decoding = decoding
		self.content = None

	def set_url(self, url):
		self.__url = url

	def get_url(self):
		return self.__url

	def set_regex(self, regex):
		self.__regex = regex

	def get_regex(self):
		return self.__regex

	def get_content(self):
		return self.content

	@abstractmethod
	def fetch(self):
		pass

	@abstractmethod
	def parse(self):
		pass

	@abstractmethod
	def output(self):
		pass

class StaticSpider(Spider):
	'''
	@__doc__
	如果子类继承了一个抽象父类，则必须实现抽象父类中的抽象方法
	否则会报出TypeError: Can't instantiate abstract class StaticSpider with abstract methods fetch, parse
	如果子类没有构造方法，则会默认去调用父类的构造方法
	如果子类有构造方法，若想调用父类构造方法则需要在子类自己的__init__()中显式调用super.__init__()
	'''
	def fetch(self):
		self.content = urllib2.urlopen(self.get_url()).read()
		self.content = self.content.decode(self.decoding).encode('utf-8')
		#print self.content

	def parse(self):
		#http://regexpal.com/ 测试正则表达式  \u4e00-\u9fa5匹配汉字
		# 取出第一个table中的内容，用str.split("分割串")来分割原始串
		self.content = self.content.split("<table")[2]
		REGEX = r"\'>([^<]+)</a></td>" #匹配“'>中海可转债债券A(000003)</a></td>”
		pattern = re.compile(REGEX)
		#match = pattern.match(self.content) # The result is None, why?
		match = pattern.findall(self.content)
		print len(match)
		funds = []
		for row in match:
			# 多个候选分割字符，使用re.split
			items = re.split(r'\(|\)', row)
			if len(items) > 2 and items[0] != '' and items[-2] != '':
				# http://hq.sinajs.cn/list=of110028
				# var hq_str_of110028="易方达安心回报债券B,1.857,2.362,1.853,0.22,2015-06-10";
				response = urllib2.urlopen('http://hq.sinajs.cn/list=of' + items[-2]).read()
				values = re.split('="|,|"', response)
				if len(values) > 6:
					funds.append({"name": items[0], "code": items[-2], "values": [values[2], values[3], values[4], values[5]], 'date': values[6]})
		print len(funds)
		meta_file = open('funds.meta', 'wb')
		pickle.dump(funds, meta_file)
		meta_file.close()
		print 'funds > funds.meta'

	def output(self):
		pass

if __name__ == "__main__":
	URL = r"http://money.finance.sina.com.cn/fund/view/vNewFund_FundListings.php"
	DECODING = 'gbk';
	#想要匹配的子串<td><a href='http://biz.finance.sina.com.cn/suggest/lookup_n.php?q=000003&country=fund' target='_blank' title='中海可转债债券A(000003)'>中海可转债债券A(000003)</a></td>
	#REGEX = r"<td><a\shref=\'(.*)\'\s[.*]\stitle=\'(*.)\'>.*</a></td>"
	
	spider = StaticSpider(URL, DECODING)
	spider.fetch()
	spider.parse()
	
