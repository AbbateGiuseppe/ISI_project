import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

FORMATO_FECHA = "%d/%m/%Y"
RUTA_DB_POR_DEFECTO = Path(__file__).resolve().parent / "appv.db"


def parsear_fecha_manual(texto_fecha: str, nombre_campo: str) -> date:
    """Convierte una cadena DD/MM/AAAA en date sin usar nunca el reloj del sistema."""
    if not texto_fecha or not isinstance(texto_fecha, str):
        raise ValueError(f"El campo '{nombre_campo}' es obligatorio.")
    try:
        return datetime.strptime(texto_fecha.strip(), FORMATO_FECHA).date()
    except ValueError as exc:
        raise ValueError(
            f"Formato inválido en '{nombre_campo}'. Usa DD/MM/AAAA (ej. 15/05/2026)."
        ) from exc


def validar_texto_obligatorio(valor: Any, nombre_campo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"El campo '{nombre_campo}' es obligatorio.")
    return valor.strip()


def validar_codigo_postal(cp: Any) -> str:
    texto = validar_texto_obligatorio(cp, "Código postal")
    if len(texto) != 5:
        raise ValueError("El código postal debe tener exactamente 5 caracteres.")
    return texto


class SistemaAPPV:
    """Gestor persistente de la cadena APPV respaldado por SQLite."""

    def __init__(self, ruta_db: Path = RUTA_DB_POR_DEFECTO):
        self.ruta_db = Path(ruta_db)
        self._inicializar_esquema()

    def _conectar(self) -> sqlite3.Connection:
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA foreign_keys = ON;")
        return conexion

    def _inicializar_esquema(self) -> None:
        with self._conectar() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS videoclubs (
                    codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_gerente TEXT NOT NULL,
                    ciudad TEXT NOT NULL,
                    calle TEXT NOT NULL,
                    codigo_postal TEXT NOT NULL CHECK (length(codigo_postal) = 5)
                );

                CREATE TABLE IF NOT EXISTS peliculas (
                    codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    director TEXT,
                    fecha_estreno TEXT NOT NULL,
                    precio_alquiler REAL NOT NULL CHECK (precio_alquiler > 0),
                    videoclub_codigo INTEGER NOT NULL,
                    FOREIGN KEY (videoclub_codigo) REFERENCES videoclubs(codigo)
                );

                CREATE TABLE IF NOT EXISTS socios (
                    codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    edad INTEGER NOT NULL CHECK (edad > 0)
                );

                CREATE TABLE IF NOT EXISTS alquileres (
                    codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    socio_codigo INTEGER NOT NULL,
                    fecha_recogida TEXT NOT NULL,
                    fecha_devolucion TEXT NOT NULL,
                    FOREIGN KEY (socio_codigo) REFERENCES socios(codigo)
                );

                CREATE TABLE IF NOT EXISTS alquiler_peliculas (
                    alquiler_codigo INTEGER NOT NULL,
                    pelicula_codigo INTEGER NOT NULL,
                    PRIMARY KEY (alquiler_codigo, pelicula_codigo),
                    FOREIGN KEY (alquiler_codigo) REFERENCES alquileres(codigo),
                    FOREIGN KEY (pelicula_codigo) REFERENCES peliculas(codigo)
                );

                CREATE TABLE IF NOT EXISTS administradores (
                    codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS estadisticas (
                    codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    administrador_codigo INTEGER NOT NULL,
                    socio_codigo INTEGER NOT NULL,
                    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
                    anio INTEGER NOT NULL,
                    fecha_creacion TEXT NOT NULL,
                    UNIQUE (socio_codigo, mes, anio),
                    FOREIGN KEY (administrador_codigo) REFERENCES administradores(codigo),
                    FOREIGN KEY (socio_codigo) REFERENCES socios(codigo)
                );
                """
            )

    @staticmethod
    def _iso_a_es(fecha_iso: str) -> str:
        return date.fromisoformat(fecha_iso).strftime(FORMATO_FECHA)

    # --- VIDEOCLUBS ---
    def crear_videoclub(
        self, nombre_gerente: str, ciudad: str, calle: str, codigo_postal: str
    ) -> Dict[str, Any]:
        gerente_ok = validar_texto_obligatorio(nombre_gerente, "Nombre del gerente")
        ciudad_ok = validar_texto_obligatorio(ciudad, "Ciudad")
        calle_ok = validar_texto_obligatorio(calle, "Calle")
        cp_ok = validar_codigo_postal(codigo_postal)

        with self._conectar() as conn:
            cursor = conn.execute(
                """
                INSERT INTO videoclubs (nombre_gerente, ciudad, calle, codigo_postal)
                VALUES (?, ?, ?, ?)
                """,
                (gerente_ok, ciudad_ok, calle_ok, cp_ok),
            )
            codigo = cursor.lastrowid
        return self.obtener_videoclub(int(codigo))

    def editar_videoclub(
        self, codigo: int, nombre_gerente: str, ciudad: str, calle: str, codigo_postal: str
    ) -> Dict[str, Any]:
        self.obtener_videoclub(codigo)
        gerente_ok = validar_texto_obligatorio(nombre_gerente, "Nombre del gerente")
        ciudad_ok = validar_texto_obligatorio(ciudad, "Ciudad")
        calle_ok = validar_texto_obligatorio(calle, "Calle")
        cp_ok = validar_codigo_postal(codigo_postal)

        with self._conectar() as conn:
            conn.execute(
                """
                UPDATE videoclubs
                SET nombre_gerente = ?, ciudad = ?, calle = ?, codigo_postal = ?
                WHERE codigo = ?
                """,
                (gerente_ok, ciudad_ok, calle_ok, cp_ok, codigo),
            )
        return self.obtener_videoclub(codigo)

    def obtener_videoclub(self, codigo: int) -> Dict[str, Any]:
        with self._conectar() as conn:
            fila = conn.execute(
                "SELECT codigo, nombre_gerente, ciudad, calle, codigo_postal FROM videoclubs WHERE codigo = ?",
                (codigo,),
            ).fetchone()
        if not fila:
            raise ValueError(f"No existe el videoclub con código {codigo}.")
        return dict(fila)

    def listar_videoclubs(self) -> List[Dict[str, Any]]:
        with self._conectar() as conn:
            filas = conn.execute(
                "SELECT codigo, nombre_gerente, ciudad, calle, codigo_postal FROM videoclubs ORDER BY codigo"
            ).fetchall()
        return [dict(f) for f in filas]

    # --- PELÍCULAS ---
    def crear_pelicula(
        self,
        videoclub_codigo: int,
        nombre: str,
        director: Optional[str],
        fecha_estreno_str: str,
        precio_alquiler: float,
    ) -> Dict[str, Any]:
        self.obtener_videoclub(videoclub_codigo)
        nombre_ok = validar_texto_obligatorio(nombre, "Nombre")
        director_ok = director.strip() if isinstance(director, str) and director.strip() else None
        fecha_estreno = parsear_fecha_manual(fecha_estreno_str, "Fecha de estreno")
        if precio_alquiler <= 0:
            raise ValueError("El precio de alquiler debe ser mayor que 0.")
        precio_ok = round(float(precio_alquiler), 2)

        with self._conectar() as conn:
            cursor = conn.execute(
                """
                INSERT INTO peliculas (nombre, director, fecha_estreno, precio_alquiler, videoclub_codigo)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nombre_ok, director_ok, fecha_estreno.isoformat(), precio_ok, videoclub_codigo),
            )
            codigo = cursor.lastrowid
        return self.obtener_pelicula(int(codigo))

    def editar_pelicula(
        self,
        codigo: int,
        nombre: str,
        director: Optional[str],
        fecha_estreno_str: str,
        precio_alquiler: float,
    ) -> Dict[str, Any]:
        self.obtener_pelicula(codigo)
        nombre_ok = validar_texto_obligatorio(nombre, "Nombre")
        director_ok = director.strip() if isinstance(director, str) and director.strip() else None
        fecha_estreno = parsear_fecha_manual(fecha_estreno_str, "Fecha de estreno")
        if precio_alquiler <= 0:
            raise ValueError("El precio de alquiler debe ser mayor que 0.")
        precio_ok = round(float(precio_alquiler), 2)

        with self._conectar() as conn:
            conn.execute(
                """
                UPDATE peliculas
                SET nombre = ?, director = ?, fecha_estreno = ?, precio_alquiler = ?
                WHERE codigo = ?
                """,
                (nombre_ok, director_ok, fecha_estreno.isoformat(), precio_ok, codigo),
            )
        return self.obtener_pelicula(codigo)

    def obtener_pelicula(self, codigo: int) -> Dict[str, Any]:
        with self._conectar() as conn:
            fila = conn.execute(
                """
                SELECT p.codigo, p.nombre, p.director, p.fecha_estreno, p.precio_alquiler,
                       p.videoclub_codigo, v.ciudad AS videoclub_ciudad
                FROM peliculas p
                JOIN videoclubs v ON v.codigo = p.videoclub_codigo
                WHERE p.codigo = ?
                """,
                (codigo,),
            ).fetchone()
        if not fila:
            raise ValueError(f"No existe la película con código {codigo}.")
        datos = dict(fila)
        datos["fecha_estreno"] = self._iso_a_es(datos["fecha_estreno"])
        return datos

    def listar_peliculas(self) -> List[Dict[str, Any]]:
        with self._conectar() as conn:
            filas = conn.execute(
                """
                SELECT p.codigo, p.nombre, p.director, p.fecha_estreno, p.precio_alquiler,
                       p.videoclub_codigo, v.ciudad AS videoclub_ciudad
                FROM peliculas p
                JOIN videoclubs v ON v.codigo = p.videoclub_codigo
                ORDER BY p.codigo
                """
            ).fetchall()
        resultado = []
        for f in filas:
            datos = dict(f)
            datos["fecha_estreno"] = self._iso_a_es(datos["fecha_estreno"])
            resultado.append(datos)
        return resultado

    # --- SOCIOS ---
    def crear_socio(self, nombre: str, edad: int) -> Dict[str, Any]:
        nombre_ok = validar_texto_obligatorio(nombre, "Nombre")
        if edad <= 0:
            raise ValueError("La edad debe ser un entero positivo.")

        with self._conectar() as conn:
            cursor = conn.execute(
                "INSERT INTO socios (nombre, edad) VALUES (?, ?)",
                (nombre_ok, int(edad)),
            )
            codigo = cursor.lastrowid
        return self.obtener_socio(int(codigo))

    def editar_socio(self, codigo: int, nombre: str, edad: int) -> Dict[str, Any]:
        self.obtener_socio(codigo)
        nombre_ok = validar_texto_obligatorio(nombre, "Nombre")
        if edad <= 0:
            raise ValueError("La edad debe ser un entero positivo.")

        with self._conectar() as conn:
            conn.execute(
                "UPDATE socios SET nombre = ?, edad = ? WHERE codigo = ?",
                (nombre_ok, int(edad), codigo),
            )
        return self.obtener_socio(codigo)

    def obtener_socio(self, codigo: int) -> Dict[str, Any]:
        with self._conectar() as conn:
            fila = conn.execute(
                "SELECT codigo, nombre, edad FROM socios WHERE codigo = ?",
                (codigo,),
            ).fetchone()
        if not fila:
            raise ValueError(f"No existe el socio con código {codigo}.")
        return dict(fila)

    def listar_socios(self) -> List[Dict[str, Any]]:
        with self._conectar() as conn:
            filas = conn.execute(
                "SELECT codigo, nombre, edad FROM socios ORDER BY codigo"
            ).fetchall()
        return [dict(f) for f in filas]

    # --- ALQUILERES ---
    def crear_alquiler(
        self,
        socio_codigo: int,
        peliculas_codigos: List[int],
        fecha_recogida_str: str,
        fecha_devolucion_str: str,
    ) -> Dict[str, Any]:
        self.obtener_socio(socio_codigo)
        if not peliculas_codigos:
            raise ValueError("Un alquiler debe incluir al menos una película.")
        if len(set(peliculas_codigos)) != len(peliculas_codigos):
            raise ValueError("No puedes repetir la misma película en el mismo alquiler.")

        for cod_pelicula in peliculas_codigos:
            self.obtener_pelicula(cod_pelicula)

        fecha_recogida = parsear_fecha_manual(fecha_recogida_str, "Fecha de recogida")
        fecha_devolucion = parsear_fecha_manual(fecha_devolucion_str, "Fecha de devolución")
        if fecha_devolucion <= fecha_recogida:
            raise ValueError("La fecha de devolución debe ser posterior a la fecha de recogida.")

        with self._conectar() as conn:
            cursor = conn.execute(
                """
                INSERT INTO alquileres (socio_codigo, fecha_recogida, fecha_devolucion)
                VALUES (?, ?, ?)
                """,
                (socio_codigo, fecha_recogida.isoformat(), fecha_devolucion.isoformat()),
            )
            alquiler_codigo = int(cursor.lastrowid)
            for cod_pelicula in peliculas_codigos:
                conn.execute(
                    """
                    INSERT INTO alquiler_peliculas (alquiler_codigo, pelicula_codigo)
                    VALUES (?, ?)
                    """,
                    (alquiler_codigo, cod_pelicula),
                )
        return self.obtener_alquiler(alquiler_codigo)

    def modificar_fecha_devolucion(
        self, codigo: int, nueva_fecha_str: str, fecha_actual_str: str
    ) -> Dict[str, Any]:
        self.obtener_alquiler(codigo)
        fecha_actual = parsear_fecha_manual(fecha_actual_str, "Fecha actual")
        nueva_fecha = parsear_fecha_manual(nueva_fecha_str, "Nueva fecha de devolución")
        if nueva_fecha <= fecha_actual:
            raise ValueError("La nueva fecha de devolución debe ser posterior a la fecha actual.")

        with self._conectar() as conn:
            conn.execute(
                "UPDATE alquileres SET fecha_devolucion = ? WHERE codigo = ?",
                (nueva_fecha.isoformat(), codigo),
            )
        return self.obtener_alquiler(codigo)

    def obtener_alquiler(self, codigo: int) -> Dict[str, Any]:
        with self._conectar() as conn:
            fila = conn.execute(
                """
                SELECT a.codigo, a.socio_codigo, s.nombre AS socio_nombre,
                       a.fecha_recogida, a.fecha_devolucion
                FROM alquileres a
                JOIN socios s ON s.codigo = a.socio_codigo
                WHERE a.codigo = ?
                """,
                (codigo,),
            ).fetchone()
            if not fila:
                raise ValueError(f"No existe el alquiler con código {codigo}.")

            peliculas_filas = conn.execute(
                """
                SELECT p.codigo, p.nombre, p.precio_alquiler AS precio
                FROM alquiler_peliculas ap
                JOIN peliculas p ON p.codigo = ap.pelicula_codigo
                WHERE ap.alquiler_codigo = ?
                ORDER BY p.codigo
                """,
                (codigo,),
            ).fetchall()

        peliculas = [dict(pf) for pf in peliculas_filas]
        total_pagar = round(sum(p["precio"] for p in peliculas), 2)
        return {
            "codigo": fila["codigo"],
            "socio_codigo": fila["socio_codigo"],
            "socio_nombre": fila["socio_nombre"],
            "peliculas": peliculas,
            "fecha_recogida": self._iso_a_es(fila["fecha_recogida"]),
            "fecha_devolucion": self._iso_a_es(fila["fecha_devolucion"]),
            "total_pagar": total_pagar,
        }

    def listar_alquileres(self) -> List[Dict[str, Any]]:
        with self._conectar() as conn:
            filas = conn.execute("SELECT codigo FROM alquileres ORDER BY codigo").fetchall()
        return [self.obtener_alquiler(int(f["codigo"])) for f in filas]

    # --- ADMINISTRADORES ---
    def crear_admin(self, nombre: str) -> Dict[str, Any]:
        nombre_ok = validar_texto_obligatorio(nombre, "Nombre")
        with self._conectar() as conn:
            cursor = conn.execute(
                "INSERT INTO administradores (nombre) VALUES (?)",
                (nombre_ok,),
            )
            codigo = cursor.lastrowid
        return self.obtener_admin(int(codigo))

    def editar_admin(self, codigo: int, nombre: str) -> Dict[str, Any]:
        self.obtener_admin(codigo)
        nombre_ok = validar_texto_obligatorio(nombre, "Nombre")
        with self._conectar() as conn:
            conn.execute(
                "UPDATE administradores SET nombre = ? WHERE codigo = ?",
                (nombre_ok, codigo),
            )
        return self.obtener_admin(codigo)

    def obtener_admin(self, codigo: int) -> Dict[str, Any]:
        with self._conectar() as conn:
            fila = conn.execute(
                "SELECT codigo, nombre FROM administradores WHERE codigo = ?",
                (codigo,),
            ).fetchone()
        if not fila:
            raise ValueError(f"No existe el administrador con código {codigo}.")
        return dict(fila)

    def listar_admins(self) -> List[Dict[str, Any]]:
        with self._conectar() as conn:
            filas = conn.execute(
                "SELECT codigo, nombre FROM administradores ORDER BY codigo"
            ).fetchall()
        return [dict(f) for f in filas]

    # --- ESTADÍSTICAS ---
    def crear_estadistica(
        self,
        admin_codigo: int,
        socio_codigo: int,
        mes: int,
        anio: int,
        fecha_creacion_str: str,
    ) -> Dict[str, Any]:
        self.obtener_admin(admin_codigo)
        socio = self.obtener_socio(socio_codigo)
        if mes < 1 or mes > 12:
            raise ValueError("El mes debe estar comprendido entre 1 y 12.")
        fecha_creacion = parsear_fecha_manual(fecha_creacion_str, "Fecha de creación")

        with self._conectar() as conn:
            existente = conn.execute(
                """
                SELECT 1 FROM estadisticas
                WHERE socio_codigo = ? AND mes = ? AND anio = ?
                """,
                (socio_codigo, mes, anio),
            ).fetchone()
            if existente:
                raise ValueError(
                    f"Ya existe una estadística para el socio '{socio['nombre']}' en {mes:02d}/{anio}."
                )

            cursor = conn.execute(
                """
                INSERT INTO estadisticas (administrador_codigo, socio_codigo, mes, anio, fecha_creacion)
                VALUES (?, ?, ?, ?, ?)
                """,
                (admin_codigo, socio_codigo, mes, anio, fecha_creacion.isoformat()),
            )
            codigo = cursor.lastrowid
        return self.obtener_estadistica(int(codigo))

    def _calcular_total_gastado(self, socio_codigo: int, mes: int, anio: int) -> float:
        periodo = f"{anio:04d}-{mes:02d}"
        with self._conectar() as conn:
            fila = conn.execute(
                """
                SELECT COALESCE(SUM(p.precio_alquiler), 0.0) AS total
                FROM alquileres a
                JOIN alquiler_peliculas ap ON ap.alquiler_codigo = a.codigo
                JOIN peliculas p ON p.codigo = ap.pelicula_codigo
                WHERE a.socio_codigo = ?
                  AND substr(a.fecha_recogida, 1, 7) = ?
                """,
                (socio_codigo, periodo),
            ).fetchone()
        return round(float(fila["total"]), 2)

    def obtener_estadistica(self, codigo: int) -> Dict[str, Any]:
        with self._conectar() as conn:
            fila = conn.execute(
                """
                SELECT e.codigo, ad.nombre AS administrador_nombre,
                       e.socio_codigo, s.nombre AS socio_nombre,
                       e.mes, e.anio, e.fecha_creacion
                FROM estadisticas e
                JOIN administradores ad ON ad.codigo = e.administrador_codigo
                JOIN socios s ON s.codigo = e.socio_codigo
                WHERE e.codigo = ?
                """,
                (codigo,),
            ).fetchone()
        if not fila:
            raise ValueError(f"No existe la estadística con código {codigo}.")

        total_gastado = self._calcular_total_gastado(
            int(fila["socio_codigo"]), int(fila["mes"]), int(fila["anio"])
        )
        return {
            "codigo": fila["codigo"],
            "administrador_nombre": fila["administrador_nombre"],
            "socio_codigo": fila["socio_codigo"],
            "socio_nombre": fila["socio_nombre"],
            "mes": fila["mes"],
            "anio": fila["anio"],
            "fecha_creacion": self._iso_a_es(fila["fecha_creacion"]),
            "total_gastado": total_gastado,
        }

    def listar_estadisticas(self) -> List[Dict[str, Any]]:
        with self._conectar() as conn:
            filas = conn.execute("SELECT codigo FROM estadisticas ORDER BY codigo").fetchall()
        return [self.obtener_estadistica(int(f["codigo"])) for f in filas]

    def estado_completo(self) -> Dict[str, Any]:
        return {
            "videoclubs": self.listar_videoclubs(),
            "peliculas": self.listar_peliculas(),
            "socios": self.listar_socios(),
            "alquileres": self.listar_alquileres(),
            "administradores": self.listar_admins(),
            "estadisticas": self.listar_estadisticas(),
        }