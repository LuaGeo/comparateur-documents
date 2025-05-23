import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import io
# import os
# import base64
# import pypandoc


# Ajoutez le répertoire racine au chemin d'accès pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.preprocessing.document_utils import (
    extract_text_from_file,
    rotate_image_to_portrait,
    display_pdf,
    convert_docx_to_pdf,
    generate_diff_html,
    count_pages,
    segment_text_by_topics,
    detect_section_headings_by_layout
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
        # Extraire o texto dos documentos
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
        
        # Contar páginas
        pages1 = count_pages(str(doc1_path), file_type1)
        pages2 = count_pages(str(doc2_path), file_type2)
        
        # Segmentar textos em tópicos
        # topics1 = segment_text_by_topics(text1)
        # topics2 = segment_text_by_topics(text2)
        if file_type1 == ".pdf":
            topics1 = {f"{i+1}.": sec["text"] for i, sec in enumerate(detect_section_headings_by_layout(str(doc1_path)))}
        else:
            topics1 = segment_text_by_topics(text1)

        if file_type2 == ".pdf":
            topics2 = {f"{i+1}.": sec["text"] for i, sec in enumerate(detect_section_headings_by_layout(str(doc2_path)))}
        else:
            topics2 = segment_text_by_topics(text2)

        
        # Calcular métricas de comparação
        from Levenshtein import distance
        lev_distance = distance(text1, text2)
        max_len = max(len(text1), len(text2))
        similarity = 1 - (lev_distance / max_len) if max_len > 0 else 0
        
        result = {
            'distance': lev_distance,
            'similarity': similarity,
            'text1_length': len(text1),
            'text2_length': len(text2),
            'pages1': pages1,
            'pages2': pages2,
            'topics1': topics1,
            'topics2': topics2
        }
        
        # Afficher les résultats
        st.header("Résultats de la Comparaison")
        
        # Configurer le layout pour une meilleure visualisation en portrait
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Document 1")
            st.metric("Nombre de pages", pages1)
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
            st.metric("Nombre de pages", pages2)
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

        # Métricas de comparação em um container separado
        with st.container():
            st.subheader("Metriques de comparaison")
            col_metrics1, col_metrics2 = st.columns(2)
            
            with col_metrics1:
                st.metric("Similarité", f"{result['similarity']:.2%}")
                st.metric("Distance de Levenshtein", result['distance'])
            
            with col_metrics2:
                st.metric("Taille du Document 1", f"{result['text1_length']} caracteres")
                st.metric("Taille du Document 2", f"{result['text2_length']} caracteres")
            
            # Comparação por tópicos
            st.subheader("Comparaison par section")
            
            # Encontrar tópicos comuns
            common_topics = set(topics1.keys()) & set(topics2.keys())
            
            if common_topics:
                def sort_key(topic):
                    # Extraire les entiers de '1.', '2.1.', '10.2'
                    return [int(part) for part in topic.strip('.').split('.') if part.isdigit()]

                for topic in sorted(common_topics, key=sort_key):
                    with st.expander(f"Section {topic}"):
                        col_t1, col_t2 = st.columns(2)
                        with col_t1:
                            st.text_area("Document 1", topics1[topic], height=200, key=f"topic1_{topic}")
                        with col_t2:
                            st.text_area("Document 2", topics2[topic], height=200, key=f"topic2_{topic}")
                        
                        # Calcular similaridade para este tópico
                        topic_lev = distance(topics1[topic], topics2[topic])
                        topic_max_len = max(len(topics1[topic]), len(topics2[topic]))
                        topic_similarity = 1 - (topic_lev / topic_max_len) if topic_max_len > 0 else 0
                        st.metric(f"Similarité de Section {topic}", f"{topic_similarity:.2%}")
            else:
                st.warning("Pas de section commune entre les documents.")
            
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

