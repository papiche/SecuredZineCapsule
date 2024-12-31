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
