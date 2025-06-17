from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv

load_dotenv()
import os

openai_api_key = os.environ.get("OPENAI_API_KEY")

def segment_text_with_llm(blocks: list[dict], model_name="gpt-4o"):
    """
    Utilise un modèle LLM pour segmenter les blocs typographiques en sections logiques.
    blocks: list de dicts comme [{"text": ..., "size": ..., "page": ...}, ...]
    """
    # 1. Build the prompt as a template with {bloc_data} variable
    prompt_text = (
        "Tu es un expert en structuration de documents.\n"
        "Voici une liste de blocs extraits d'un document avec leur taille de police.\n"
        "Segmentes-les en sections logiques avec un titre et un contenu clair.\n"
        "Rends-moi un JSON formaté comme : {{\"titre\": ..., \"bloc_data\": ...}}, ...\n\n"
        "{bloc_data}"
    )
    prompt_template = ChatPromptTemplate.from_template(prompt_text)

    # 2. Prepare bloc_data_text
    bloc_data_text = "\n".join([f"[taille={b['size']}] {b['text']}" for b in blocks if b["text"].strip()])

    # 3. Setup LLM and chain
    llm = ChatOpenAI(openai_api_key=openai_api_key, model_name=model_name, temperature=0)
    chain = prompt_template | llm | StrOutputParser()

    # 4. Invoke with correct variable
    return chain.invoke({
    "bloc_data": bloc_data_text,
    "titre": "Titre du document"  # ou toute autre valeur
})
