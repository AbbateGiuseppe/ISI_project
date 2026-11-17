from datetime import date, datetime
from typing import List, Optional


# ==============================================================================
# FUNCIONES DE UTILIDAD PARA ENTRADA Y VALIDACIÓN DE DATOS
# ==============================================================================

def leer_texto_obligatorio(mensaje: str) -> str:
    """Lee una cadena de texto no vacía."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("Error: este campo es obligatorio.")


def leer_texto_opcional(mensaje: str) -> Optional[str]:
    """Lee una cadena de texto opcional (devuelve None si se deja vacía)."""
    valor = input(mensaje).strip()
    return valor if valor else None


def leer_codigo_postal(mensaje: str) -> str:
    """Lee un código postal de exactamente 5 caracteres."""
    while True:
        cp = input(mensaje).strip()
        if len(cp) == 5:
            return cp
        print("Error: el código postal debe tener exactamente 5 caracteres.")


def leer_entero(mensaje: str, minimo: int = 1, maximo: Optional[int] = None) -> int:
    """Lee un número entero dentro de los límites especificados."""
    while True:
        try:
            valor = int(input(mensaje).strip())
            if valor < minimo or (maximo is not None and valor > maximo):
                limite_sup = f" y {maximo}" if maximo is not None else ""
                print(f"Error: introduce un número entero >= {minimo}{limite_sup}.")
                continue
            return valor
        except ValueError:
            print("Error: introduce un número entero válido.")


def leer_real(mensaje: str, minimo: float = 0.01) -> float:
    """Lee un número real positivo."""
    while True:
        try:
            valor = float(input(mensaje).strip().replace(",", "."))
            if valor < minimo:
                print(f"Error: introduce un valor mayor o igual a {minimo}.")
                continue
            return round(valor, 2)
        except ValueError:
            print("Error: introduce un número real válido.")


def leer_fecha_manual(mensaje: str) -> date:
    """
    Solicita una fecha manualmente al usuario en formato DD/MM/AAAA.
    NO utiliza nunca la fecha del sistema.
    """
    while True:
        texto = input(mensaje).strip()
        try:
            return datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            print("Error: formato de fecha no válido. Usa DD/MM/AAAA (ej. 15/05/2026).")


# ==============================================================================
# CLASES DEL DOMINIO (CADENA APPV)
# ==============================================================================

class Videoclub:
    _contador_codigo = 1

    def __init__(self, nombre_gerente: str, ciudad: str, calle: str, codigo_postal: str):
        if len(codigo_postal) != 5:
            raise ValueError("El código postal debe tener exactamente 5 caracteres.")
        self._codigo: int = Videoclub._contador_codigo
        Videoclub._contador_codigo += 1

        self.nombre_gerente: str = nombre_gerente
        self.ciudad: str = ciudad
        self.calle: str = calle
        self.codigo_postal: str = codigo_postal
        self.peliculas: List["Pelicula"] = []

    @property
    def codigo(self) -> int:
        return self._codigo

    def __str__(self) -> str:
        return (
            f"[Videoclub #{self.codigo}] Gerente: {self.nombre_gerente} | "
            f"Dirección: {self.calle}, {self.ciudad} (CP: {self.codigo_postal})"
        )


class Pelicula:
    _contador_codigo = 1

    def __init__(
        self,
        nombre: str,
        fecha_estreno: date,
        precio_alquiler: float,
        videoclub: Videoclub,
        director: Optional[str] = None,
    ):
        self._codigo: int = Pelicula._contador_codigo
        Pelicula._contador_codigo += 1

        self.nombre: str = nombre
        self.director: Optional[str] = director
        self.fecha_estreno: date = fecha_estreno
        self.precio_alquiler: float = precio_alquiler
        self.videoclub: Videoclub = videoclub
        videoclub.peliculas.append(self)

    @property
    def codigo(self) -> int:
        return self._codigo

    def __str__(self) -> str:
        director_str = self.director if self.director else "No especificado"
        return (
            f"[Película #{self.codigo}] '{self.nombre}' | Director: {director_str} | "
            f"Estreno: {self.fecha_estreno.strftime('%d/%m/%Y')} | "
            f"Precio: {self.precio_alquiler:.2f} € | Videoclub #{self.videoclub.codigo}"
        )


class Socio:
    _contador_codigo = 1

    def __init__(self, nombre: str, edad: int):
        self._codigo: int = Socio._contador_codigo
        Socio._contador_codigo += 1

        self.nombre: str = nombre
        self.edad: int = edad
        self.alquileres: List["Alquiler"] = []

    @property
    def codigo(self) -> int:
        return self._codigo

    def __str__(self) -> str:
        return f"[Socio #{self.codigo}] Nombre: {self.nombre} | Edad: {self.edad}"


class Alquiler:
    _contador_codigo = 1

    def __init__(
        self,
        socio: Socio,
        peliculas: List[Pelicula],
        fecha_recogida: date,
        fecha_devolucion: date,
    ):
        if not peliculas:
            raise ValueError("Un alquiler debe incluir al menos una película.")
        if fecha_devolucion <= fecha_recogida:
            raise ValueError("La fecha de devolución debe ser posterior a la fecha de recogida.")

        self._codigo: int = Alquiler._contador_codigo
        Alquiler._contador_codigo += 1

        self.socio: Socio = socio
        self.peliculas: List[Pelicula] = list(peliculas)
        # Obligatoria y no editable tras su creación
        self._fecha_recogida: date = fecha_recogida
        # Obligatoria y editable mediante método con validación
        self._fecha_devolucion: date = fecha_devolucion

        socio.alquileres.append(self)

    @property
    def codigo(self) -> int:
        return self._codigo

    @property
    def fecha_recogida(self) -> date:
        return self._fecha_recogida

    @property
    def fecha_devolucion(self) -> date:
        return self._fecha_devolucion

    def modificar_fecha_devolucion(self, nueva_fecha: date, fecha_actual: date) -> None:
        """
        Modifica la fecha de devolución comprobando que sea estrictamente
        posterior a la fecha actual introducida manualmente por el usuario.
        """
        if nueva_fecha <= fecha_actual:
            raise ValueError(
                "La nueva fecha de devolución debe ser posterior a la fecha actual."
            )
        self._fecha_devolucion = nueva_fecha

    @property
    def total_pagar(self) -> float:
        """Atributo derivado: suma de los precios de alquiler de las películas incluidas."""
        return round(sum(p.precio_alquiler for p in self.peliculas), 2)

    def __str__(self) -> str:
        titulos = ", ".join(f"'{p.nombre}' (#{p.codigo})" for p in self.peliculas)
        return (
            f"[Alquiler #{self.codigo}] Socio: {self.socio.nombre} (#{self.socio.codigo}) | "
            f"Recogida: {self.fecha_recogida.strftime('%d/%m/%Y')} | "
            f"Devolución: {self.fecha_devolucion.strftime('%d/%m/%Y')} | "
            f"Total a pagar: {self.total_pagar:.2f} €\n   Películas incluidas: {titulos}"
        )


class Administrador:
    _contador_codigo = 1

    def __init__(self, nombre: str):
        self._codigo: int = Administrador._contador_codigo
        Administrador._contador_codigo += 1
        self.nombre: str = nombre

    @property
    def codigo(self) -> int:
        return self._codigo

    def __str__(self) -> str:
        return f"[Administrador #{self.codigo}] Nombre: {self.nombre}"


class Estadistica:
    _contador_codigo = 1

    def __init__(
        self,
        administrador: Administrador,
        socio: Socio,
        mes: int,
        anio: int,
        fecha_creacion: date,
    ):
        self._codigo: int = Estadistica._contador_codigo
        Estadistica._contador_codigo += 1

        self.administrador: Administrador = administrador
        self.socio: Socio = socio
        self.mes: int = mes
        self.anio: int = anio
        # Obligatoria y no editable tras su creación
        self._fecha_creacion: date = fecha_creacion

    @property
    def codigo(self) -> int:
        return self._codigo

    @property
    def fecha_creacion(self) -> date:
        return self._fecha_creacion

    @property
    def total_gastado(self) -> float:
        """Atributo derivado: total de euros gastados por el socio en el mes y año indicados."""
        return round(
            sum(
                alq.total_pagar
                for alq in self.socio.alquileres
                if alq.fecha_recogida.month == self.mes
                and alq.fecha_recogida.year == self.anio
            ),
            2,
        )

    def __str__(self) -> str:
        return (
            f"[Estadística #{self.codigo}] Socio: {self.socio.nombre} (#{self.socio.codigo}) | "
            f"Periodo: {self.mes:02d}/{self.anio} | Total gastado: {self.total_gastado:.2f} € | "
            f"Creada el: {self.fecha_creacion.strftime('%d/%m/%Y')} por {self.administrador.nombre}"
        )


# ==============================================================================
# GESTOR DE LA CADENA APPV
# ==============================================================================

class SistemaAPPV:
    def __init__(self):
        self.videoclubs: List[Videoclub] = []
        self.peliculas: List[Pelicula] = []
        self.socios: List[Socio] = []
        self.alquileres: List[Alquiler] = []
        self.administradores: List[Administrador] = []
        self.estadisticas: List[Estadistica] = []

    # --- Métodos de búsqueda ---
    def buscar_videoclub(self, codigo: int) -> Optional[Videoclub]:
        return next((v for v in self.videoclubs if v.codigo == codigo), None)

    def buscar_pelicula(self, codigo: int) -> Optional[Pelicula]:
        return next((p for p in self.peliculas if p.codigo == codigo), None)

    def buscar_socio(self, codigo: int) -> Optional[Socio]:
        return next((s for s in self.socios if s.codigo == codigo), None)

    def buscar_alquiler(self, codigo: int) -> Optional[Alquiler]:
        return next((a for a in self.alquileres if a.codigo == codigo), None)

    def buscar_admin(self, codigo: int) -> Optional[Administrador]:
        return next((ad for ad in self.administradores if ad.codigo == codigo), None)

    # --- Videoclubs ---
    def crear_videoclub(self) -> None:
        print("\n--- Nuevo Videoclub ---")
        gerente = leer_texto_obligatorio("Nombre del gerente: ")
        ciudad = leer_texto_obligatorio("Ciudad: ")
        calle = leer_texto_obligatorio("Calle: ")
        cp = leer_codigo_postal("Código postal (5 caracteres): ")
        vc = Videoclub(gerente, ciudad, calle, cp)
        self.videoclubs.append(vc)
        print(f"Videoclub creado correctamente: {vc}")

    def editar_videoclub(self) -> None:
        if not self.videoclubs:
            print("No hay videoclubs registrados.")
            return
        for v in self.videoclubs:
            print(v)
        vc = self.buscar_videoclub(leer_entero("Código del videoclub a modificar: "))
        if not vc:
            print("Videoclub no encontrado.")
            return
        vc.nombre_gerente = leer_texto_obligatorio("Nuevo nombre del gerente: ")
        vc.ciudad = leer_texto_obligatorio("Nueva ciudad: ")
        vc.calle = leer_texto_obligatorio("Nueva calle: ")
        vc.codigo_postal = leer_codigo_postal("Nuevo código postal (5 caracteres): ")
        print(f"Videoclub actualizado: {vc}")

    # --- Películas ---
    def crear_pelicula(self) -> None:
        if not self.videoclubs:
            print("Error: primero debes crear al menos un videoclub al que asignar la película.")
            return
        print("\n--- Nueva Película ---")
        for v in self.videoclubs:
            print(v)
        vc = self.buscar_videoclub(leer_entero("Código del videoclub de asignación: "))
        if not vc:
            print("Videoclub no encontrado.")
            return
        nombre = leer_texto_obligatorio("Nombre de la película: ")
        director = leer_texto_opcional("Director (opcional, pulsa Enter para omitir): ")
        fecha_estreno = leer_fecha_manual("Fecha de estreno (DD/MM/AAAA): ")
        precio = leer_real("Precio de alquiler (€): ")
        pelicula = Pelicula(nombre, fecha_estreno, precio, vc, director)
        self.peliculas.append(pelicula)
        print(f"Película creada correctamente: {pelicula}")

    def editar_pelicula(self) -> None:
        if not self.peliculas:
            print("No hay películas registradas.")
            return
        for p in self.peliculas:
            print(p)
        pelicula = self.buscar_pelicula(leer_entero("Código de la película a modificar: "))
        if not pelicula:
            print("Película no encontrada.")
            return
        pelicula.nombre = leer_texto_obligatorio("Nuevo nombre: ")
        pelicula.director = leer_texto_opcional("Nuevo director (opcional): ")
        pelicula.fecha_estreno = leer_fecha_manual("Nueva fecha de estreno (DD/MM/AAAA): ")
        pelicula.precio_alquiler = leer_real("Nuevo precio de alquiler (€): ")
        print(f"Película actualizada: {pelicula}")

    # --- Socios ---
    def crear_socio(self) -> None:
        print("\n--- Registro de Socio ---")
        nombre = leer_texto_obligatorio("Nombre del socio: ")
        edad = leer_entero("Edad: ", minimo=1)
        socio = Socio(nombre, edad)
        self.socios.append(socio)
        print(f"Socio registrado correctamente: {socio}")

    def editar_socio(self) -> None:
        if not self.socios:
            print("No hay socios registrados.")
            return
        for s in self.socios:
            print(s)
        socio = self.buscar_socio(leer_entero("Código del socio a modificar: "))
        if not socio:
            print("Socio no encontrado.")
            return
        socio.nombre = leer_texto_obligatorio("Nuevo nombre: ")
        socio.edad = leer_entero("Nueva edad: ", minimo=1)
        print(f"Socio actualizado: {socio}")

    # --- Alquileres ---
    def crear_alquiler(self) -> None:
        if not self.socios or not self.peliculas:
            print("Error: se necesita al menos un socio y una película registrados.")
            return
        print("\n--- Nuevo Alquiler ---")
        for s in self.socios:
            print(s)
        socio = self.buscar_socio(leer_entero("Código del socio: "))
        if not socio:
            print("Socio no encontrado.")
            return

        print("\nPelículas disponibles en la cadena APPV:")
        for p in self.peliculas:
            print(p)

        peliculas_seleccionadas: List[Pelicula] = []
        while True:
            cod_p = leer_entero("Introduce el código de la película a añadir (0 para finalizar): ", minimo=0)
            if cod_p == 0:
                if not peliculas_seleccionadas:
                    print("Debes seleccionar al menos una película.")
                    continue
                break
            pelicula = self.buscar_pelicula(cod_p)
            if not pelicula:
                print("Película no encontrada.")
            elif pelicula in peliculas_seleccionadas:
                print("Esa película ya está incluida en este alquiler.")
            else:
                peliculas_seleccionadas.append(pelicula)
                print(f"Añadida: '{pelicula.nombre}' ({pelicula.precio_alquiler:.2f} €)")

        fecha_recogida = leer_fecha_manual("Fecha de recogida (DD/MM/AAAA): ")
        while True:
            fecha_devolucion = leer_fecha_manual("Fecha de devolución (DD/MM/AAAA): ")
            if fecha_devolucion > fecha_recogida:
                break
            print("Error: la fecha de devolución debe ser posterior a la fecha de recogida.")

        alquiler = Alquiler(socio, peliculas_seleccionadas, fecha_recogida, fecha_devolucion)
        self.alquileres.append(alquiler)
        print(f"\nAlquiler registrado:\n{alquiler}")

    def editar_fecha_devolucion_alquiler(self) -> None:
        if not self.alquileres:
            print("No hay alquileres registrados.")
            return
        for a in self.alquileres:
            print(a)
        alquiler = self.buscar_alquiler(leer_entero("Código del alquiler a modificar: "))
        if not alquiler:
            print("Alquiler no encontrado.")
            return

        fecha_actual = leer_fecha_manual("Introduce la fecha actual (DD/MM/AAAA): ")
        nueva_fecha = leer_fecha_manual("Introduce la nueva fecha de devolución (DD/MM/AAAA): ")
        try:
            alquiler.modificar_fecha_devolucion(nueva_fecha, fecha_actual)
            print(f"Fecha de devolución actualizada:\n{alquiler}")
        except ValueError as e:
            print(f"Error: {e}")

    # --- Administradores ---
    def crear_admin(self) -> None:
        print("\n--- Nuevo Administrador ---")
        nombre = leer_texto_obligatorio("Nombre del administrador: ")
        admin = Administrador(nombre)
        self.administradores.append(admin)
        print(f"Administrador creado correctamente: {admin}")

    def editar_admin(self) -> None:
        if not self.administradores:
            print("No hay administradores registrados.")
            return
        for ad in self.administradores:
            print(ad)
        admin = self.buscar_admin(leer_entero("Código del administrador a modificar: "))
        if not admin:
            print("Administrador no encontrado.")
            return
        admin.nombre = leer_texto_obligatorio("Nuevo nombre: ")
        print(f"Administrador actualizado: {admin}")

    # --- Estadísticas ---
    def generar_estadistica(self) -> None:
        if not self.administradores or not self.socios:
            print("Error: se necesita al menos un administrador y un socio registrados.")
            return
        print("\n--- Cálculo de Estadística Mensual por Socio ---")
        for ad in self.administradores:
            print(ad)
        admin = self.buscar_admin(leer_entero("Código del administrador: "))
        if not admin:
            print("Administrador no encontrado.")
            return

        for s in self.socios:
            print(s)
        socio = self.buscar_socio(leer_entero("Código del socio: "))
        if not socio:
            print("Socio no encontrado.")
            return

        mes = leer_entero("Mes a consultar (1-12): ", minimo=1, maximo=12)
        anio = leer_entero("Año a consultar (ej. 2026): ", minimo=1900, maximo=2100)

        # Restricción: máximo un dato estadístico por socio en un mismo mes
        ya_existe = any(
            e.socio.codigo == socio.codigo and e.mes == mes and e.anio == anio
            for e in self.estadisticas
        )
        if ya_existe:
            print(
                f"Error: ya existe un dato estadístico para el socio '{socio.nombre}' "
                f"en el mes {mes:02d}/{anio}."
            )
            return

        fecha_creacion = leer_fecha_manual("Fecha de creación de la estadística (DD/MM/AAAA): ")
        est = Estadistica(admin, socio, mes, anio, fecha_creacion)
        self.estadisticas.append(est)
        print(f"Estadística generada:\n{est}")

    # --- Visualización completa ---
    def mostrar_todo(self) -> None:
        print("\n================ ESTADO DE LA CADENA APPV ================")
        print("\n[VIDEOCLUBS]")
        print("\n".join(str(v) for v in self.videoclubs) or "Ninguno")
        print("\n[PELÍCULAS]")
        print("\n".join(str(p) for p in self.peliculas) or "Ninguna")
        print("\n[SOCIOS]")
        print("\n".join(str(s) for s in self.socios) or "Ninguno")
        print("\n[ALQUILERES]")
        print("\n".join(str(a) for a in self.alquileres) or "Ninguno")
        print("\n[ADMINISTRADORES]")
        print("\n".join(str(ad) for ad in self.administradores) or "Ninguno")
        print("\n[ESTADÍSTICAS]")
        print("\n".join(str(e) for e in self.estadisticas) or "Ninguna")
        print("==========================================================")


# ==============================================================================
# MENÚ PRINCIPAL
# ==============================================================================

def main() -> None:
    sistema = SistemaAPPV()

    while True:
        print("\n--- GESTIÓN DE VIDEOCLUBS APPV ---")
        print("1. Crear Videoclub")
        print("2. Modificar Videoclub")
        print("3. Crear Película (asignada a un Videoclub)")
        print("4. Modificar Película")
        print("5. Registrar Socio")
        print("6. Modificar Socio")
        print("7. Registrar Alquiler")
        print("8. Modificar Fecha de Devolución de Alquiler")
        print("9. Crear Administrador")
        print("10. Modificar Administrador")
        print("11. Generar Estadística Mensual por Socio")
        print("12. Mostrar todos los datos del sistema")
        print("0. Salir")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            sistema.crear_videoclub()
        elif opcion == "2":
            sistema.editar_videoclub()
        elif opcion == "3":
            sistema.crear_pelicula()
        elif opcion == "4":
            sistema.editar_pelicula()
        elif opcion == "5":
            sistema.crear_socio()
        elif opcion == "6":
            sistema.editar_socio()
        elif opcion == "7":
            sistema.crear_alquiler()
        elif opcion == "8":
            sistema.editar_fecha_devolucion_alquiler()
        elif opcion == "9":
            sistema.crear_admin()
        elif opcion == "10":
            sistema.editar_admin()
        elif opcion == "11":
            sistema.generar_estadistica()
        elif opcion == "12":
            sistema.mostrar_todo()
        elif opcion == "0":
            print("Cerrando el sistema APPV.")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()