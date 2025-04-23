import streamlit as st
from utils.ocr import extract_text
from utils.compare import compare_documents
import pandas as pd

st.set_page_config(page_title="Comparateur de Documents", layout="wide")

# Sidebar Upload
with st.sidebar:
    st.header("📤 Téléversement")
    doc1 = st.file_uploader("Document 1", type=["pdf", "docx", "png", "jpg"])
    doc2 = st.file_uploader("Document 2", type=["pdf", "docx", "png", "jpg"])

# Main Content
st.title("🔍 Comparateur IA de Documents")

if doc1 and doc2:
    with st.spinner("Analyse en cours..."):
        # Extraction et comparaison
        result = compare_documents(doc1, doc2)
        
        # Métriques principales
        col1, col2, col3 = st.columns(3)
        col1.metric("Distance de Levenshtein", result['distance'])
        col2.metric("Similarité", f"{result['similarity']:.2%}")
        col3.metric("Différence de longueur", abs(result['text1_length'] - result['text2_length']))
        
        # Affichage comparé
        st.subheader("Comparaison côte à côte")
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_area("Texte Document 1", result['text1'], height=300)
        
        with col2:
            st.text_area("Texte Document 2", result['text2'], height=300)
        
        # Détection des différences (optionnel)
        st.subheader("Zones de divergence")
        diff_html = highlight_differences(result['text1'], result['text2'])
        st.components.v1.html(diff_html, height=400, scrolling=True)

else:
    st.info("Veuillez téléverser deux documents à comparer")