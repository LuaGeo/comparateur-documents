from pdf2image import convert_from_path

# Chemin du PDF scanné
pdf_path = ".\docs\img\exemple1_scanned.pdf"

# Convertir le PDF en images
images = convert_from_path(pdf_path, fmt="jpeg")

# Sauvegarder les images
for i, image in enumerate(images):
    image.save(f"page_{i + 1}.jpg", "JPEG")
    print(f"Page {i + 1} sauvegardée sous page_{i + 1}.jpg")