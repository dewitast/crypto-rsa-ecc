from flask import Flask, render_template, request, send_file
from io import BytesIO
from os import SEEK_END
from random import randrange
from timeit import default_timer
from werkzeug import FileStorage
from sys import byteorder

from src.elliptic_curve import EllipticCurve
from src.koblitz import encode, decode
from src.point import Point
from src.utils import is_prime
from src.rsa import RSAKeyPair, RSAPublicKey, RSAPrivateKey, generate_random_prime, byte_length

MAX_KEY = 1000000

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_file(
        'static/' + filename, attachment_filename=filename, as_attachment=True)

@app.route('/ecc', methods=['GET'])
def ecc():
	return render_template('ecc/index.html')

@app.route('/ecc/encrypt', methods=['GET', 'POST'])
def ecc_encrypt():
	if request.method == 'GET':
		return render_template('ecc/encrypt/index.html')

	message = request.files['message'].read()
	filename = 'encrypted_' + request.files['message'].filename
	kob = int(request.form['koblitz'])

	coef = int(request.form['x-coef'])
	const = int(request.form['const'])
	modulo = int(request.form['modulo'])
	if not is_prime(modulo):
		return "Error: Modulo must be prime"
	curve = EllipticCurve(coef, const, modulo)

	base_x = int(request.form['bpoint-x'])
	base_y = int(request.form['bpoint-y'])
	bpoint = Point(base_x, base_y, modulo)
	if not curve.contains(bpoint):
		return "Error: The base point is not a point in the curve"

	pubkey = request.files.get('pubkey-file', None)
	if pubkey==None:
		pubkey_x = int(request.form['pubkey-x'])
		pubkey_y = int(request.form['pubkey-y'])
		pubkey = Point(pubkey_x, pubkey_y, modulo)
	else:
		pubkey = pubkey.read().decode()
		pubkey = Point(0, 0, modulo, pubkey)
	if not curve.contains(pubkey):
		return "Error: The public key is not a point in the curve"

	plaintext = encode(curve, message, kob)
	start = default_timer()
	k = randrange(1, modulo)
	ciphertext = [curve.add(point, curve.multiply(k, pubkey)) for point in plaintext]
	ciphertext.append(curve.multiply(k, bpoint))
	end = default_timer()
	string = ' '.join([point.print() for point in ciphertext])

	file = FileStorage(stream=BytesIO(string.encode()), filename=filename)
	file.seek(0, SEEK_END)
	size = file.tell()
	file.seek(0)
	file.save('static/' + filename)
	return render_template('ecc/encrypt/result.html', 
				plaintext=message, 
				ciphertext=string, 
				time=end-start, 
				filename=filename, 
				size=size)

@app.route('/ecc/decrypt', methods=['GET', 'POST'])
def ecc_decrypt():
	if request.method == 'GET':
		return render_template('ecc/decrypt/index.html')

	message = request.files['message'].read()
	kob = int(request.form['koblitz'])

	coef = int(request.form['x-coef'])
	const = int(request.form['const'])
	modulo = int(request.form['modulo'])
	if not is_prime(modulo):
		return "Error: Modulo must be prime"
	curve = EllipticCurve(coef, const, modulo)

	prikey = request.files.get('prikey-file', None)
	if prikey==None:
		prikey = int(request.form['prikey'])
	else:
		prikey = int(prikey.read())

	raw_ciphertext = message.decode().split(' ')
	while raw_ciphertext[-1] == '':
		del raw_ciphertext[-1]
	ciphertext = [Point(0, 0, modulo, point) for point in raw_ciphertext]
	start = default_timer()
	point_neg = curve.multiply(prikey, ciphertext[-1])
	del ciphertext[-1]
	point_neg.negate()
	plaintext = [curve.add(point, point_neg) for point in ciphertext]
	end = default_timer()
	string = decode(plaintext, kob)

	filename = request.form['filename']
	file = FileStorage(stream=BytesIO(string), filename=filename)
	file.seek(0, SEEK_END)
	size = file.tell()
	file.seek(0)
	file.save('static/' + filename)
	return render_template('ecc/decrypt/result.html', 
				plaintext=string, 
				ciphertext=message.decode(), 
				time=end-start, 
				filename=filename, 
				size=size
				)

@app.route('/ecc/generate', methods=['GET', 'POST'])
def ecc_generate():
	if request.method == 'GET':
		return render_template('ecc/generate/index.html')

	coef = int(request.form['x-coef'])
	const = int(request.form['const'])
	modulo = int(request.form['modulo'])
	if not is_prime(modulo):
		return "Error: Modulo must be prime"
	curve = EllipticCurve(coef, const, modulo)
	
	base_x = int(request.form['bpoint-x'])
	base_y = int(request.form['bpoint-y'])
	bpoint = Point(base_x, base_y, modulo)
	if not curve.contains(bpoint):
		return "Error: The base point is not a point in the curve"

	private_key = randrange(1, MAX_KEY)
	public_key = curve.multiply(private_key, bpoint)

	filename = request.form['filename']
	public_file = FileStorage(
		stream=BytesIO(public_key.print().encode()),
		filename=filename + '.pub')
	public_file.save('static/' + public_file.filename);
	private_file = FileStorage(
		stream=BytesIO(str(private_key).encode()),
		filename=filename + '.pri')
	private_file.save('static/' + private_file.filename);
	return render_template('ecc/generate/result.html')
	
