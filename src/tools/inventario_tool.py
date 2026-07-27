"""
Herramienta de consulta estructurada: busca productos en el inventario de
Mercado Central 24h (data/inventario_de_supermercado_latam.xlsx) por SKU,
nombre, marca o categoria.
"""
import openpyxl
from langchain.tools import tool

from src import config

_wb = openpyxl.load_workbook(config.INVENTARIO_PATH, data_only=True)
_ws = _wb.active
_filas = list(_ws.iter_rows(values_only=True))
_encabezados = _filas[0]
_productos = [dict(zip(_encabezados, fila)) for fila in _filas[1:] if fila[0]]


@tool
def consultar_inventario(termino: str) -> str:
    """
    Busca productos en el inventario de Mercado Central 24h por SKU, nombre,
    marca o categoria. Devuelve stock actual, precio de venta, ubicacion en
    tienda y proveedor principal. Usala cuando la pregunta trate sobre
    disponibilidad, precio, stock o proveedor de un producto.
    """
    termino_normalizado = termino.strip().lower()
    coincidencias = [
        p
        for p in _productos
        if termino_normalizado in str(p.get("Descripción", "")).lower()
        or termino_normalizado in str(p.get("SKU", "")).lower()
        or termino_normalizado in str(p.get("Marca", "")).lower()
        or termino_normalizado in str(p.get("Categoría", "")).lower()
    ]

    if not coincidencias:
        return f"No se encontraron productos que coincidan con '{termino}'."

    lineas = []
    for p in coincidencias[:5]:
        lineas.append(
            f"- {p['Descripción']} ({p['Marca']}) | SKU: {p['SKU']} | "
            f"Stock: {p['Stock Actual']} unidades | "
            f"Precio: ${p['Precio de Venta Unitario']} | "
            f"Ubicación: {p['Ubicación']} | "
            f"Proveedor: {p['Proveedor Principal']}"
        )

    if len(coincidencias) > 5:
        lineas.append(f"... y {len(coincidencias) - 5} resultado(s) más.")

    return "\n".join(lineas)
