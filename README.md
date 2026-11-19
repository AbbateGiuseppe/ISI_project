# ISI Project – Sistema de Gestión de Videoclubs (Cadena APPV)

Aplicación de consola desarrollada en Python para la gestión operativa y estadística de todos los videoclubs de la cadena **APPV**.

## Descripción del sistema

El software implementa la gestión de las seis entidades principales definidas en los requisitos del caso de estudio:

- **Videoclub**: sedes de la cadena identificadas mediante un código autonumérico, con nombre del gerente, ciudad, calle y código postal de 5 caracteres.
- **Película**: catálogo asignado a un videoclub específico, con nombre, director (opcional), fecha de estreno y precio de alquiler. Las películas con el mismo nombre en distintos videoclubs se gestionan como objetos diferentes con códigos únicos.
- **Socio**: registro de los clientes de la cadena, con derecho a alquilar películas en cualquier videoclub de APPV y no solo en el que se hayan registrado.
- **Alquiler**: registro de una o más películas con fecha de recogida (obligatoria y no editable), fecha de devolución (editable únicamente por una fecha posterior a la actual) y total a pagar calculado como atributo derivado sumando los precios de las películas incluidas.
- **Administrador**: encargados de generar los informes estadísticos mensuales.
- **Estadística**: cálculo mensual del total gastado por un socio en toda la cadena de videoclubs, con la restricción de almacenar como máximo un dato estadístico por socio en un mismo mes.

## Reglas de implementación

- **Gestión manual de fechas**: el sistema no utiliza la fecha del sistema; todas las fechas necesarias (fecha de estreno, recogida, devolución, fecha actual de validación y creación de estadística) se solicitan por pantalla para que el usuario las introduzca manualmente en formato `DD/MM/AAAA`.
- **Atributos derivados y no editables**: los códigos identificativos son autonuméricos; las fechas de recogida y de creación de estadística son de solo lectura, mientras que el total a pagar y el total gastado se calculan dinámicamente.

# ISI Project – Sistema de Gestión de Videoclubs (Cadena APPV)

Aplicación web Full-Stack (Backend en Python/Flask y Frontend en HTML/CSS/JavaScript) para la gestión operativa y estadística de todos los videoclubs de la cadena **APPV**.

## Arquitectura del proyecto

```text
ISI_project/
├── backend/
│   ├── models.py                # Entidades y reglas de negocio de APPV
│   ├── app.py                   # API REST y servidor web en Flask
│   └── requirements.txt         # Dependencias del backend
├── frontend/
│   ├── index.html               # Interfaz de usuario en español
│   ├── style.css                # Estilos de la aplicación
│   └── app.js                   # Lógica de cliente y peticiones a la API
├── sonar-project.properties     # Configuración para análisis estático en SonarQube
├── README.md
└── .gitignore
## Requisitos y ejecución

- **Python 3.8** o superior (no requiere librerías externas).

Para ejecutar el programa desde la terminal:

```bash
python APPV.py
```