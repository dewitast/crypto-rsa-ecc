from flask import Flask, render_template, request

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

	return render_template('ecc/index.html')

@app.route('/ecc/decrypt', methods=['GET', 'POST'])
def ecc_decrypt():
	if request.method == 'GET':
		return render_template('ecc/decrypt.html')

	return render_template('ecc/index.html')

@app.route('/ecc/generate', methods=['GET', 'POST'])
def ecc_generate():
	if request.method == 'GET':
		return render_template('ecc/generate.html')

	return render_template('ecc/index.html')

@app.route('/rsa', methods=['GET'])
def rsa():
	return render_template('rsa/index.html')

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
