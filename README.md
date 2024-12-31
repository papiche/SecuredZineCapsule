**Résumé du Projet**

Ce projet vise à créer un Zine numérique sécurisé, accessible uniquement après une authentification combinant un mot de passe et un code TOTP (Time-Based One-Time Password). Le contenu du Zine est chiffré, et l'accès nécessite un déchiffrement côté client après une authentification réussie. La solution comprend un serveur Python pour la génération du Zine chiffré et la gestion des mots de passe, ainsi qu'une page de déverrouillage en HTML/JavaScript pour l'authentification et le déchiffrement côté client.

**Objectifs Principaux**

1.  **Confidentialité:** Protéger le contenu du Zine contre les accès non autorisés grâce au chiffrement.
2.  **Authentification:** Valider l'identité de l'utilisateur avec un mot de passe et un code TOTP.
3.  **Sécurité:** Utiliser des méthodes cryptographiques robustes (libsodium) et le hachage de mots de passe.
4.  **Facilité d'utilisation:** Offrir une interface simple pour déverrouiller le Zine.
5.  **Récupération du secret TOTP :** Permettre la récupération du secret TOTP si l'utilisateur oublie son mot de passe.

**Fichiers Utilisés**

1.  **`server.py` (Serveur Python):**
    *   Génère le Zine chiffré en réponse à une requête POST à `/generate_zine`.
    *   Hache le mot de passe et stocke son hachage ainsi que le secret TOTP dans un fichier JSON (`zine_passwords.json`).
    *   Génère une clé de chiffrement et un nonce pour le chiffrement AES-GCM (via libsodium).
    *   Retourne les données chiffrées, le secret TOTP (en base64) et le nonce (en base64)
    *   Fournit une route `/recover_secret` pour récupérer le secret TOTP à partir du mot de passe.
    *   Utilise Flask pour gérer les requêtes HTTP.
2.  **`zine_passwords.json` (Fichier JSON):**
    *   Stocke les hachages de mots de passe avec leur salt et les secrets TOTP (en base64).
    *   Utilisé pour la récupération du secret TOTP et la réinitialisation du mot de passe (à implémenter).
3.  **`index.html` (Page de Déverrouillage):**
    *   Page HTML avec un formulaire de déverrouillage (champs mot de passe et code TOTP).
    *   Contient un QR Code pour la configuration de l'application TOTP.
    *   Contient les liens vers le `libsodium.js` et `script.js`.
4.  **`script.js` (Script JavaScript):**
    *   Récupère les données du Zine chiffré et le secret TOTP du serveur.
    *   Charge la bibliothèque Libsodium (depuis un CDN/IPFS).
    *   Déchiffre le Zine avec la clé dérivée du mot de passe (avec `crypto_pwhash_scryptsalsa208sha256`) et le nonce.
    *   Vérifie le code TOTP avec `jsOTP`.
    *   Télécharge et affiche le contenu du Zine une fois déchiffré et le code TOTP validé.
5.  **`libsodium.js` (Bibliothèque Libsodium):**
    *   Bibliothèque JavaScript pour la cryptographie côté client (téléchargée depuis IPFS/CDN).

**Flux de Fonctionnement**

1.  **Génération du Zine (Côté Serveur):**
    *   L'utilisateur (ou l'administrateur) envoie une requête POST à l'endpoint `/generate_zine` avec :
        *   Un dictionnaire `zine_content` contenant des clés avec le nom des fichiers (par exemple, "index.html", "style.css") et leur valeur en contenu.
        *   Un mot de passe `password` pour le chiffrement et le déchiffrement.
    *   Le serveur crée un fichier zip des fichiers reçu, puis génère un secret TOTP aléatoire et une clé de chiffrement,
    *   Le serveur chiffre le contenu du ZIP avec Libsodium.
    *   Le serveur stocke l'hachage du mot de passe (avec un salt) et le secret TOTP, dans `zine_passwords.json`.
    *   Le serveur renvoie les données chiffrées, le secret TOTP (en base64) et le nonce (en base64).

2.  **Page de Déverrouillage (Côté Client):**
    *   L'utilisateur accède à la page `index.html` qui contient un formulaire de déverrouillage.
    *   L'utilisateur scanne le QR Code avec une application TOTP (Google Authenticator, Authy).
    *   L'utilisateur entre le mot de passe et le code TOTP.
    *   Le `script.js` envoie une requête au serveur pour récupérer le JSON contenant le zine chiffré.
    *   Le `script.js` utilise `crypto_pwhash_scryptsalsa208sha256` avec le mot de passe pour retrouver la clé de déchiffrement.
    *   Le `script.js` déchiffre le contenu du Zine avec Libsodium.
     *    Le script `script.js` valide le code TOTP avec `jsOTP`.
    *   Si l'authentification est réussie, le `script.js` décompresse le ZIP en mémoire et redirige vers un lien blob de ce fichier.
    *  Si l'authentification échoue, un message d'erreur est affiché.

3.  **Récupération du Secret TOTP:**
    *   L'utilisateur peut demander la récupération du secret TOTP en envoyant une requête POST à `/recover_secret` avec le mot de passe.
    *   Le serveur vérifie si le mot de passe haché existe dans `zine_passwords.json`.
    *   Si le mot de passe est valide, le serveur renvoie le secret TOTP associé.
    *   Sinon, une erreur est renvoyée.

**Détails Techniques**

*   **Chiffrement:** `libsodium.js` est utilisé pour le chiffrement symétrique avec `crypto_secretbox` qui offre une confidentialité et intégrité des données. La clé de chiffrement est dérivée du mot de passe via la méthode  `crypto_pwhash_scryptsalsa208sha256` , ce qui assure que même si le fichier zip chiffré est intercepté, le contenu ne pourra être déchiffré sans le mot de passe.
*   **Authentification TOTP:** Le secret TOTP est généré côté serveur, converti en QR Code pour être scanné avec une application d'authentification. Le `script.js` utilise `jsOTP` pour vérifier le code TOTP envoyé par l'utilisateur.
*   **Hachage de Mots de Passe:** Les mots de passe sont hachés avec un salt via `pysodium.crypto_pwhash_scryptsalsa208sha256`, ce qui améliore la sécurité.
*   **Gestion des Erreurs:**  Des messages d'erreur sont affichés si le mot de passe ou le code TOTP sont invalides.

**Améliorations Possibles**

*   **Réinitialisation du Mot de Passe:** Ajouter une fonction pour réinitialiser le mot de passe via email ou un autre système de notification.
*  **Stocker les fichiers chiffré** : Stocker le zine chiffré dans un CDN ou un stockage IPFS.
*  **Charger les fichiers en mémoire** : Eviter de télécharger le zine en un seul fichier et le charger en mémoire. Cela pourrait se faire via le streaming.
*   **Interface Utilisateur:** Améliorer l'interface utilisateur pour une meilleure expérience.
*   **Sécurité du Serveur:** Renforcer la sécurité du serveur et les pratiques de stockage des clés.
*   **Session côté serveur :** Ajouter un session côté serveur pour éviter de devoir renvoyer le mot de passe à chaque vérification.
*  **Chiffrement asymétrique :** remplacer le chiffrement du zip par un chiffrement asymétrique. La clé publique du serveur serait partagée, et l'utilisateur pourrait alors chiffrer son mot de passe pour le déchiffrer du côté serveur.

En résumé, ce projet fournit une base solide pour la création d'un Zine numérique sécurisé, avec un chiffrement robuste, une authentification forte, et une gestion de la récupération de l'accès.

