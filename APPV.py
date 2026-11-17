from datetime import date, datetime
from typing import List, Optional


# ==============================================================================
# FUNZIONI DI UTILITÀ PER INPUT E VALIDAZIONE
# ==============================================================================

def leer_texto_obligatorio(mensaje: str) -> str:
    """Legge una stringa non vuota."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("Errore: questo campo è obbligatorio.")


def leer_texto_opcional(mensaje: str) -> Optional[str]:
    """Legge una stringa opzionale (restituisce None se lasciata vuota)."""
    valor = input(mensaje).strip()
    return valor if valor else None


def leer_codigo_postal(mensaje: str) -> str:
    """Legge un codice postale di esattamente 5 caratteri."""
    while True:
        cp = input(mensaje).strip()
        if len(cp) == 5:
            return cp
        print("Errore: il codice postale deve avere esattamente 5 caratteri.")


def leer_entero(mensaje: str, minimo: int = 1, maximo: Optional[int] = None) -> int:
    """Legge un numero intero entro i limiti specificati."""
    while True:
        try:
            valor = int(input(mensaje).strip())
            if valor < minimo or (maximo is not None and valor > maximo):
                limite_sup = f" e {maximo}" if maximo is not None else ""
                print(f"Errore: inserisci un numero intero >= {minimo}{limite_sup}.")
                continue
            return valor
        except ValueError:
            print("Errore: inserisci un numero intero valido.")


def leer_real(mensaje: str, minimo: float = 0.01) -> float:
    """Legge un numero reale positivo."""
    while True:
        try:
            valor = float(input(mensaje).strip().replace(",", "."))
            if valor < minimo:
                print(f"Errore: inserisci un valore maggiore o uguale a {minimo}.")
                continue
            return round(valor, 2)
        except ValueError:
            print("Errore: inserisci un numero reale valido.")


def leer_fecha_manual(mensaje: str) -> date:
    """
    Richiede una data manualmente all'utente in formato GG/MM/AAAA.
    NON utilizza mai la data di sistema.
    """
    while True:
        texto = input(mensaje).strip()
        try:
            return datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            print("Errore: formato data non valido. Usa GG/MM/AAAA (es. 15/05/2026).")


# ==============================================================================
# CLASSI DEL DOMINIO (APPV)
# ==============================================================================

class Videoclub:
    _contador_codigo = 1

    def __init__(self, nombre_gerente: str, ciudad: str, calle: str, codigo_postal: str):
        if len(codigo_postal) != 5:
            raise ValueError("Il codice postale deve avere esattamente 5 caratteri.")
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
            f"Indirizzo: {self.calle}, {self.ciudad} (CP: {self.codigo_postal})"
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
        dir_str = self.director if self.director else "Non specificato"
        return (
            f"[Film #{self.codigo}] '{self.nombre}' | Regista: {dir_str} | "
            f"Uscita: {self.fecha_estreno.strftime('%d/%m/%Y')} | "
            f"Prezzo: {self.precio_alquiler:.2f} € | Videoclub #{self.videoclub.codigo}"
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
        return f"[Socio #{self.codigo}] Nome: {self.nombre} | Età: {self.edad}"


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
            raise ValueError("Un noleggio deve contenere almeno un film.")
        if fecha_devolucion <= fecha_recogida:
            raise ValueError("La data di restituzione deve essere successiva a quella di ritiro.")

        self._codigo: int = Alquiler._contador_codigo
        Alquiler._contador_codigo += 1

        self.socio: Socio = socio
        self.peliculas: List[Pelicula] = list(peliculas)
        # Non modificabile dopo la creazione
        self._fecha_recogida: date = fecha_recogida
        # Modificabile tramite metodo dedicato
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
        Modifica la data di restituzione verificando che sia strettamente
        successiva alla data attuale inserita manualmente dall'utente.
        """
        if nueva_fecha <= fecha_actual:
            raise ValueError(
                "La nuova data di restituzione deve essere successiva alla data attuale."
            )
        self._fecha_devolucion = nueva_fecha

    @property
    def total_pagar(self) -> float:
        """Attributo derivato: somma dei prezzi di noleggio dei film inclusi."""
        return round(sum(p.precio_alquiler for p in self.peliculas), 2)

    def __str__(self) -> str:
        titoli = ", ".join(f"'{p.nombre}' (#{p.codigo})" for p in self.peliculas)
        return (
            f"[Noleggio #{self.codigo}] Socio: {self.socio.nombre} (#{self.socio.codigo}) | "
            f"Ritiro: {self.fecha_recogida.strftime('%d/%m/%Y')} | "
            f"Restituzione: {self.fecha_devolucion.strftime('%d/%m/%Y')} | "
            f"Totale: {self.total_pagar:.2f} €\n   Film inclusi: {titoli}"
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
        return f"[Admin #{self.codigo}] Nome: {self.nombre}"


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
        # Non modificabile dopo la creazione
        self._fecha_creacion: date = fecha_creacion

    @property
    def codigo(self) -> int:
        return self._codigo

    @property
    def fecha_creacion(self) -> date:
        return self._fecha_creacion

    @property
    def total_gastado(self) -> float:
        """Attributo derivato: totale speso dal socio nel mese e anno selezionati."""
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
            f"[Statistica #{self.codigo}] Socio: {self.socio.nombre} (#{self.socio.codigo}) | "
            f"Periodo: {self.mes:02d}/{self.anio} | Totale speso: {self.total_gastado:.2f} € | "
            f"Creata il: {self.fecha_creacion.strftime('%d/%m/%Y')} da {self.administrador.nombre}"
        )


