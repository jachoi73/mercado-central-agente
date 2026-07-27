"""
Carga los PDFs de politicas de Mercado Central 24h, los divide en fragmentos
(chunks) y construye un indice vectorial FAISS que luego usara la herramienta
de RAG (src/tools/politicas_tool.py).

Ejecutar una sola vez (o cada vez que cambien los documentos en data/politicas):
    python -m src.ingest
"""
import os
import time

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src import config

# El free tier de la API de Gemini limita embed_content a 100 unidades por
# minuto. Embebemos en lotes pequeños con una pausa entre ellos para no
# exceder esa cuota.
LOTE_EMBEDDINGS = 90
PAUSA_ENTRE_LOTES_SEG = 61


def construir_vectorstore():
    print(f"Cargando PDFs desde: {config.POLITICAS_DIR}")
    loader = PyPDFDirectoryLoader(config.POLITICAS_DIR)
    documentos = loader.load()
    print(f"  -> {len(documentos)} paginas cargadas")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    fragmentos = splitter.split_documents(documentos)
    print(f"  -> {len(fragmentos)} fragmentos generados")

    embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)

    textos = [f.page_content for f in fragmentos]
    metadatas = [f.metadata for f in fragmentos]

    vectores = []
    total_lotes = (len(textos) + LOTE_EMBEDDINGS - 1) // LOTE_EMBEDDINGS
    for i in range(0, len(textos), LOTE_EMBEDDINGS):
        lote = textos[i : i + LOTE_EMBEDDINGS]
        num_lote = i // LOTE_EMBEDDINGS + 1
        print(f"  -> Generando embeddings: lote {num_lote}/{total_lotes} ({len(lote)} fragmentos)")
        vectores.extend(embeddings.embed_documents(lote))
        if i + LOTE_EMBEDDINGS < len(textos):
            print(f"     Esperando {PAUSA_ENTRE_LOTES_SEG}s para respetar la cuota gratuita...")
            time.sleep(PAUSA_ENTRE_LOTES_SEG)

    vectorstore = FAISS.from_embeddings(
        list(zip(textos, vectores)), embeddings, metadatas=metadatas
    )

    os.makedirs(config.VECTORSTORE_DIR, exist_ok=True)
    vectorstore.save_local(config.VECTORSTORE_DIR)
    print(f"Vectorstore guardado en: {config.VECTORSTORE_DIR}")


if __name__ == "__main__":
    construir_vectorstore()
