from .utils import invmod

class Point:
	def __init__(self, absis, ordinat, modulo, string = None):
		if string != None:
			spl = string.split(',')
			absis = spl[0]
			ordinat = spl[1]
			self.absis = int(absis[1:])
			self.ordinat = int(ordinat[:-1])
			self.modulo = modulo
			return
		self.modulo = modulo
		self.absis = absis % self.modulo
		if self.absis<0:
			self.absis += self.modulo
		self.ordinat = ordinat % self.modulo
		if self.ordinat<0:
			self.ordinat += self.modulo

	def negate(self):
		self.ordinat = (self.modulo - self.ordinat) % self.modulo
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
		return (dy * invmod(dx, self.modulo)) % self.modulo

	def equal(self, point):
		return self.absis == point.absis and self.ordinat == point.ordinat and self.modulo == point.modulo

	def is_inf(self):
		return self.modulo == -1

	def print(self):
		res = "(" + str(self.absis) + "," + str(self.ordinat) + ")"
		return res