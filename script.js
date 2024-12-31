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
