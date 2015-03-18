#coding=utf-8
##########################
#  Iterators
##########################
'''
迭代器是一个可以对集合进行迭代访问的对象
如果一个对象定义了__iter__方法，并且此方法返回一个迭代器，那么这个对象就是可迭代的
迭代器是指实现了__iter__以及next（python3中是__next__）两个方法的对象
__iter__方法返回一个迭代对象，一般总是简单的返回self，next方法返回迭代过程的下一个集合元素
避免直接调用对象的__iter__以及next方法，而应该使用for或是列表推导式，或者使用内建函数iter以及next

'''

class count_iterator(object):
	n = 0
	def __iter__(self):
		return self
	def next(self):
		y = self.n
		self.n += 1
		return y
'''
如过一个对象没有__iter__方法但定义了__getitem__方法，那么该对象仍然是可迭代的
使用内建函数iter将会返回一个该对象的迭代器类型
如果StopIteration或者IndexError异常被抛出，则迭代停止
'''
class SimpleList(object):
	def __init__(self, *items):
		self.items = items
	def __getitem__(self, i):
		return self.items[i]
'''
根据初始条件使用迭代器生成Hofstadter Q序列
Q(n) = Q(n-Q(n-1)) + Q(n-Q(n-2))
'''
class QSequence(object):
	def __init__(self, s):
		self.s = s
	def next(self):
		try:
			#n-x实际上在列表中就是倒序的x，所以可以直接省略n
			q = self.s[-self.s[-1]] + self.s[-self.s[-2]]
			self.s.append(q)
			return q
		except IndexError:
			raise StopIteration()
	def __iter__(self):
		return self
	def current_state(self):
		return self.s


if __name__ == "__main__":
	counter = count_iterator()
	print next(counter)
	print next(counter)

	simple = SimpleList(1, 2, 3)
	it = iter(simple)
	print next(it)
	print next(it)

	Q = QSequence([1, 1])
	print [next(Q) for __ in xrange(10)]