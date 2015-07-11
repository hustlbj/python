#coding=utf-8
###########################
#   Generator
###########################
import itertools

'''
生成器内部用到yield表达式，不会使用return返回值，当需要时使用yield表达式返回结果
python的内在机制能够帮助记住当前生成器的上下文，也就是当前的控制流和局部变量的值等
每次生成器被调用都使用yield返回迭代过程中的下一个值，__iter__方法是默认实现的，意味着任何能够使用迭代器的地方都能够使用生成器
'''

def count_generator():
	n = 0
	while True:
		yield n
		n += 1

def qsequence_genetator(s):
	a = s[:]
	while True:
		try:
			q = a[-a[-1]] + a[-a[-2]]
			a.append(q)
			yield q
		except IndexError:
			return
#Collatz序列
def collatz(n):
	yield n
	while n != 1:
		n = n / 2 if n % 2 == 0 else 3 * n + 1
		yield n

'''
生成器可以像其他函数那样递归，简单版本的itertools.permutations
这个生成器通过给定一个item列表生成其全排列
基本思想是：对列表中的每个元素，通过将它与列表第一个元素交换将其放置到第一的位置上去，而后重新递归拍I咧列表的剩余部分
'''
def permutations(items):
	if len(items) == 0:
		yield []
	else:
		pi = items[:]
		for i in xrange(len(pi)):
			pi[0], pi[i] = pi[i], pi[0]
			for p in permutations(pi[1:]):
				yield [pi[0]] + p

if __name__ == "__main__":
	counter = count_generator()
	print next(counter)
	print next(counter)

	print list(collatz(7))

	for p in permutations([1, 2, 3]):
		print p
	'''
	生成器表达式可以让你通过一个简单的单行声明定义生成器，和列表推导式非诚类似
	'''
	g = (x ** 2 for x in itertools.count(1))
	print [g.next() for __ in xrange(10)]