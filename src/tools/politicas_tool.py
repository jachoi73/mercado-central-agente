"""
Herramienta de RAG: responde preguntas sobre las politicas de Mercado Central 24h
(atencion al cliente, devoluciones, reglamento interno, proveedores) usando el
vectorstore construido por src/ingest.py.

Construida con LCEL (LangChain Expression Language), el patron moderno de
composicion de cadenas en LangChain.

Requiere haber ejecutado antes: python -m src.ingest
"""
from langchain.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from src import config

_embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)
_vectorstore = FAISS.load_local(
    config.VECTORSTORE_DIR, _embeddings, allow_dangerous_deserialization=True
)
_retriever = _vectorstore.as_retriever(search_kwargs={"k": 4})

_llm = ChatGoogleGenerativeAI(model=config.MODEL_NAME, temperature=0)

_PROMPT = ChatPromptTemplate.from_template(
    """Responde la pregunta usando unicamente el siguiente contexto extraido
de los documentos oficiales de Mercado Central 24h. Si la respuesta no esta
en el contexto, indica con claridad que no cuentas con esa informacion.

Contexto:
{context}

Pregunta: {question}

Respuesta:"""
)


def _formatear_documentos(documentos):
    return "\n\n".join(doc.page_content for doc in documentos)


_cadena_rag = (
    {"context": _retriever | _formatear_documentos, "question": RunnablePassthrough()}
    | _PROMPT
    | _llm
    | StrOutputParser()
)


@tool
def consultar_politicas(pregunta: str) -> str:
    """
    Responde preguntas sobre las politicas de Mercado Central 24h: atencion al
    cliente, cambios y devoluciones, reglamento interno para empleados y el
    manual de proveedores. Usala cuando la pregunta trate sobre reglas,
    procedimientos, beneficios, garantias o normas de la empresa.
    """
    return _cadena_rag.invoke(pregunta)
