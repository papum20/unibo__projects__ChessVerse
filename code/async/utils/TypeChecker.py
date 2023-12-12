
class TypeChecker:
	"""
	Static class to check types and values
	"""

	@staticmethod
	def isIntInRange(n:int, inf:int, sup:int):
		try:
			return inf <= int(n) <= sup
		except (ValueError, TypeError):
			return False