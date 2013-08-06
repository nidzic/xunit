#! pthon

import unittest
import logging

from xunit.utils import exception
from xunit.case import XUnitCase
import types


class LoadModuleError(exception.XUnitException):
	pass

class ClassNotSupportError(exception.XUnitException):
	pass

class XUnitSuiteBase(unittest.TestSuite):
	def __LoadCase(self,mn,cn,fn=None):
		rst = unittest.TestSuite()
		try:
			m = __import__(mn)
			if cn:
				cls = getattr(m,cn)
				if not issubclass(cls,XUnitCase):
					raise ClassNotSupportError('[%s].%s:%s not XUnitCase (%s)'%(mn,cn,fn and fn or '',cls))
				if fn:
					rst.addTest(cls(fn))
				else:
					tests = unittest.loader.TestLoader().loadTestsFromTestCase(cls)
					rst.addTest(tests)
			else:
				# now to get all the 
				cns = dir(m)
				for c in cns:
					cls = getattr(m,c)
					if hasattr(cls,'__class__') :
						try:
							if issubclass(cls,XUnitCase):
								tests = unittest.loader.TestLoader().loadTestsFromTestCase(cls)
								rst.addTest(tests)
						except:
							pass
		except:
			raise LoadModuleError('can not load [%s].%s:%s module'%(mn,cn,fn))
		return rst


	def LoadCase(self,case):
		'''
			case is in the format like module.class:function
			module is the module name
			class is the class name in the modulef
			function is the function name 
		'''
		mcname = case
		fn = None
		if ':' in case:
			mcname,fn = case.split(':')

		kpart = mcname
		rst = None

		if fn is None:
			try:
				# first we test whether it is the whole module to import
				rst = self.__LoadCase(kpart,None,None)
				if rst is not None:
					self.addTests(rst)
					return
			except:
				pass
		while len(kpart) > 0:
			r = kpart.rfind('.')
			if r < 0 :
				break
			mn = mcname[:r]
			cn = mcname[r+1:]
			try:
				rst = self.__LoadCase(mn,cn,fn)
				break
			except LoadModuleError as e :
				kpart = mn

		if rst is None:
			raise LoadModuleError('can not load %s'%(case))
		self.addTests(rst)
		return

	
