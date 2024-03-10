from flask import Flask, request, render_template
from PIL import Image

# Note: static folder means all files from there will be automatically served over HTTP
app = Flask(__name__, static_folder="public")

message = ''

@app.route("/")
@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/")
@app.route("/encode.html", methods=["GET", "POST"])
def encode():
    return render_template("encode.html")

@app.route("/")
@app.route("/decode.html", methods=["GET", "POST"])
def decode():
    return render_template("decode.html")

def encode_lsb(image_path, message):
    image = Image.open(image_path)
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    binary_message += '1111111111111111'
    pixels = image.load()
    width, height = image.size
    index = 0
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            r = (r & 0xFE) | int(binary_message[index])
            index += 1
            if index >= len(binary_message):
                image.save("./public/images/encoded_image.png")
                return   
            g = (g & 0xFE) | int(binary_message[index])
            index += 1
            if index >= len(binary_message):
                image.save("./public/images/encoded_image.png")
                return
            b = (b & 0xFE) | int(binary_message[index])
            index += 1
            if index >= len(binary_message):
                image.save("./public/images/encoded_image.png")
                return
            pixels[x, y] = (r, g, b)

@app.route("/")
@app.route('/encode_result.html', methods=['GET', 'POST'])
def encode_result():
    image = request.files['image']
    image.save("./public/images/temp.png")
    message = request.form['message']
    image_path = "./public/images/temp.png"
    encode_lsb(image_path, message)
    return render_template('encode_result.html')

def decode_lsb(image_path):
    image = Image.open(image_path)
    pixels = image.load()
    width, height = image.size
    binary_message = ""
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)
    binary_message = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
    message = ""
    for binary in binary_message:
        decimal = int(binary, 2)
        if decimal == 255:
            break
        message += chr(decimal)
    return message

@app.route("/")
@app.route('/decode_result.html', methods=['GET', 'POST'])
def decode_result():
    image = request.files['image']
    image.save("./public/images/temp.png")
    image_path = "./public/images/temp.png"
    message = decode_lsb(image_path)
    return render_template("decode_result.html", message=message)

# Run the webserver (port 8080)
if __name__ == "__main__":
    app.run(debug=True, port=8080)