@app.route('/rsa', methods=['GET'])
def rsa():
	return render_template('rsa/index.html')
	
@app.route('/rsa/encrypt', methods=['GET', 'POST'])
def rsa_encrypt():
	if request.method == 'GET':
		return render_template('rsa/encrypt/index.html')
	
	if request.files['pubkey-file']:
		rsaPublicKey = RSAPublicKey.from_json(request.files['pubkey-file'].read())
	else:
		rsaPublicKey = RSAPublicKey(int(request.form['n']), int(request.form['e']))
		
	start = default_timer()	
		
	n_byte_length = byte_length(rsaPublicKey.n)
	chunk_byte_length = n_byte_length - 1
	if chunk_byte_length <= 0:
		return 'Modulus too small'
	message = request.files['message'].read()
	plaintext = len(message).to_bytes(4, byteorder) + message
	plaintext_chunks = [plaintext[i:i+chunk_byte_length] for i in range(0, len(plaintext), chunk_byte_length)]
	ciphertext = bytes()
	for chunk in plaintext_chunks:
		ciphertext += rsaPublicKey.encrypt(int.from_bytes(chunk, byteorder)).to_bytes(n_byte_length, byteorder)
		
	end = default_timer()
	
	filename = 'encrypted_' + request.files['message'].filename
	ciphertext_file = FileStorage(stream=BytesIO(ciphertext), filename=filename)
	ciphertext_file.seek(0, SEEK_END)
	size = ciphertext_file.tell()
	ciphertext_file.seek(0)
	ciphertext_file.save('static/' + filename)
	
	return render_template('rsa/encrypt/result.html', 
				plaintext=message, 
				ciphertext=ciphertext, 
				time=end-start, 
				filename=filename, 
				size=size
				)

@app.route('/rsa/decrypt', methods=['GET', 'POST'])
def rsa_decrypt():
	if request.method == 'GET':
		return render_template('rsa/decrypt/index.html')
		
	if request.files['prikey-file']:
		rsaPrivateKey = RSAPrivateKey.from_json(request.files['prikey-file'].read())
	else:
		rsaPrivateKey = RSAPrivateKey(int(request.form['n']), int(request.form['d']))
		
	start = default_timer()	
		
	n_byte_length = byte_length(rsaPrivateKey.n)
	if n_byte_length <= 1:
		return 'Modulus too small'
	ciphertext = request.files['message'].read()
	ciphertext_chunks = [ciphertext[i:i+n_byte_length] for i in range(0, len(ciphertext), n_byte_length)]
	plaintext = bytes()
	for chunk in ciphertext_chunks:
		plaintext += rsaPrivateKey.decrypt(int.from_bytes(chunk, byteorder)).to_bytes(n_byte_length, byteorder)[:-1]
	plaintext = plaintext[4:int.from_bytes(plaintext[:4], byteorder)+4]
		
	end = default_timer()
	
	filename = 'decrypted_' + request.files['message'].filename
	plaintext_file = FileStorage(stream=BytesIO(plaintext), filename=filename)
	plaintext_file.seek(0, SEEK_END)
	size = plaintext_file.tell()
	plaintext_file.seek(0)
	plaintext_file.save('static/' + filename)
	
	return render_template('rsa/decrypt/result.html', 
				plaintext=plaintext, 
				ciphertext=ciphertext, 
				time=end-start, 
				filename=filename, 
				size=size
				)

@app.route('/rsa/generate', methods=['GET', 'POST'])
def rsa_generate():
	if request.method == 'GET':
		return render_template('rsa/generate/index.html')
	
	rsaKeyPair = RSAKeyPair(int(request.form['p']), int(request.form['q']), int(request.form['e']))
	filename = request.form['filename']
	public_file = FileStorage(stream=BytesIO(rsaKeyPair.public.to_json().encode()), filename=filename + '.pub')
	public_file.save('static/' + public_file.filename)
	private_file = FileStorage(stream=BytesIO(rsaKeyPair.private.to_json().encode()), filename=filename + '.pri')
	private_file.save('static/' + private_file.filename)
	
	return render_template('rsa/generate/result.html')
	
@app.route('/rsa/generateprime', methods=['POST'])
def rsa_generateprime():
	return str(generate_random_prime(int(request.form['bits'])))

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
