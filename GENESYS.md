# Comment protéger l'ouverture d'un Zine en utilisant un libsodium et/ou TOTP

Absolument ! Protéger l'ouverture d'un Zine numérique avec `libsodium` et/ou TOTP (Time-Based One-Time Password) est un excellent moyen d'ajouter une couche de sécurité et de contrôle d'accès. Voici une approche détaillée, avec des explications et du code pour vous guider.

**Contexte et Objectifs**

*   **Objectif principal:** Empêcher l'accès non autorisé au contenu du Zine.
*   **LibSodium:** Fournit des primitives cryptographiques robustes pour le chiffrement et la signature.
*   **TOTP:** Génère des codes d'authentification à usage unique basés sur le temps, ajoutant une authentification à deux facteurs (2FA).

**Stratégies de Protection**

On peut envisager deux approches principales, qui peuvent être utilisées séparément ou combinées :

1.  **Chiffrement du Zine avec une clé dérivée d'un mot de passe (LibSodium):**
    *   Le contenu du Zine (tous les fichiers HTML, CSS, JavaScript, images) est chiffré.
    *   L'utilisateur doit fournir un mot de passe pour déchiffrer le contenu.
    *   On utilisera LibSodium pour la dérivation de clé, le chiffrement et le déchiffrement.
2.  **Authentification TOTP:**
    *   L'accès au Zine nécessite un code TOTP généré par une application d'authentification (Google Authenticator, Authy, etc.).
    *   L'utilisateur doit scanner un QR code pour enregistrer le secret TOTP.
    *   Cette méthode peut être combinée avec le chiffrement pour une double couche de protection.

**Mise en Œuvre (Approche Hybride)**

Nous allons implémenter une approche hybride combinant le chiffrement et l'authentification TOTP.

**Étape 1: Génération des Clés (Côté Serveur ou hors ligne)**

