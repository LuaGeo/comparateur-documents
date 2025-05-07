from pdf2image import convert_from_path
import os
import platform
from pathlib import Path

def get_poppler_path():
    """Retourne le chemin de Poppler selon le système d'exploitation"""
    system = platform.system()
    
    if system == 'Windows':
        # Chemins possibles pour Windows
        windows_paths = [
            r"C:\Users\DEOLIVEIRALuana\Poppler\poppler-25.05.0\Library\bin",
            r"C:\Program Files\poppler-25.05.0\Library\bin"
        ]
        for path in windows_paths:
            if os.path.exists(path):
                return path
    else:  # Mac ou Linux
        # Chemins possibles para Mac/Linux
        unix_paths = [
            '/usr/local/bin',
            '/usr/bin',
            '/opt/homebrew/bin'
        ]
        for path in unix_paths:
            if os.path.exists(path):
                return path
    
    raise EnvironmentError("Poppler non trouvé. Veuillez l'installer et vérifier les chemins.")

def pdf_to_images(pdf_path, output_dir=None):
    """Convertit un PDF en images et retourne la liste des chemins des images"""
    try:
        print(f"Tentative de conversion du PDF en images: {pdf_path}")
        
        # Vérifier si le fichier existe
        if not os.path.exists(pdf_path):
            raise ValueError(f"Le fichier PDF n'existe pas: {pdf_path}")
        
        # Si aucun dossier de sortie n'est spécifié, utiliser un dossier temporaire
        if output_dir is None:
            output_dir = Path("temp_pdf_images")
            output_dir.mkdir(exist_ok=True)
            print(f"Dossier temporaire créé: {output_dir}")
        
        # Obtenir le chemin de Poppler
        poppler_path = get_poppler_path()
        print(f"Chemin Poppler utilisé: {poppler_path}")
        
        # Convertir le PDF en images avec des paramètres optimisés
        print("Début de la conversion PDF en images...")
        images = convert_from_path(
            pdf_path,
            fmt="jpeg",
            poppler_path=poppler_path,
            dpi=400,  # Augmenter la résolution
            grayscale=True,  # Convertir en niveaux de gris
            size=(3000, None),  # Redimensionner pour une meilleure qualité
            thread_count=4,  # Utiliser plusieurs threads pour la conversion
            use_pdftocairo=True  # Utiliser pdftocairo pour une meilleure qualité
        )
        print(f"Conversion terminée. {len(images)} pages converties")
        
        # Sauvegarder les images et collecter les chemins
        image_paths = []
        for i, image in enumerate(images):
            output_path = output_dir / f"page_{i + 1}.jpg"
            print(f"Sauvegarde de la page {i+1} dans: {output_path}")
            # Sauvegarder avec une meilleure qualité
            image.save(str(output_path), "JPEG", quality=100)
            image_paths.append(str(output_path))
        
        print(f"Conversion terminée avec succès. {len(image_paths)} images créées")
        return image_paths
    except Exception as e:
        print(f"Erreur lors de la conversion du PDF en images: {str(e)}")
        return []