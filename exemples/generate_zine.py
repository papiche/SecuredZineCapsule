import requests
import json

# Exemple de contenu de Zine
zine_content = {
    "index.html": "<h1>My Zine</h1><p>Welcome!</p>",
    "style.css": "body { background-color: lightblue; }"
}

password = "mysecretpassword"
# Envoyer la requête POST pour générer le Zine
url = "http://localhost:5002/generate_zine"
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
