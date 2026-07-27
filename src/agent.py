"""
Define y orquesta el agente inteligente de Mercado Central 24h usando LangGraph.
El agente decide, segun la pregunta del usuario, si debe consultar las
politicas de la empresa (RAG) o el inventario de productos (consulta
estructurada), o ambas.
"""
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from src import config
from src.tools.inventario_tool import consultar_inventario
from src.tools.politicas_tool import consultar_politicas

_llm = ChatGoogleGenerativeAI(model=config.MODEL_NAME, temperature=0)

_herramientas = [consultar_politicas, consultar_inventario]

_PROMPT_SISTEMA = """Eres el asistente virtual interno de Mercado Central 24h.
Respondes preguntas de colaboradores sobre las politicas de la empresa
(atencion al cliente, devoluciones, reglamento interno, proveedores) y sobre
el inventario de productos (stock, precio, ubicacion, proveedor).

Usa la herramienta 'consultar_politicas' para preguntas sobre reglas,
procedimientos o normas. Usa 'consultar_inventario' para preguntas sobre
productos especificos. Si la pregunta no puede responderse con la
informacion disponible, dilo con claridad en vez de inventar una respuesta.
Responde siempre en espanol, de forma clara y concisa.
"""

agente = create_agent(_llm, _herramientas, system_prompt=_PROMPT_SISTEMA)


def _extraer_texto(contenido) -> str:
    """Normaliza el content del mensaje a texto plano.

    Versiones recientes de langchain-google-genai devuelven el content como
    una lista de bloques (p. ej. [{"type": "text", "text": "...", "extras": {...}}])
    en vez de un string simple, para soportar firmas de razonamiento.
    """
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        partes = []
        for bloque in contenido:
            if isinstance(bloque, dict) and bloque.get("type") == "text":
                partes.append(bloque.get("text", ""))
            elif isinstance(bloque, str):
                partes.append(bloque)
        return "".join(partes)
    return str(contenido)


def preguntar(pregunta: str) -> str:
    """Punto de entrada simple para hacerle una pregunta al agente."""
    resultado = agente.invoke({"messages": [("user", pregunta)]})
    return _extraer_texto(resultado["messages"][-1].content)


if __name__ == "__main__":
    print("Agente de Mercado Central 24h -- escribe 'salir' para terminar\n")
    while True:
        pregunta = input("Tu: ")
        if pregunta.strip().lower() == "salir":
            break
        print("Agente:", preguntar(pregunta), "\n")
