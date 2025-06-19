import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import io

# Ajoutez le répertoire racine au chemin d'accès pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.preprocessing.segment_with_llm import segment_text_with_llm
from src.preprocessing.document_utils import (
    extract_text_from_file,
    rotate_image_to_portrait,
    display_pdf,
    #generate_diff_html,
    count_pages,
    segment_text_by_topics,
    #analyze_text_structure,
    #extract_typo_blocks,
    extract_paragraph_blocks
    #highlight_diff_html

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
    if compare_button and (not doc1 or not doc2):
        st.warning("❗ Merci de recharger les deux documents avant de lancer la comparaison.")
        st.stop()

# Champ principal pour les résultats
if doc1 and doc2 and compare_button:
    if doc1 is None or doc2 is None:
        st.warning("Fichiers manquants. Veuillez les recharger dans la barre latérale.")
        st.stop()
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
        topics1 = segment_text_by_topics(text1)
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

            
        #     st.header("Résultats de la Comparaison")

        # if file_type1 == '.pdf':
        #     st.subheader("Structure typographique du Document 1")
        #     try:
        #         structure1 = analyze_text_structure(str(doc1_path))
        #         for niveau, infos in structure1.items():
        #             st.markdown(f"**{niveau}** — taille : {infos['taille_px']} px — {infos['occurrences']} occurrences")
        #             for ex in infos["exemples"]:
        #                 st.markdown(f"- _{ex}_")
        #     except Exception as e:
        #         st.warning(f"Erreur d'analyse typographique du document 1 : {e}")

        #     if file_type2 == '.pdf':
        #         st.subheader("Structure typographique du Document 2")
        #         try:
        #             structure2 = analyze_text_structure(str(doc2_path))
        #             for niveau, infos in structure2.items():
        #                 st.markdown(f"**{niveau}** — taille : {infos['taille_px']} px — {infos['occurrences']} occurrences")
        #                 for ex in infos["exemples"]:
        #                     st.markdown(f"- _{ex}_")
        #         except Exception as e:
        #             st.warning(f"Erreur d'analyse typographique du document 2 : {e}")

            # with st.expander("🧠 Différences détaillées"):
            #     diff_html = generate_diff_html(text1, text2)
            #     st.markdown(diff_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erreur lors de la comparaison: {str(e)}")
    

    # finally:
    #     # Nettoyer les fichiers temporaires
    #     if doc1_path.exists():
    #         doc1_path.unlink()
    #     if doc2_path.exists():
    #         doc2_path.unlink()

        # Extraire blocs des deux documents (ancien approche)
    """blocks1 = extract_paragraph_blocks(str(doc1_path))
    blocks2 = extract_paragraph_blocks(str(doc2_path))

    with st.expander("🔍 Visualiser les blocs typographiques extraits du Document 1"):
        for i, block in enumerate(blocks1):
            st.markdown(f"Bloc #{i+1} (page {block['page']})")
            st.code(block['text'], language='markdown')


    with st.expander("🔍 Visualiser les blocs typographiques extraits du Document 2"):
        for i, block in enumerate(blocks2):
            st.markdown(f"Bloc #{i+1} (page {block['page']})")
            st.code(block['text'], language='markdown')"""

###################################################################    
###### Extraire blocs des deux documents (NOUVEL approche): #######
###################################################################

    blocks1 = extract_paragraph_blocks(str(doc1_path))
    blocks2 = extract_paragraph_blocks(str(doc2_path))

    # # Afficher les statistiques
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.metric("📄 Document 1", f"{len(blocks1)} blocs")
    # with col2:
    #     st.metric("📄 Document 2", f"{len(blocks2)} blocs")

    # # Fonction utilitaire pour l'affichage avec style
    # def display_block_with_style(block, block_num):
    #     """Affiche un bloc avec un style selon son type"""
        
    #     # Définir les couleurs et icônes selon le type
    #     type_config = {
    #         "titre": {"color": "blue", "icon": "🏷️", "bg": "#e6f3ff"},
    #         "paragraphe": {"color": "black", "icon": "📝", "bg": "#f9f9f9"},
    #         "liste": {"color": "green", "icon": "📋", "bg": "#f0fff4"},
    #         "citation": {"color": "purple", "icon": "💬", "bg": "#faf0ff"}
    #     }
        
    #     config = type_config.get(block.get('type', 'paragraphe'), type_config['paragraphe'])
        
    #     # Conteneur avec style personnalisé
    #     with st.container():
    #         # En-tête du bloc
    #         col1, col2, col3 = st.columns([0.5, 2, 1])
    #         with col1:
    #             st.write(f"{config['icon']}")
    #         with col2:
    #             st.markdown(f"**Bloc #{block_num}** - {block.get('type', 'paragraphe').title()}")
    #         with col3:
    #             st.caption(f"Page {block['page']}")
            
    #         # Contenu du bloc avec style conditionnel
    #         if block.get('type') == 'titre':
    #             st.markdown(f"### {block['text']}")
    #         else:
    #             # Utiliser un conteneur avec background coloré
    #             st.markdown(f"""
    #             <div style="background-color: {config['bg']}; padding: 10px; border-radius: 5px; margin: 5px 0;">
    #                 {block['text']}
    #             </div>
    #             """, unsafe_allow_html=True)
            
    #         # Informations supplémentaires pour DOCX
    #         if 'style' in block:
    #             st.caption(f"Style: {block['style']}")

    # # Visualisation du Document 1
    # with st.expander("🔍 Visualiser les blocs typographiques extraits du Document 1"):
    #     # Filtres optionnels
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         show_types1 = st.multiselect(
    #             "Filtrer par type:", 
    #             options=list(set(block.get('type', 'paragraphe') for block in blocks1)),
    #             default=list(set(block.get('type', 'paragraphe') for block in blocks1)),
    #             key="filter1"
    #         )
    #     with col2:
    #         show_pages1 = st.multiselect(
    #             "Filtrer par page:", 
    #             options=sorted(list(set(block['page'] for block in blocks1))),
    #             default=sorted(list(set(block['page'] for block in blocks1))),
    #             key="pages1"
    #         )
        
    #     # Filtrer les blocs
    #     filtered_blocks1 = [
    #         block for block in blocks1 
    #         if block.get('type', 'paragraphe') in show_types1 and block['page'] in show_pages1
    #     ]
        
    #     st.info(f"Affichage de {len(filtered_blocks1)} blocs sur {len(blocks1)} total")
        
    #     for i, block in enumerate(filtered_blocks1):
    #         display_block_with_style(block, i+1)
    #         if i < len(filtered_blocks1) - 1:  # Pas de séparateur après le dernier
    #             st.divider()

    # # Visualisation du Document 2
    # with st.expander("🔍 Visualiser les blocs typographiques extraits du Document 2"):
    #     # Filtres optionnels
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         show_types2 = st.multiselect(
    #             "Filtrer par type:", 
    #             options=list(set(block.get('type', 'paragraphe') for block in blocks2)),
    #             default=list(set(block.get('type', 'paragraphe') for block in blocks2)),
    #             key="filter2"
    #         )
    #     with col2:
    #         show_pages2 = st.multiselect(
    #             "Filtrer par page:", 
    #             options=sorted(list(set(block['page'] for block in blocks2))),
    #             default=sorted(list(set(block['page'] for block in blocks2))),
    #             key="pages2"
    #         )
        
    #     # Filtrer les blocs
    #     filtered_blocks2 = [
    #         block for block in blocks2 
    #         if block.get('type', 'paragraphe') in show_types2 and block['page'] in show_pages2
    #     ]
        
    #     st.info(f"Affichage de {len(filtered_blocks2)} blocs sur {len(blocks2)} total")
        
    #     for i, block in enumerate(filtered_blocks2):
    #         display_block_with_style(block, i+1)
    #         if i < len(filtered_blocks2) - 1:
    #             st.divider()

    with st.expander("🔍 Visualiser les blocs typographiques extraits du Document 1"):
        for i, block in enumerate(blocks1):
            # Ajout du type dans l'affichage
            type_emoji = {"titre": "🏷️", "liste": "📋", "citation": "💬"}.get(block.get('type'), "📝")
            st.markdown(f"{type_emoji} **Bloc #{i+1}** (page {block['page']}) - *{block.get('type', 'paragraphe')}*")
            st.code(block['text'], language='markdown')

    with st.expander("🔍 Visualiser les blocs typographiques extraits du Document 2"):
        for i, block in enumerate(blocks2):
            type_emoji = {"titre": "🏷️", "liste": "📋", "citation": "💬"}.get(block.get('type'), "📝")
            st.markdown(f"{type_emoji} **Bloc #{i+1}** (page {block['page']}) - *{block.get('type', 'paragraphe')}*")
            st.code(block['text'], language='markdown')


    # Segmentation sémantique via GPT
    # sections1 = segment_text_with_llm(blocks1)
    # sections2 = segment_text_with_llm(blocks2)

    # st.write("sections1 =", sections1)
    # st.write("sections2 =", sections2)
    # st.write("type(sections1[0]) =", type(sections1[0]))

    # # Associer les titres communs pour comparaison
    # common_titles = {s["titre"] for s in sections1} & {s["titre"] for s in sections2}

    # for title in sorted(common_titles):
    #     text1 = next(s["contenu"] for s in sections1 if s["titre"] == title)
    #     text2 = next(s["contenu"] for s in sections2 if s["titre"] == title)
        
    #     st.markdown(f"### 🔎 Section : {title}")
    #     html_diff = highlight_diff_html(text1, text2)
    #     st.markdown(html_diff, unsafe_allow_html=True)

elif compare_button and (not doc1 or not doc2):
    st.warning("Veuillez uploader les deux documents avant de lancer la comparaison.") 





