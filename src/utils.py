from math import sqrt

def is_prime(num):
	if num<=1:
		return False
	for i in range(2, int(sqrt(num))+1):
		if num%i==0:
			return False
	return True

def modpow(num, power, modulo):
	if power==0:
		return 1
	ans = 1
	rest = num
	while power>0:
		if power&1:
			ans = (ans * rest) % modulo
		rest = (rest * rest) % modulo
		power >>= 1
	return ans

def invmod(num, modulo):
	return modpow(num, modulo-2, modulo)