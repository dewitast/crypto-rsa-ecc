import random
import pickle

class RSAKeyPair:
	def __init__ (self, p, q, e):
		phi = (p - 1) * (q - 1)
		n = p * q
		if extended_gcd(e, phi)[0] != 1:
			raise Exception('Public exponent and phi are not coprimes')
		d = modular_inverse(e, phi)
		self.public = RSAPublicKey(n, e)
		self.private = RSAPrivateKey(n, d)

class RSAPublicKey:
	def __init__ (self, n, e):
		self.n = n
		self.e = e
		
	def encrypt (self, plaintext):
		return pow(plaintext, self.e, self.n)
		
	def write_file (self, filename):
		with open(filename, 'wb') as f:
			pickle.dump((self.n, self.e), f)
	
	@classmethod
	def read_file (cls, filename):
		with open(filename, 'rb') as f:
			return cls(*pickle.load(f))
		
class RSAPrivateKey:
	def __init__ (self, n, d):
		self.n = n
		self.d = d
		
	def decrypt (self, ciphertext):
		return pow(ciphertext, self.d, self.n)
		
	def write_file (self, filename):
		with open(filename, 'wb') as f:
			pickle.dump((self.n, self.d), f)
	
	@classmethod		
	def read_file (cls, filename):
		with open(filename, 'rb') as f:
			return cls(*pickle.load(f))

		
SMALL_PRIMES = [
    3, 5, 7, 11, 13, 17, 19,
    23, 29, 31, 37, 41, 43, 47, 53,
    59, 61, 67, 71, 73, 79, 83, 89,
    97, 101, 103, 107, 109, 113, 127, 131,
    137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199, 211, 223,
    227, 229, 233, 239, 241, 251, 257, 263,
    269, 271, 277, 281, 283, 293, 307, 311,
    313, 317, 331, 337, 347, 349, 353, 359,
    367, 373, 379, 383, 389, 397, 401, 409,
    419, 421, 431, 433, 439, 443, 449, 457,
    461, 463, 467, 479, 487, 491, 499, 503,
    509, 521, 523, 541, 547, 557, 563, 569,
    571, 577, 587, 593, 599, 601, 607, 613,
    617, 619, 631, 641, 643, 647, 653, 659,
    661, 673, 677, 683, 691, 701, 709, 719,
    727, 733, 739, 743, 751, 757, 761, 769,
    773, 787, 797, 809, 811, 821, 823, 827,
    829, 839, 853, 857, 859, 863, 877, 881,
    883, 887, 907, 911, 919, 929, 937, 941,
    947, 953, 967, 971, 977, 983, 991, 997
]

def is_probable_prime (n, k=10):
	if n < 2:
		return False
	for prime in SMALL_PRIMES:
		if n == prime:
			return True
	r = 0
	s = n - 1
	while s & 1 == 0:
		r += 1
		s >>= 1
	for _ in range(k):
		a = random.randrange(2, n - 2)
		x = pow(a, s, n)
		if x == 1 or x == n - 1:
			continue
		for _ in range(r - 1):
			x = pow(x, 2, n)
			if x == n - 1:
				break
		else:
			return False
	return True
	
def generate_random_prime(bits):
	n = random.randrange(3, 1 << bits)
	n |= 1
	while not is_probable_prime(n):
		n += 2
	return n

def extended_gcd(a, b):
	if a == 0:
		return (b, 0, 1)
	else:
		g, y, x = extended_gcd(b % a, a)
		return (g, x - (b // a) * y, y)

def modular_inverse(a, m):
	g, x, _ = extended_gcd(a, m)
	if g != 1:
		raise Exception('not invertable')
	else:
		return x % m
		
def main ():
	rsaKeyPair = RSAKeyPair(generate_random_prime(1024), generate_random_prime(1024), 65537)
	plaintext = 3
	ciphertext = rsaKeyPair.public.encrypt(plaintext)
	result = rsaKeyPair.private.decrypt(ciphertext)
	print(plaintext)
	print(ciphertext)
	print(result)
	
if __name__ == '__main__':
	main()

