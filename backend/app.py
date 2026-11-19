from pathlib import Path
from typing import Any, Dict
from flask import Flask, jsonify, request, send_from_directory

from models import SistemaAPPV

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
sistema = SistemaAPPV()


def obtener_json() -> Dict[str, Any]:
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise ValueError("Cuerpo JSON inválido.")
    return datos


@app.errorhandler(ValueError)
def manejar_error_validacion(error: ValueError):
    return jsonify({"error": str(error)}), 400


@app.route("/")
def servir_inicio():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/estado")
def obtener_estado():
    return jsonify(sistema.estado_completo())


# --- VIDEOCLUBS ---
@app.post("/api/videoclubs")
def crear_videoclub():
    datos = obtener_json()
    vc = sistema.crear_videoclub(
        datos.get("nombre_gerente", ""),
        datos.get("ciudad", ""),
        datos.get("calle", ""),
        datos.get("codigo_postal", ""),
    )
    return jsonify(vc), 201


@app.put("/api/videoclubs/<int:codigo>")
def editar_videoclub(codigo: int):
    datos = obtener_json()
    vc = sistema.editar_videoclub(
        codigo,
        datos.get("nombre_gerente", ""),
        datos.get("ciudad", ""),
        datos.get("calle", ""),
        datos.get("codigo_postal", ""),
    )
    return jsonify(vc)


# --- PELÍCULAS ---
@app.post("/api/peliculas")
def crear_pelicula():
    datos = obtener_json()
    pelicula = sistema.crear_pelicula(
        int(datos.get("videoclub_codigo", 0)),
        datos.get("nombre", ""),
        datos.get("director"),
        datos.get("fecha_estreno", ""),
        float(datos.get("precio_alquiler", 0)),
    )
    return jsonify(pelicula), 201


@app.put("/api/peliculas/<int:codigo>")
def editar_pelicula(codigo: int):
    datos = obtener_json()
    pelicula = sistema.editar_pelicula(
        codigo,
        datos.get("nombre", ""),
        datos.get("director"),
        datos.get("fecha_estreno", ""),
        float(datos.get("precio_alquiler", 0)),
    )
    return jsonify(pelicula)


# --- SOCIOS ---
@app.post("/api/socios")
def crear_socio():
    datos = obtener_json()
    socio = sistema.crear_socio(datos.get("nombre", ""), int(datos.get("edad", 0)))
    return jsonify(socio), 201


@app.put("/api/socios/<int:codigo>")
def editar_socio(codigo: int):
    datos = obtener_json()
    socio = sistema.editar_socio(codigo, datos.get("nombre", ""), int(datos.get("edad", 0)))
    return jsonify(socio)


# --- ALQUILERES ---
@app.post("/api/alquileres")
def crear_alquiler():
    datos = obtener_json()
    codigos_peliculas = datos.get("peliculas_codigos", [])
    if not isinstance(codigos_peliculas, list) or not codigos_peliculas:
        raise ValueError("Debes seleccionar al menos una película.")

    alquiler = sistema.crear_alquiler(
        int(datos.get("socio_codigo", 0)),
        [int(c) for c in codigos_peliculas],
        datos.get("fecha_recogida", ""),
        datos.get("fecha_devolucion", ""),
    )
    return jsonify(alquiler), 201


@app.put("/api/alquileres/<int:codigo>/devolucion")
def editar_devolucion(codigo: int):
    datos = obtener_json()
    alquiler = sistema.modificar_fecha_devolucion(
        codigo,
        datos.get("nueva_fecha_devolucion", ""),
        datos.get("fecha_actual", ""),
    )
    return jsonify(alquiler)


# --- ADMINISTRADORES ---
@app.post("/api/administradores")
def crear_administrador():
    datos = obtener_json()
    admin = sistema.crear_admin(datos.get("nombre", ""))
    return jsonify(admin), 201


@app.put("/api/administradores/<int:codigo>")
def editar_administrador(codigo: int):
    datos = obtener_json()
    admin = sistema.editar_admin(codigo, datos.get("nombre", ""))
    return jsonify(admin)


# --- ESTADÍSTICAS ---
@app.post("/api/estadisticas")
def crear_estadistica():
    datos = obtener_json()
    est = sistema.crear_estadistica(
        int(datos.get("administrador_codigo", 0)),
        int(datos.get("socio_codigo", 0)),
        int(datos.get("mes", 0)),
        int(datos.get("anio", 0)),
        datos.get("fecha_creacion", ""),
    )
    return jsonify(est), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)