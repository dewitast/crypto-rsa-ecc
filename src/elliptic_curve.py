from .point import Point
from .utils import invmod, modpow

INF = Point(0, 0, -1)

class EllipticCurve:
	def __init__(self, coef, const, modulo):
		self.modulo = modulo
		self.coef = coef % self.modulo
		if self.coef<0:
			self.coef += self.modulo
		self.const = const % self.modulo
		if self.const:
			self.const += self.modulo

	def contains(self, point):
		lhs = (point.ordinat ** 2) % self.modulo
		rhs = (point.absis ** 3) % self.modulo
		rhs %= self.modulo
		rhs += (point.absis * self.coef) % self.modulo
		rhs %= self.modulo
		rhs += self.const
		rhs %= self.modulo
		return (rhs==lhs)

	def gradient(self, point):
		dx = (3 * point.absis * point.absis + self.coef) % self.modulo
		dy = (point.ordinat + point.ordinat) % self.modulo
		if dy==0:
			return None
		dy = invmod(dy, self.modulo)
		return (dx * dy) % self.modulo

	def add(self, point1, point2):
		if point1.equal(point2):
			return square(point1)
		if point1.is_inf():
			return point2
		if point2.is_inf():
			return point1
		grad = point1.gradient(point2)
		if grad == None:
			return INF
		absis = (grad * grad - point1.absis - point2.absis) % self.modulo
		if absis<0:
			absis += self.modulo
		ordinat = (grad * (point1.absis - absis) - point1.ordinat) % self.modulo
		if ordinat<0:
			ordinat += self.modulo
		return Point(absis, ordinat, self.modulo)

	def square(self, point):
		if point.is_inf():
			return point
		grad = self.gradient(point)
		if grad == None:
			return INF
		absis = (grad * grad - point.absis - point.absis) % self.modulo
		if absis<0:
			absis += self.modulo
		ordinat = (grad * (point.absis - absis) - point.ordinat) % self.modulo
		if ordinat<0:
			ordinat += self.modulo
		return Point(absis, ordinat, self.modulo)

	def multiply(self, k, point):
		ans = INF
		rest = point
		while k>0:
			if k&1:
				ans = self.add(ans, rest)
			rest = self.square(rest)
			k >>= 1
		return ans

	def solve(self, x):
		rhs = (x*x*x+x*self.coef+self.const) % self.modulo
		if self.modulo==2:
			return rhs
		if modpow(rhs, (self.modulo - 1) // 2, self.modulo) != 1:
			return None
		ans = 0
		while (ans * ans) % self.modulo != rhs:
			ans += 1
		return ans

	def print(self):
		res = "y^2 = x^3 + " + str(self.coef) + "x + " + str(self.const) + " mod " + str(self.modulo)
		return res