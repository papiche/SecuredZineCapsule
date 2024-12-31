**Explications**

*   **Structure HTML:**
    *   Le code HTML crée une page simple avec un formulaire de déverrouillage et une image pour le QR code du TOTP.
    *   Un conteneur `div` pour centrer et styliser le formulaire.
    *   Un formulaire avec des champs de saisie pour le mot de passe et le code TOTP.
    *   Un bouton de soumission pour déclencher le processus de déverrouillage.
    *   Une image pour le QR code du TOTP (vous devrez remplacer `/ipfs/<your TOTP Qr code>` par le chemin vers votre QR code).
*   **Styles CSS:**
    *   Le CSS inclus stylise la page pour une présentation agréable et centrée.
    *   Il définit les styles du conteneur, des champs de saisie, du bouton de soumission et de l'image du QR code.
*   **Script JavaScript:**
    *   Le script est chargé depuis le lien IPFS `/ipfs/QmXq9b8y3kZ2b6d9R8wN7qJ5p6jK0v7sL6c4f3gH5t8k`. C'est la nouvelle version du `script.js` qui a été mis à jour. Il se chargera du traitement du dévérouillage (déchiffrement, validation du code TOTP) et de la redirection.

**Comment utiliser**

1.  **Enregistrez ce code** sous le nom `zine.html`.
2.  **Remplacez `/ipfs/<your TOTP Qr code>`** par le chemin vers l'image QR Code TOTP générée (vous pouvez utiliser une libraire python comme `qrcode` pour le générer).
3.  **Assurez-vous que le fichier `script.js`** (celui qui a été fourni précédemment) est disponible à l'adresse `/ipfs/QmXq9b8y3kZ2b6d9R8wN7qJ5p6jK0v7sL6c4f3gH5t8k` (en IPFS ou sur votre serveur).
4.  **Assurez-vous que le fichier `libsodium.js`** est disponible à l'adresse `/ipfs/QmVQvM2aF5aV665yV9XjZ3h8G7Ue58V9953e8G4n8x2v4` (en IPFS ou sur votre serveur).
5.  **Placez ce fichier `zine.html`** à la place de la page `index.html` de votre zine.

**Important**

*   Le chemin vers le script JavaScript dans la balise `<script>` doit correspondre au chemin réel de votre fichier `script.js`.
*   Le style CSS est inclus directement dans le fichier HTML pour une meilleure portabilité. Si vous avez d'autres styles CSS, vous pouvez les inclure dans un fichier CSS externe et les lier.

Ce fichier HTML fournira une page de déverrouillage fonctionnelle pour votre Zine. L'utilisateur devra entrer le mot de passe et le code TOTP pour accéder au contenu du Zine. N'hésitez pas à l'adapter à votre design et vos besoins spécifiques.
