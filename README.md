# 🛒 Asistente Inteligente — Mercado Central 24h

Proyecto final del **Challenge Alura Agente** (Programa ONE AI FOR TECH — Alura Latam & Oracle).

Un agente de inteligencia artificial que responde, en lenguaje natural, preguntas sobre las políticas internas de Mercado Central 24h y sobre su inventario de productos, evitando que las personas colaboradoras tengan que buscar manualmente dentro de manuales, reglamentos y hojas de cálculo.

## 📋 Descripción general

Mercado Central 24h es una cadena de supermercados con presencia en México y Latinoamérica. Como en muchas empresas, su información vive repartida en distintos documentos: políticas de atención al cliente, reglamento interno, manual de proveedores, preguntas frecuentes y un inventario de productos en Excel.

Este proyecto implementa un **agente conversacional** capaz de:
- Responder preguntas sobre **políticas de la empresa** (devoluciones, reglamento interno, manual de proveedores, FAQ) a partir de los documentos PDF oficiales.
- Responder preguntas sobre el **inventario de productos** (stock, precio, ubicación en tienda, proveedor) a partir de un archivo Excel con 200 productos.

## 🏗️ Arquitectura de la solución

El agente está construido con **LangGraph** y decide dinámicamente qué herramienta usar según la pregunta recibida (patrón ReAct: razona sobre la pregunta y elige la acción adecuada).

```
                    ┌───────────────────────┐
   Pregunta ──────▶ │  Agente (LangGraph)    │
   del usuario      │  decide qué tool usar  │
                    └───────────┬────────────┘
                                │
              ┌──────────────────┴──────────────────┐
              ▼                                      ▼
  ┌─────────────────────────┐      ┌──────────────────────────────┐
  │ Tool: consultar_politicas│      │ Tool: consultar_inventario    │
  │                          │      │                                │
  │ RAG sobre 4 PDFs:        │      │ Búsqueda estructurada sobre    │
  │ atención al cliente,     │      │ el inventario Excel (200       │
  │ FAQ, reglamento interno, │      │ productos, 8 categorías):      │
  │ manual de proveedores.   │      │ stock, precio, ubicación,      │
  │ Vectorstore: FAISS       │      │ proveedor.                     │
  │ Embeddings: Gemini       │      │                                │
  └─────────────────────────┘      └──────────────────────────────┘
```

**Flujo de ingesta (una sola vez):** los PDFs de `data/politicas/` se cargan, se dividen en fragmentos (`chunk_size=1000`) y se convierten en embeddings que se guardan en un índice **FAISS** local (`src/ingest.py`).

**Flujo de consulta:** el usuario escribe una pregunta → el agente (LangGraph + Gemini) decide si necesita consultar las políticas (RAG), el inventario (búsqueda estructurada), o ambas → devuelve una respuesta en lenguaje natural.

## 🛠️ Tecnologías utilizadas

| Componente | Herramienta |
|---|---|
| Lenguaje | Python 3.11+ |
| Orquestación del agente | LangChain + LangGraph |
| Modelo de lenguaje (LLM) | Google Gemini (`gemini-flash-latest`) |
| Embeddings | Google Generative AI Embeddings (`gemini-embedding-001`) |
| Vectorstore | FAISS |
| Lectura de PDFs | PyPDF |
| Lectura de inventario | openpyxl |
| Interfaz | Streamlit |
| Despliegue | Oracle Cloud Infrastructure (OCI Compute) |

## 📁 Estructura del proyecto

```
mercado-central-agente/
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   ├── politicas/                          # PDFs de políticas de la empresa
│   └── inventario_de_supermercado_latam.xlsx
├── src/
│   ├── config.py                           # configuración y rutas
│   ├── ingest.py                           # construye el índice FAISS
│   ├── tools/
│   │   ├── politicas_tool.py               # herramienta RAG
│   │   └── inventario_tool.py              # herramienta de consulta estructurada
│   ├── agent.py                            # define y orquesta el agente
│   └── app.py                              # interfaz Streamlit
├── notebooks/
│   └── prototipo.ipynb                     # prototipado en Google Colab
└── vectorstore/                            # índice FAISS generado (no versionado)
```

