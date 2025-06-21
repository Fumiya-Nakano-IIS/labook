# app.py
# A simple Flask application serving HTTPS with a self-signed certificate
# All comments and messages are in English

from flask import Flask, send_file, send_from_directory
import os

app = Flask(__name__)


# Serve index.html at root
@app.route("/")
def index():
    return send_file("index.html")


@app.route("/<path:filename>")
def root_files(filename):
    return send_from_directory(os.path.dirname(__file__), filename)


if __name__ == "__main__":
    # Paths to the certificate and key files
    base_dir = os.path.dirname(__file__)
    cert_file = os.path.join(base_dir, "localhost+3.pem")
    key_file = os.path.join(base_dir, "localhost+3-key.pem")

    # Check that certificate files exist
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        raise FileNotFoundError(
            "Certificate files not found. Please generate cert.pem and key.pem first."
        )

    # Run Flask app with SSL context
    # Use debug=False in production-like setups
    app.run(host="0.0.0.0", port=5000, ssl_context=(cert_file, key_file), debug=True)
