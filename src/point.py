from .utils import invmod

class Point:
	def __init__(self, absis, ordinat, modulo):
		self.modulo = modulo
		self.absis = absis % self.modulo
		if self.absis<0:
			self.absis += self.modulo
		self.ordinat = ordinat % self.modulo
		if self.ordinat<0:
			self.ordinat += self.modulo

	def negate(self):
		if self.ordinat<0:
			self.absis = self.modulo - self.absis
		return self

	def gradient(self, point):
		dx = (self.absis - point.absis) % self.modulo
		if dx<0:
			dx += self.modulo
		dy = (self.ordinat - point.ordinat) % self.modulo
		if dy<0:
			dy += self.modulo
		if dx==0:
			return None
		dx = invmod(dx, self.modulo)
		return (dy * dx) % self.modulo

	def equal(self, point):
		return self.absis == point.absis and self.ordinat == point.ordinat and self.modulo == point.modulo

	def is_inf(self):
		return self.modulo == -1

	def print(self):
		res = "(" + str(self.absis) + ", " + str(self.ordinat) + ")"
		return res