## ▶️ Instrucciones para ejecutar el proyecto

### 1. Clonar el repositorio e instalar dependencias

```bash
git clone <URL_DE_ESTE_REPOSITORIO>
cd mercado-central-agente
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar la clave de API

Copia `.env.example` a `.env` y agrega tu clave de Google Gemini:

```bash
cp .env.example .env
```

```
GOOGLE_API_KEY=tu_api_key_aqui
```

### 3. Construir el índice de políticas (una sola vez)

```bash
python -m src.ingest
```

> El proceso embebe los fragmentos en lotes pequeños con pausas entre ellos para respetar el límite gratuito de la API de Gemini (100 solicitudes/minuto), por lo que puede tardar 3-4 minutos.

### 4. Ejecutar el agente

**Por consola:**
```bash
python -m src.agent
```

**Con interfaz web (Streamlit):**
```bash
streamlit run src/app.py
```

## 💬 Ejemplos de preguntas y respuestas

> **Pregunta:** ¿Cuántos días tengo para devolver un producto en Mercado Central 24h?
>
> **Respuesta del agente:** El plazo para devolver un producto en Mercado Central 24h depende de su categoría:
> - Abarrotes, enlatados, productos no perecederos, electrónica y hogar: hasta 30 días naturales.
> - Productos importados, cosméticos, cuidado personal, artículos de limpieza y artículos de temporada: hasta 15 días naturales.
> - Vinos y licores: hasta 7 días naturales.
> - Lácteos y embutidos: hasta 48 horas.
> - Frutas, verduras, panadería y pasteles (perecederos en general): hasta 24 horas.
> - Carnes, aves, mariscos y pescados frescos: hasta 12 horas (o el mismo día de la compra antes de las 22:00 h).

> **Pregunta:** ¿Cuántas unidades hay disponibles de Arroz Blanco Tipo 1 5kg?
>
> **Respuesta del agente:** Actualmente hay disponibles dos marcas de Arroz Blanco Tipo 1 5kg:
> 1. Marca Verde Valle (SKU: MER-001): 150 unidades disponibles (Pasillo 1, $25.9).
> 2. Marca Diana (SKU: MER-004): 120 unidades disponibles (Pasillo 1, $26.9).

> **Pregunta:** ¿Cuál es el proceso para dar de alta a un nuevo proveedor?
>
> **Respuesta del agente:** El proceso para dar de alta a un nuevo proveedor en Mercado Central 24h consta de 6 pasos:
> 1. Registro inicial en el portal: llenar el formulario en proveedores.mercadocentral24h.com con datos generales, categorías, representante legal, ejecutivo de ventas y cuenta CLABE interbancaria.
> 2. Entrega de documentación obligatoria: subir en formato PDF la documentación requerida (RFC, Opinión de Cumplimiento Fiscal, comprobantes, pólizas, etc.).
> 3. Visita técnica: inspección técnica a las instalaciones del proveedor.
> 4. Evaluación y dictamen del Comité de Compras: se evalúa el expediente completo y se emite un dictamen (Aprobado, Aprobado con condiciones, Diferido o Rechazado).
> 5. Firma de Contrato Marco y Alta en ERP: firma del Contrato Marco de Proveeduría y registro en el ERP corporativo, asignando un código de proveedor único.
> 6. Pedido piloto y evaluación de resultados: cumplimiento satisfactorio de una primera orden piloto antes de su integración regular al programa de compras.

> **Pregunta:** ¿Qué proveedor surte el Frijol Negro 1kg y cuál es su precio de venta?
>
> **Respuesta del agente:** El proveedor del Frijol Negro 1kg (Goya) es Distribuidora Granos S.A. y su precio de venta es $8.49.

## ☁️ Evidencia del despliegue en OCI

- **URL pública de la aplicación:** *[COMPLETAR — enlace a la app corriendo en OCI]*
- **Captura de pantalla:** *[COMPLETAR — agrega una imagen en `docs/` y enlázala aquí, ej. `![Deploy en OCI](docs/deploy-oci.png)`]*

## 👤 Autor

Proyecto desarrollado por **Julio Agustín Choi** como parte del programa **ONE AI FOR TECH** (Alura Latam & Oracle).
