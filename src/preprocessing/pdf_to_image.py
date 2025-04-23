from pdf2image import convert_from_path
import os

# Chemin du PDF scanné
pdf_path = ".\docs\examples\img\exemple1_scanned.pdf"

# Dossier de sortie
output_dir = ".\docs\output\pages"

# Créer le dossier s'il n'existe pas
os.makedirs(output_dir, exist_ok=True)

# Convertir le PDF en images
images = convert_from_path(pdf_path, fmt="jpeg", poppler_path=r"C:\Users\DEOLIVEIRALuana\Poppler\poppler-24.08.0\Library\bin")

# Sauvegarder les images
for i, image in enumerate(images):
    output_path = os.path.join(output_dir, f"page_{i + 1}.jpg")
    image.save(output_path, "JPEG")
    print(f"Page {i + 1} sauvegardée sous {output_path}")