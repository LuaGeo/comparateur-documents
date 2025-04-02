#!/bin/bash

# Vérifie si Homebrew est installé
if ! command -v brew &> /dev/null
then
    echo "Installation de Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Installe Tesseract et les langues
echo "Installation de Tesseract..."
brew install tesseract tesseract-lang

# Vérification
echo "Vérification de l'installation..."
tesseract --version