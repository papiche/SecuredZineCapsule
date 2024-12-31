import pysodium
import qrcode
import pyotp
import base64
import os
import json
from flask import Flask, request, jsonify, send_file
import io
import zipfile

app = Flask(__name__)

# Configuration
SECRET_KEY_ENV = "ZINE_KEY"
ZINE_PASSWORD_FILE = "zine_passwords.json" # Stockage des hachage de mots de passe, pour la récupération
SALT_SIZE = pysodium.crypto_pwhash_SALTBYTES
KEY_SIZE = pysodium.crypto_secretbox_KEYBYTES

#Fonction utilitaire
def generate_nonce():
    return pysodium.randombytes(pysodium.crypto_secretbox_NONCEBYTES)

def hash_password(password, salt=None):
    if salt is None:
        salt = pysodium.randombytes(SALT_SIZE)
    hash = pysodium.crypto_pwhash_scryptsalsa208sha256(
        KEY_SIZE, password.encode(), salt, 10, 15674, 2
    )
    return base64.b64encode(hash).decode(), base64.b64encode(salt).decode()

# Fonction utilitaire pour charger les mots de passe
def load_passwords():
    if not os.path.exists(ZINE_PASSWORD_FILE):
         return {}
    with open(ZINE_PASSWORD_FILE, 'r') as file:
            return json.load(file)

# Fonction utilitaire pour enregistrer les mots de passe
def save_passwords(passwords):
     with open(ZINE_PASSWORD_FILE, 'w') as file:
            json.dump(passwords, file)

#Fonction utilitaire pour chiffrer
def encrypt_zip(zip_buffer, key, nonce):
    return pysodium.crypto_secretbox(zip_buffer, nonce, key)

# Route de génération du Zine sécurisé
@app.route("/generate_zine", methods=["POST"])
def generate_zine():
    try:
        data = request.get_json()
        # Les contenu du zine et le mot de passe du zine sont envoyé via le json
        zine_content = data.get("zine_content", "")
        password = data.get("password", "")
        if not zine_content or not password:
                return jsonify({"error": "Zine content or password missing"}), 400

        #Génération du zine en ZIP (temporaire)
        zip_buffer = create_zip_buffer(zine_content)

        #Génération de clés et secret
        secret_key = pysodium.crypto_secretbox_keygen()
        secret_totp = pysodium.randombytes(32)

        #Chiffrement du zip
        nonce = generate_nonce()
        key =  pysodium.crypto_pwhash_scryptsalsa208sha256(KEY_SIZE, password.encode(), pysodium.randombytes(SALT_SIZE), 10, 15674, 2)
        encrypted_zip = encrypt_zip(zip_buffer, key, nonce)

        #Préparation de l'objet de retour
        zine_data = {
                "encryptedZine": base64.b64encode(encrypted_zip).decode(),
                "totpSecret": base64.b64encode(secret_totp).decode(),
                "nonce": base64.b64encode(nonce).decode()
            }


        #Gestion du mot de passe et enregistrement
        passwords = load_passwords()
        password_hash, salt = hash_password(password)
        passwords[password_hash] = { 'salt': salt, 'totp': base64.b64encode(secret_totp).decode()}
        save_passwords(passwords)


        return jsonify(zine_data), 200
    except Exception as e:
           return jsonify({"error": str(e)}), 500


# Route de récupération du secret TOTP pour un mot de passe
@app.route("/recover_secret", methods=["POST"])
def recover_secret():
     data = request.get_json()
     password = data.get("password", "")
     if not password:
            return jsonify({"error": "Password missing"}), 400

     passwords = load_passwords()
     password_hash, _ = hash_password(password)

     if password_hash in passwords:
            return jsonify({"totpSecret": passwords[password_hash]['totp'] }), 200
     else:
          return jsonify({"error": "Password not found"}), 404

def create_zip_buffer(zine_content):
     zip_buffer = io.BytesIO()
     with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_name, content in zine_content.items():
            zf.writestr(file_name, content)

     return zip_buffer.getvalue()


if __name__ == "__main__":
    app.run(debug=True, port=5002)