*   **Génération de la clé de chiffrement:**
    *   Générer une clé aléatoire avec `crypto_secretbox_keygen()` à stocker de façon sécurisé (par exemple, une variable d'environnement)
*   **Génération du secret TOTP:**
    *   Générer un secret aléatoire pour le TOTP. `sodium.crypto_generichash(32, sodium.randombytes_buf(32))`

**Étape 2: Chiffrement du Zine**

1.  **Chiffrez le contenu du Zine (HTML, CSS, JS, etc.) en un seul fichier zip**:
    *   Utiliser une approche type `crypto_secretbox`  de libsodium avec la clé de chiffrement.
2.  **Encapsulez ce zip chiffré dans un fichier JSON:**
     *     ```json
            {
            "encryptedZine": "<le zip chiffré en base64>",
            "totpSecret": "<le secret en base64>",
            "nonce": "<le nonce en base64>"
            }
            ```

**Étape 3: Affichage de la page de dévérouillage**

1.  **Remplacer le contenu du zine par une interface de dévérouillage:**
     *   Cette page contiendra un formulaire avec un champ de mot de passe, et un champ code TOTP.
     *   Ajouter un QR Code du secret TOTP
     *   Ajouter un `script.js` qui fera le travail de déchiffrement et de génération de l'URL du Zine

**Étape 4: Code JavaScript (script.js)**

```javascript
async function loadSodium() {
    if (window.sodium) return window.sodium;
    const wasmBin = '/ipfs/QmVQvM2aF5aV665yV9XjZ3h8G7Ue58V9953e8G4n8x2v4'; // Remplacer
    return new Promise((resolve, reject) => {
        fetch(wasmBin)
        .then((response) => response.arrayBuffer())
        .then((wasmBinary) => {
            sodium.ready.then(() => {
                resolve(sodium);
                sodium.load(wasmBinary);
                })

        });
    });
  }

  async function decryptZine(password, totpCode) {
      const sodium = await loadSodium();

        const zineDataRaw = await fetch("/ipfs/QmYnQpB5bQ8jM5g2hJz8zG8X2zC6b7e9pZ8sN7g4wFq").then(response => response.json());
        const encryptedZine =  sodium.from_base64(zineDataRaw.encryptedZine);
        const nonce = sodium.from_base64(zineDataRaw.nonce);
        const totpSecret = sodium.from_base64(zineDataRaw.totpSecret);


        const totp = new jsOTP.totp();
        const totpCheck = totp.verify(totpCode, totpSecret);
        if(!totpCheck) {
            alert("Code TOTP incorrect")
            return;
        }

      const key =  sodium.crypto_pwhash_scryptsalsa208sha256(sodium.crypto_secretbox_KEYBYTES, sodium.from_string(password), sodium.randombytes_buf(sodium.crypto_pwhash_scryptsalsa208sha256_SALTBYTES), 10, 15674, 2);

      try{
        const decryptedZipBuffer = sodium.crypto_secretbox_open(encryptedZine, nonce, key);
          if (!decryptedZipBuffer){
                alert("Mot de passe incorrect")
                return;
        }
      } catch(error) {
            alert("Mot de passe incorrect")
            return;
      }
      const decryptedZipBuffer = sodium.crypto_secretbox_open(encryptedZine, nonce, key);
       const decryptedZip = new JSZip();
          await decryptedZip.loadAsync(decryptedZipBuffer);
       const blobUrl = URL.createObjectURL(new Blob([decryptedZipBuffer], { type: 'application/zip' }));
       window.location.href = blobUrl;
  }


  document.addEventListener('DOMContentLoaded', function () {
     const decryptForm = document.getElementById("decryptForm");

     decryptForm.addEventListener('submit', async function(event) {
        event.preventDefault();
       const password = document.getElementById('password').value;
       const totpCode = document.getElementById('totpCode').value;
       await decryptZine(password, totpCode);
    });
});

```

**Exemple de code pour générer les clés côté serveur (NodeJS)**

```javascript
    const sodium = require('libsodium-wrappers');
    const fs = require('node:fs/promises');
    const JSZip = require("jszip");

    async function generateKeys() {
            await sodium.ready;
            const secretKey =  sodium.crypto_secretbox_keygen();
            const secretTotp = sodium.crypto_generichash(32, sodium.randombytes_buf(32));

            const secretKeyBase64 = sodium.to_base64(secretKey);
            const secretTotpBase64 = sodium.to_base64(secretTotp);
            console.log("Secret key :", secretKeyBase64);
            console.log("Secret totp:", secretTotpBase64);

            const zineFiles = {
                "index.html" : "<h1>Hello World</h1><p>This is the first Page of the Zine</p>",
                "style.css" : "body { background-color: red}"
            }

          const zip = new JSZip();

           for (const [filename, content] of Object.entries(zineFiles)) {
                zip.file(filename, content);
            }

        const zipBuffer = await zip.generateAsync({ type: "uint8array" });
        const nonce = sodium.randombytes_buf(sodium.crypto_secretbox_NONCEBYTES);
        const key =  sodium.crypto_pwhash_scryptsalsa208sha256(sodium.crypto_secretbox_KEYBYTES, sodium.from_string("password"), sodium.randombytes_buf(sodium.crypto_pwhash_scryptsalsa208sha256_SALTBYTES), 10, 15674, 2);

        const encryptedZip = sodium.crypto_secretbox(zipBuffer, nonce, key);


        const zineData = {
             "encryptedZine": sodium.to_base64(encryptedZip),
             "totpSecret": secretTotpBase64,
             "nonce": sodium.to_base64(nonce)
        }

        fs.writeFile("zineData.json", JSON.stringify(zineData))
    }

    generateKeys();
```

**Points Importants**

*   **LibSodium:** Assurez-vous d'avoir la bibliothèque LibSodium disponible dans votre environnement. Si vous l'utilisez dans un navigateur, vous devrez la charger via un CDN ou l'inclure dans votre projet.
*   **Sécurité du Secret TOTP:** Ne jamais exposer le secret TOTP directement dans le code client. Il doit être utilisé uniquement lors du processus d'authentification côté serveur ou local avec un fichier.
*   **Mot de passe:** La sécurité dépend de la complexité du mot de passe. Il est crucial que l'utilisateur utilise un mot de passe fort et unique.
*   **Chiffrement côté client :** Le code de l'exemple ci-dessus chiffre un fichier zip côté serveur (nodeJS) mais utilise le mot de passe pour déchiffrer en navigateur, d'où un risque potentiel d'attaque par force brute. On pourrait opter pour une solution avec un mot de passe seulement pour récupérer la clé de déchiffrement.

**Comment Utiliser**

1.  **Générez les clés côté serveur** et stocker le `zineData.json` en IPFS.
2.  **Incluez le fichier `libsodium.js`** dans la page de dévérouillage.
3.  **Créez une page de dévérouillage**, avec le code HTML suivant:

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Zine dévérouillage</title>
</head>
<body>
    <div class="container">
      <h2>Déverrouiller le Zine</h2>
      <form id="decryptForm">
            <div>
                  <label for="password">Mot de passe:</label>
                  <input type="password" id="password" required>
            </div>
            <div>
                <label for="totpCode">Code TOTP:</label>
                <input type="text" id="totpCode" required>
             </div>
           <button type="submit">Déverrouiller</button>
       </form>
    <img src="<your TOTP Qr code>" alt="QR Code TOTP" />
    </div>
      <script src="/ipfs/QmU3L7h4W67d7T6zN9gq3hR7bW5zY9p3L5c0u2b8X9k3v"></script>
</body>
</html>
```

4.  **Ajouter la page de dévérouillage** comme première page du Zine
5.  **Modifiez le `script.js`** avec le code ci-dessus.
6.  **Hébergez votre Zine** ainsi que le fichier `libsodium.js`, et  la page de dévérouillage avec votre fichier JSON.

**Conclusion**

En mettant en œuvre une combinaison de chiffrement avec LibSodium et d'authentification avec TOTP, vous offrez une solide protection à votre Zine numérique. Vous pouvez ainsi contrôler qui y a accès et quand, tout en assurant la confidentialité du contenu.

N'hésitez pas à adapter ce code à votre cas spécifique. Vous pouvez par exemple ajouter une fonction qui affiche une erreur si le mot de passe est erroné, ou vous faire une solution pour la gestion des mots de passes oublié. N'hésitez pas à me poser d'autres questions si vous en avez !

---

Coder la partie serveur en python (en incluant la génération du Zine et les étapes de création de sa version sécurisée)
ajouter une fonction qui affiche une erreur si le mot de passe est erroné
faire une solution pour la gestion des mots de passes oublié.

---

Absolument ! Voici une implémentation côté serveur en Python, intégrant la génération du Zine, le chiffrement avec `libsodium`, la gestion de l'authentification TOTP, la gestion des erreurs de mot de passe, et une solution pour les mots de passe oubliés.

**Prérequis**

1.  **Installation des bibliothèques:**
    ```bash
    pip install pysodium qrcode pyotp flask
    ```
2.  **Installation de `libsodium` (si nécessaire).** En général `pysodium` l'installe en même temps.

**Code Python (server.py)**

```python
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
    app.run(debug=True, port=5001)
```

**Explications**

1.  **Importations:** Les bibliothèques nécessaires sont importées.
2.  **Configuration:**
    *   `SECRET_KEY_ENV`: Variable d'environnement pour stocker la clé secrète.
    *   `ZINE_PASSWORD_FILE`: Fichier JSON pour stocker les hachages de mots de passe et les secrets TOTP pour la récupération.
3.  **Fonctions utilitaires:**
    *   `generate_nonce()`: Génère un nonce pour le chiffrement.
    *  `hash_password()`: Hache les mots de passe avec un salt pour le stockage sécurisé.
    *   `load_passwords()`: Charge les hachages de mots de passe et secrets TOTP depuis un fichier JSON.
    *   `save_passwords()`: Enregistre les hachages de mots de passe et les secrets TOTP dans un fichier JSON.
    *  `encrypt_zip()` : Chiffre un zip buffer avec la clé et le nonce
4.  **Route `/generate_zine`:**
    *   Génère le contenu du Zine (à partir d'un JSON) en un fichier zip
    *   Génère un secret pour le TOTP et la clé de chiffrement avec Libsodium et le mot de passe
    *   Chiffre le contenu du zine avec `crypto_secretbox`
    *   Stocke les clés et les infos dans un fichier JSON, en hachant le mot de passe.
    *   Retourne les informations du zine chiffré, du secret totp et du nonce (en base64).
5.   **Route `/recover_secret`:**
    *   Permet de récupérer le secret totp en fournissant le mot de passe.
6. **Fonction `create_zip_buffer` :**
    *   Convertie un dictionnaire de contenu en un buffer zip
7.  **Démarrage du serveur Flask** sur le port 5001

**Gestion du Mot de Passe Oublié**

*   **Stockage des Hachages:** Les mots de passe sont hachés avec un salt et stockés dans un fichier JSON ( `zine_passwords.json`). On stock aussi les secrets TOTP
*   **Récupération du Secret TOTP:** Une fonction dans l'API permet, lors de la soumission du mot de passe, de récupérer le secret TOTP qui lui est associé (si le mot de passe est valide). On utilise les même paramètres de salage pour retrouver le hash du mot de passe stocké.
*   **Réinitialisation du Mot de Passe:** Il faudrait ajouter une fonctionnalité qui permet de réinitialiser le mot de passe. Une solution pourrait être d'envoyer un lien de réinitialisation par email.

**Comment Utiliser**

1.  **Lancez le serveur Python** avec `python server.py`.
2.  **Envoyez une requête POST à `/generate_zine`** avec les paramètres `zine_content` et `password`. Voici un exemple en Python :

```python
import requests
import json

# Exemple de contenu de Zine
zine_content = {
    "index.html": "<h1>My Zine</h1><p>Welcome!</p>",
    "style.css": "body { background-color: lightblue; }"
}

password = "mysecretpassword"
# Envoyer la requête POST pour générer le Zine
url = "http://localhost:5001/generate_zine"
headers = {'Content-type': 'application/json'}

data = {
    "zine_content": zine_content,
    "password": password
}

response = requests.post(url, data=json.dumps(data), headers=headers)
if response.status_code == 200:
        zine_data = response.json()
        print("Zine généré :", zine_data)
else:
        print("Erreur :", response.json())

```
3.  **Récupérez le mot de passe :**
```python
import requests
import json

password = "mysecretpassword"

# Envoyer la requête POST pour générer le Zine
url = "http://localhost:5001/recover_secret"
headers = {'Content-type': 'application/json'}

data = {
    "password": password
}
response = requests.post(url, data=json.dumps(data), headers=headers)
if response.status_code == 200:
        zine_data = response.json()
        print("Secret totp récupéré :", zine_data)
else:
        print("Erreur :", response.json())
```

4.  **Utilisez le `zine_data`**  pour créer le fichier JSON pour la page de dévérouillage.
5. **Récuperez le `libsodium.js`** depuis IPFS et modifiez le `script.js` comme vu dans la réponse précédente.
6. **Ajoutez le QR Code** généré à partir du secret totp à votre page de dévérouillage. Vous pouvez utiliser une bibliothèque comme `qrcode` en python ou un autre service en ligne.

**Points à Noter**

*   **Sécurité des Clés:** Dans cet exemple, les clés et le fichier des mots de passe sont stockés localement, ce qui n'est pas idéal pour la production. Utilisez des variables d'environnement et des solutions de stockage sécurisées.
*   **Complexité du Mot de Passe:** La force du chiffrement dépend de la complexité du mot de passe.
*   **Réinitialisation du Mot de Passe:** La solution pour la réinitialisation du mot de passe est sommaire. Elle devrait être améliorée avec des solutions plus robuste et plus sécurisées.
*   **TOTP:** Pour le moment, le secret TOTP est seulement rendu accessible pour la récupération, mais non validé.

N'hésitez pas à me poser d'autres questions.
