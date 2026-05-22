from flask import Flask, render_template, request, send_from_directory
import os

from sessions import sessions, generate_code
from aes_utils import encrypt_message, decrypt_message
from stego import encode_image, decode_image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/send", methods=["GET"])
def send_page():
    return render_template("send.html")


@app.route("/send", methods=["POST"])
def send_message():
    image = request.files["image"]
    message = request.form["message"]

    code = generate_code()

    original_path = os.path.join(UPLOAD_FOLDER, code + "_original.png")
    encoded_path = os.path.join(UPLOAD_FOLDER, code + "_encoded.png")

    image.save(original_path)

    encrypted = encrypt_message(message)

    encode_image(original_path, encoded_path, encrypted)

    sessions[code] = {
        "filename": code + "_encoded.png"
    }

    return render_template("send.html", code=code)


@app.route("/receive", methods=["GET"])
def receive_page():
    return render_template("receive.html")


@app.route("/receive", methods=["POST"])
def receive_message():
    code = request.form["code"]

    if code in sessions:
        filename = sessions[code]["filename"]
        path = os.path.join(UPLOAD_FOLDER, filename)

        encrypted = decode_image(path)
        message = decrypt_message(encrypted)

        return render_template("receive.html", message=message, filename=filename)

    return render_template("receive.html", error="Invalid OTP")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
