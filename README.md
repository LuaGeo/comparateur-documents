# Comparateur de Documents

Outil pour comparer des documents (textes, PDF, images) avec IA

## Prérequis

- macOS (testé sur Ventura 13.4)
- Tesseract OCR 5.3.2+
- Python 3.13.2 (recommandé)

## Installation

```bash
git clone https://github.com/LuaGeo/comparateur-documents.git
cd comparateur-documents

# Installation des dépendances
./scripts/install_tesseract.sh  # Pour Mac
pip install -r requirements.txt
```

## Utilisation

```python
from src.main import compare_documents

result = compare_documents("doc1.pdf", "doc2.docx")
print(result)
```

## Structure

```
/expliquer structure ici/
```

## Contribuer

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez (`git commit -m 'Ajout feature'`)
4. Pushez (`git push origin feature/amelioration`)
5. Créez une Pull Request

```

```
