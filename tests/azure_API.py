import os
from dotenv import load_dotenv
import requests
import json
import certifi

load_dotenv(dotenv_path="./.env/.env")

ENDPOINT = os.getenv('ENDPOINT')
API_KEY = os.getenv('KEY')
OCR_URL = f"{ENDPOINT}vision/v3.2/ocr"

# Chemin de l'image
image_path = "./docs/examples/img/exemple1_scanned.jpg"

# Lire l'image en binaire
with open(image_path, "rb") as image_file:
    image_data = image_file.read()

# En-têtes de requête
headers = {
    "Ocp-Apim-Subscription-Key": API_KEY,
    "Content-Type": "application/octet-stream"
}

# Envoi de l’image à l’API OCR
response = requests.post(OCR_URL, headers=headers, data=image_data, verify=certifi.where())
result = response.json()

# Affichage du texte extrait
extracted_text = []
for region in result.get("regions", []):
    for line in region.get("lines", []):
        words = [word["text"] for word in line["words"]]
        extracted_text.append(" ".join(words))

print("\n".join(extracted_text))