# ==============================================================================
# GESTORE DELLA CATENA APPV
# ==============================================================================

class SistemaAPPV:
    def __init__(self):
        self.videoclubs: List[Videoclub] = []
        self.peliculas: List[Pelicula] = []
        self.socios: List[Socio] = []
        self.alquileres: List[Alquiler] = []
        self.administradores: List[Administrador] = []
        self.estadisticas: List[Estadistica] = []

    # --- Metodi di ricerca ---
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

    # --- Videoclub ---
    def crear_videoclub(self) -> None:
        print("\n--- Nuovo Videoclub ---")
        gerente = leer_texto_obligatorio("Nome del gerente: ")
        ciudad = leer_texto_obligatorio("Città: ")
        calle = leer_texto_obligatorio("Via/Indirizzo: ")
        cp = leer_codigo_postal("Codice postale (5 caratteri): ")
        vc = Videoclub(gerente, ciudad, calle, cp)
        self.videoclubs.append(vc)
        print(f"Creato con successo: {vc}")

    def editar_videoclub(self) -> None:
        if not self.videoclubs:
            print("Nessun videoclub registrato.")
            return
        for v in self.videoclubs:
            print(v)
        vc = self.buscar_videoclub(leer_entero("Codice del videoclub da modificare: "))
        if not vc:
            print("Videoclub non trovato.")
            return
        vc.nombre_gerente = leer_texto_obligatorio("Nuovo nome gerente: ")
        vc.ciudad = leer_texto_obligatorio("Nuova città: ")
        vc.calle = leer_texto_obligatorio("Nuova via: ")
        vc.codigo_postal = leer_codigo_postal("Nuovo codice postale (5 caratteri): ")
        print(f"Aggiornato: {vc}")

    # --- Películas ---
    def crear_pelicula(self) -> None:
        if not self.videoclubs:
            print("Errore: devi prima creare almeno un videoclub a cui assegnare il film.")
            return
        print("\n--- Nuovo Film ---")
        for v in self.videoclubs:
            print(v)
        vc = self.buscar_videoclub(leer_entero("Codice del videoclub di assegnazione: "))
        if not vc:
            print("Videoclub non trovato.")
            return
        nombre = leer_texto_obligatorio("Titolo del film: ")
        director = leer_texto_opcional("Regista (opzionale, premi Invio per saltare): ")
        fecha_estreno = leer_fecha_manual("Data di uscita (GG/MM/AAAA): ")
        precio = leer_real("Prezzo di noleggio (€): ")
        peli = Pelicula(nombre, fecha_estreno, precio, vc, director)
        self.peliculas.append(peli)
        print(f"Creato con successo: {peli}")

    def editar_pelicula(self) -> None:
        if not self.peliculas:
            print("Nessun film registrato.")
            return
        for p in self.peliculas:
            print(p)
        peli = self.buscar_pelicula(leer_entero("Codice del film da modificare: "))
        if not peli:
            print("Film non trovato.")
            return
        peli.nombre = leer_texto_obligatorio("Nuovo titolo: ")
        peli.director = leer_texto_opcional("Nuovo regista (opzionale): ")
        peli.fecha_estreno = leer_fecha_manual("Nuova data di uscita (GG/MM/AAAA): ")
        peli.precio_alquiler = leer_real("Nuovo prezzo di noleggio (€): ")
        print(f"Aggiornato: {peli}")

    # --- Socios ---
    def crear_socio(self) -> None:
        print("\n--- Registrazione Socio ---")
        nombre = leer_texto_obligatorio("Nome del socio: ")
        edad = leer_entero("Età: ", minimo=1)
        socio = Socio(nombre, edad)
        self.socios.append(socio)
        print(f"Registrato con successo: {socio}")

    def editar_socio(self) -> None:
        if not self.socios:
            print("Nessun socio registrato.")
            return
        for s in self.socios:
            print(s)
        socio = self.buscar_socio(leer_entero("Codice del socio da modificare: "))
        if not socio:
            print("Socio non trovato.")
            return
        socio.nombre = leer_texto_obligatorio("Nuovo nome: ")
        socio.edad = leer_entero("Nuova età: ", minimo=1)
        print(f"Aggiornato: {socio}")

    # --- Alquileres ---
    def crear_alquiler(self) -> None:
        if not self.socios or not self.peliculas:
            print("Errore: servono almeno un socio e un film registrati.")
            return
        print("\n--- Nuovo Noleggio ---")
        for s in self.socios:
            print(s)
        socio = self.buscar_socio(leer_entero("Codice del socio: "))
        if not socio:
            print("Socio non trovato.")
            return

        print("\nFilm disponibili nella catena APPV:")
        for p in self.peliculas:
            print(p)

        peliculas_seleccionadas: List[Pelicula] = []
        while True:
            cod_p = leer_entero("Inserisci il codice del film da aggiungere (0 per terminare): ", minimo=0)
            if cod_p == 0:
                if not peliculas_seleccionadas:
                    print("Devi selezionare almeno un film.")
                    continue
                break
            peli = self.buscar_pelicula(cod_p)
            if not peli:
                print("Film non trovato.")
            elif peli in peliculas_seleccionadas:
                print("Film già inserito in questo noleggio.")
            else:
                peliculas_seleccionadas.append(peli)
                print(f"Aggiunto: '{peli.nombre}' ({peli.precio_alquiler:.2f} €)")

        fecha_recogida = leer_fecha_manual("Data di ritiro (GG/MM/AAAA): ")
        while True:
            fecha_devolucion = leer_fecha_manual("Data di restituzione (GG/MM/AAAA): ")
            if fecha_devolucion > fecha_recogida:
                break
            print("Errore: la data di restituzione deve essere successiva a quella di ritiro.")

        alquiler = Alquiler(socio, peliculas_seleccionadas, fecha_recogida, fecha_devolucion)
        self.alquileres.append(alquiler)
        print(f"\nNoleggio registrato:\n{alquiler}")

    def editar_fecha_devolucion_alquiler(self) -> None:
        if not self.alquileres:
            print("Nessun noleggio registrato.")
            return
        for a in self.alquileres:
            print(a)
        alquiler = self.buscar_alquiler(leer_entero("Codice del noleggio da modificare: "))
        if not alquiler:
            print("Noleggio non trovato.")
            return

        fecha_actual = leer_fecha_manual("Inserisci la data attuale (GG/MM/AAAA): ")
        nueva_fecha = leer_fecha_manual("Inserisci la nuova data di restituzione (GG/MM/AAAA): ")
        try:
            alquiler.modificar_fecha_devolucion(nueva_fecha, fecha_actual)
            print(f"Data di restituzione aggiornata:\n{alquiler}")
        except ValueError as e:
            print(f"Errore: {e}")

    # --- Administradores ---
    def crear_admin(self) -> None:
        print("\n--- Nuovo Amministratore ---")
        nombre = leer_texto_obligatorio("Nome dell'amministratore: ")
        admin = Administrador(nombre)
        self.administradores.append(admin)
        print(f"Creato con successo: {admin}")

    def editar_admin(self) -> None:
        if not self.administradores:
            print("Nessun amministratore registrato.")
            return
        for ad in self.administradores:
            print(ad)
        admin = self.buscar_admin(leer_entero("Codice dell'amministratore da modificare: "))
        if not admin:
            print("Amministratore non trovato.")
            return
        admin.nombre = leer_texto_obligatorio("Nuovo nome: ")
        print(f"Aggiornato: {admin}")

    # --- Estadísticas ---
    def generar_estadistica(self) -> None:
        if not self.administradores or not self.socios:
            print("Errore: servono almeno un amministratore e un socio registrati.")
            return
        print("\n--- Calcolo Statistica Mensile per Socio ---")
        for ad in self.administradores:
            print(ad)
        admin = self.buscar_admin(leer_entero("Codice dell'amministratore: "))
        if not admin:
            print("Amministratore non trovato.")
            return

        for s in self.socios:
            print(s)
        socio = self.buscar_socio(leer_entero("Codice del socio: "))
        if not socio:
            print("Socio non trovato.")
            return

        mes = leer_entero("Mese di riferimento (1-12): ", minimo=1, maximo=12)
        anio = leer_entero("Anno di riferimento (es. 2026): ", minimo=1900, maximo=2100)

        # Vincolo: massimo 1 dato statistico per socio in uno stesso mese
        ya_existe = any(
            e.socio.codigo == socio.codigo and e.mes == mes and e.anio == anio
            for e in self.estadisticas
        )
        if ya_existe:
            print(
                f"Errore: esiste già una statistica per il socio '{socio.nombre}' "
                f"nel mese {mes:02d}/{anio}."
            )
            return

        fecha_creacion = leer_fecha_manual("Data di creazione della statistica (GG/MM/AAAA): ")
        est = Estadistica(admin, socio, mes, anio, fecha_creacion)
        self.estadisticas.append(est)
        print(f"Statistica generata:\n{est}")

    # --- Visualizzazione completa ---
    def mostrar_todo(self) -> None:
        print("\n================ STATO CATENA APPV ================")
        print("\n[VIDEOCLUB]")
        print("\n".join(str(v) for v in self.videoclubs) or "Nessuno")
        print("\n[FILM]")
        print("\n".join(str(p) for p in self.peliculas) or "Nessuno")
        print("\n[SOCI]")
        print("\n".join(str(s) for s in self.socios) or "Nessuno")
        print("\n[NOLEGGI]")
        print("\n".join(str(a) for a in self.alquileres) or "Nessuno")
        print("\n[AMMINISTRATORI]")
        print("\n".join(str(ad) for ad in self.administradores) or "Nessuno")
        print("\n[STATISTICHE]")
        print("\n".join(str(e) for e in self.estadisticas) or "Nessuna")
        print("===================================================")


# ==============================================================================
# MENU PRINCIPALE
# ==============================================================================

def main() -> None:
    sistema = SistemaAPPV()

    while True:
        print("\n--- GESTIONE CATENA VIDEOCLUB APPV ---")
        print("1. Crea Videoclub")
        print("2. Modifica Videoclub")
        print("3. Crea Film (assegnato a un Videoclub)")
        print("4. Modifica Film")
        print("5. Registra Socio")
        print("6. Modifica Socio")
        print("7. Registra Noleggio")
        print("8. Modifica Data Restituzione Noleggio")
        print("9. Crea Amministratore")
        print("10. Modifica Amministratore")
        print("11. Genera Statistica Mensile Socio")
        print("12. Visualizza tutti i dati del sistema")
        print("0. Esci")

        opcion = input("Seleziona un'opzione: ").strip()

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
            print("Chiusura del sistema APPV.")
            break
        else:
            print("Opzione non valida.")


if __name__ == "__main__":
    main()