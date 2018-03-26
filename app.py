from flask import Flask, render_template, request, send_file
from io import BytesIO
from random import randrange
from werkzeug import FileStorage

from src.elliptic_curve import EllipticCurve
from src.koblitz import encode, decode
from src.point import Point
from src.utils import is_prime

MAX_KEY = 1000000

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@app.route('/ecc', methods=['GET'])
def ecc():
	return render_template('ecc/index.html')

@app.route('/ecc/encrypt', methods=['GET', 'POST'])
def ecc_encrypt():
	if request.method == 'GET':
		return render_template('ecc/encrypt.html')


	message = request.files['message'].read()
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

	pubkey_x = int(request.form['pubkey-x'])
	pubkey_y = int(request.form['pubkey-y'])
	pubkey = Point(pubkey_x, pubkey_y, modulo)
	if not curve.contains(pubkey):
		return "Error: The public key is not a point in the curve"

	plaintext = encode(curve, message, kob)
	k = randrange(1, modulo)
	ciphertext = [curve.add(point, curve.multiply(k, pubkey)) for point in plaintext]
	ciphertext.append(curve.multiply(k, bpoint))
	string = ''
	for point in ciphertext:
		string += point.print() + ' '

	file = FileStorage(stream=BytesIO(string.encode()), filename='ciphertext.txt')
	return send_file(file, attachment_filename=file.filename, as_attachment=True)

@app.route('/ecc/decrypt', methods=['GET', 'POST'])
def ecc_decrypt():
	if request.method == 'GET':
		return render_template('ecc/decrypt.html')

	return render_template('ecc/index.html')

@app.route('/ecc/generate', methods=['GET', 'POST'])
def ecc_generate():
	if request.method == 'GET':
		return render_template('ecc/generate.html')

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
	return "Success"

@app.route('/rsa', methods=['GET'])
def rsa():
	return render_template('rsa/index.html')

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
