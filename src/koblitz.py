from .point import Point
from .utils import modpow

def encode_char(curve, char, var):
	num = int(char)
	x = num * var + 1
	y = curve.solve(x)
	while y == None:
		x += 1
		y = curve.solve(x)
	return Point(x, y, curve.modulo)

def encode(curve, string, var):
	return [encode_char(curve, char, var) for char in string]

def decode_point(point, var):
	m = (point.absis - 1) // var
	return m

def decode(arr, var):
	res = ''
	for point in arr:
		res += chr(decode_point(point, var))
	return res