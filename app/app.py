import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import io


# Ajoutez le répertoire racine au chemin d'accès pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.preprocessing.document_utils import (
    extract_text_from_file,
    rotate_image_to_portrait,
    display_pdf,
    convert_docx_to_pdf,
    generate_diff_html
)

st.set_page_config(
    page_title="Comparateur de Documents",
    page_icon="📄",
    layout="centered"
)

st.title("Comparateur de Documents 📄")

st.markdown("""
Cette application permet de comparer deux documents (images, PDF ou DOCX) et d'analyser leurs différences.
""")

# Barre latérale pour télécharger des fichiers
with st.sidebar:
    st.header("Upload des Documents")
    
    # Téléchargement du premier document
    doc1 = st.file_uploader("Document 1", type=['jpg', 'jpeg', 'png', 'pdf', 'docx'])
    
    # Téléchargement du deuxième document
    doc2 = st.file_uploader("Document 2", type=['jpg', 'jpeg', 'png', 'pdf', 'docx'])
    
    # Bouton pour lancer la comparaison
    compare_button = st.button("Comparer les Documents")

# Champ principal pour les résultats
if doc1 and doc2 and compare_button:
    # Créer un répertoire temporaire si ce n'est pas déjà fait
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Enregistrer les fichiers temporairement
    doc1_path = temp_dir / doc1.name
    doc2_path = temp_dir / doc2.name
    
    with open(doc1_path, "wb") as f:
        f.write(doc1.getbuffer())
    with open(doc2_path, "wb") as f:
        f.write(doc2.getbuffer())
    
    try:
        # Extraire le texte des documents
        file_type1 = Path(doc1.name).suffix.lower()
        file_type2 = Path(doc2.name).suffix.lower()
        
        print(f"Traitement du document 1: {doc1_path} (type: {file_type1})")
        text1 = extract_text_from_file(str(doc1_path), file_type1)
        print(f"Texte extrait du document 1 (longueur: {len(text1)}): {text1[:100]}...")
        
        print(f"Traitement du document 2: {doc2_path} (type: {file_type2})")
        text2 = extract_text_from_file(str(doc2_path), file_type2)
        print(f"Texte extrait du document 2 (longueur: {len(text2)}): {text2[:100]}...")
        
        if not text1:
            raise ValueError(f"Le document 1 n'a pas pu être lu (type: {file_type1})")
        if not text2:
            raise ValueError(f"Le document 2 n'a pas pu être lu (type: {file_type2})")
        
        # Calculer les métriques de comparaison
        from Levenshtein import distance
        lev_distance = distance(text1, text2)
        max_len = max(len(text1), len(text2))
        similarity = 1 - (lev_distance / max_len) if max_len > 0 else 0
        
        result = {
            'distance': lev_distance,
            'similarity': similarity,
            'text1_length': len(text1),
            'text2_length': len(text2)
        }
        
        # Afficher les résultats
        st.header("Résultats de la Comparaison")
        
        # Configurer le layout pour une meilleure visualisation en portrait
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Document 1")
            if file_type1 in ['.jpg', '.jpeg', '.png']:
                img1 = Image.open(io.BytesIO(doc1.getvalue()))
                img1 = rotate_image_to_portrait(img1)
                st.image(img1, use_container_width=True)
            elif file_type1 == '.pdf':
                display_pdf(str(doc1_path))
            elif file_type1 == '.docx':
                st.text_area("Aperçu du document Word", text1, height=600, key="docx_preview_1")
            else:
                st.warning(f"Format non pris en charge : {file_type1}")

        with col2:
            st.subheader("Document 2")
            if file_type2 in ['.jpg', '.jpeg', '.png']:
                img2 = Image.open(io.BytesIO(doc2.getvalue()))
                img2 = rotate_image_to_portrait(img2)
                st.image(img2, use_container_width=True)
            elif file_type2 == '.pdf':
                display_pdf(str(doc2_path))
            elif file_type2 == '.docx':
                st.text_area("Aperçu du document Word", text2, height=600, key="docx_preview_2")
            else:
                st.warning(f"Format non pris en charge : {file_type2}")


        # Métriques de comparaison dans un conteneur séparé
        with st.container():
            st.subheader("Métriques de Comparaison")
            col_metrics1, col_metrics2 = st.columns(2)
            
            with col_metrics1:
                st.metric("Similarité", f"{result['similarity']:.2%}")
                st.metric("Distance de Levenshtein", result['distance'])
            
            with col_metrics2:
                st.metric("Longueur Document 1", f"{result['text1_length']} caractères")
                st.metric("Longueur Document 2", f"{result['text2_length']} caractères")
            
            with st.expander("🧠 Différences détaillées"):
                diff_html = generate_diff_html(text1, text2)
                st.markdown(diff_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erreur lors de la comparaison: {str(e)}")
    
    finally:
        # Nettoyer les fichiers temporaires
        if doc1_path.exists():
            doc1_path.unlink()
        if doc2_path.exists():
            doc2_path.unlink()



elif compare_button and (not doc1 or not doc2):
    st.warning("Veuillez uploader les deux documents avant de lancer la comparaison.") 

