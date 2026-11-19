const notificacionEl = document.getElementById("notificacion");

function mostrarNotificacion(mensaje, esError = false) {
  notificacionEl.textContent = mensaje;
  notificacionEl.className = `notificacion ${esError ? "error" : "exito"}`;
}

async function enviarPeticion(url, metodo, cuerpo = null) {
  const opciones = {
    method: metodo,
    headers: { "Content-Type": "application/json" },
  };
  if (cuerpo !== null) {
    opciones.body = JSON.stringify(cuerpo);
  }
  const respuesta = await fetch(url, opciones);
  const datos = await respuesta.json();
  if (!respuesta.ok) {
    throw new Error(datos.error || "Error al procesar la solicitud.");
  }
  return datos;
}

function renderizarLista(idLista, elementos, formateador) {
  const lista = document.getElementById(idLista);
  lista.innerHTML = "";
  if (elementos.length === 0) {
    const itemVacio = document.createElement("li");
    itemVacio.textContent = "Sin registros.";
    lista.appendChild(itemVacio);
    return;
  }
  elementos.forEach((elem) => {
    const li = document.createElement("li");
    li.textContent = formateador(elem);
    lista.appendChild(li);
  });
}

async function cargarEstado() {
  const estado = await enviarPeticion("/api/estado", "GET");

  renderizarLista(
    "lista-videoclubs",
    estado.videoclubs,
    (v) => `#${v.codigo} | Gerente: ${v.nombre_gerente} | ${v.calle}, ${v.ciudad} (CP: ${v.codigo_postal})`
  );

  renderizarLista(
    "lista-peliculas",
    estado.peliculas,
    (p) =>
      `#${p.codigo} '${p.nombre}' | Dir: ${p.director || "N/A"} | Estreno: ${p.fecha_estreno} | ${p.precio_alquiler.toFixed(2)} € | Videoclub #${p.videoclub_codigo} (${p.videoclub_ciudad})`
  );

  renderizarLista(
    "lista-socios",
    estado.socios,
    (s) => `#${s.codigo} | ${s.nombre} (${s.edad} años)`
  );

  renderizarLista("lista-alquileres", estado.alquileres, (a) => {
    const titulos = a.peliculas.map((p) => `'${p.nombre}' (#${p.codigo})`).join(", ");
    return `#${a.codigo} | Socio: ${a.socio_nombre} (#${a.socio_codigo}) | Recogida: ${a.fecha_recogida} | Devolución: ${a.fecha_devolucion} | Total: ${a.total_pagar.toFixed(2)} € | Películas: ${titulos}`;
  });

  renderizarLista(
    "lista-admins",
    estado.administradores,
    (ad) => `#${ad.codigo} | ${ad.nombre}`
  );

  renderizarLista(
    "lista-estadisticas",
    estado.estadisticas,
    (e) =>
      `#${e.codigo} | Socio: ${e.socio_nombre} (#${e.socio_codigo}) | Periodo: ${String(e.mes).padStart(2, "0")}/${e.anio} | Total gastado: ${e.total_gastado.toFixed(2)} € | Creada: ${e.fecha_creacion} por ${e.administrador_nombre}`
  );
}

function registrarFormulario(idFormulario, accion, mensajeExito) {
  const formulario = document.getElementById(idFormulario);
  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    try {
      await accion();
      formulario.reset();
      await cargarEstado();
      mostrarNotificacion(mensajeExito);
    } catch (error) {
      mostrarNotificacion(error.message, true);
    }
  });
}

// Videoclubs
registrarFormulario(
  "form-videoclub",
  () =>
    enviarPeticion("/api/videoclubs", "POST", {
      nombre_gerente: document.getElementById("vc-gerente").value,
      ciudad: document.getElementById("vc-ciudad").value,
      calle: document.getElementById("vc-calle").value,
      codigo_postal: document.getElementById("vc-cp").value,
    }),
  "Videoclub creado correctamente."
);

registrarFormulario(
  "form-editar-videoclub",
  () => {
    const codigo = document.getElementById("vc-edit-codigo").value;
    return enviarPeticion(`/api/videoclubs/${codigo}`, "PUT", {
      nombre_gerente: document.getElementById("vc-edit-gerente").value,
      ciudad: document.getElementById("vc-edit-ciudad").value,
      calle: document.getElementById("vc-edit-calle").value,
      codigo_postal: document.getElementById("vc-edit-cp").value,
    });
  },
  "Videoclub actualizado correctamente."
);

// Películas
registrarFormulario(
  "form-pelicula",
  () =>
    enviarPeticion("/api/peliculas", "POST", {
      videoclub_codigo: Number(document.getElementById("pel-vc").value),
      nombre: document.getElementById("pel-nombre").value,
      director: document.getElementById("pel-director").value,
      fecha_estreno: document.getElementById("pel-estreno").value,
      precio_alquiler: Number(document.getElementById("pel-precio").value),
    }),
  "Película creada correctamente."
);

registrarFormulario(
  "form-editar-pelicula",
  () => {
    const codigo = document.getElementById("pel-edit-codigo").value;
    return enviarPeticion(`/api/peliculas/${codigo}`, "PUT", {
      nombre: document.getElementById("pel-edit-nombre").value,
      director: document.getElementById("pel-edit-director").value,
      fecha_estreno: document.getElementById("pel-edit-estreno").value,
      precio_alquiler: Number(document.getElementById("pel-edit-precio").value),
    });
  },
  "Película actualizada correctamente."
);

// Socios
registrarFormulario(
  "form-socio",
  () =>
    enviarPeticion("/api/socios", "POST", {
      nombre: document.getElementById("soc-nombre").value,
      edad: Number(document.getElementById("soc-edad").value),
    }),
  "Socio registrado correctamente."
);

registrarFormulario(
  "form-editar-socio",
  () => {
    const codigo = document.getElementById("soc-edit-codigo").value;
    return enviarPeticion(`/api/socios/${codigo}`, "PUT", {
      nombre: document.getElementById("soc-edit-nombre").value,
      edad: Number(document.getElementById("soc-edit-edad").value),
    });
  },
  "Socio actualizado correctamente."
);

// Alquileres
registrarFormulario(
  "form-alquiler",
  () => {
    const codigosTexto = document.getElementById("alq-peliculas").value;
    const codigos = codigosTexto
      .split(",")
      .map((c) => Number(c.trim()))
      .filter((n) => !Number.isNaN(n) && n > 0);

    return enviarPeticion("/api/alquileres", "POST", {
      socio_codigo: Number(document.getElementById("alq-socio").value),
      peliculas_codigos: codigos,
      fecha_recogida: document.getElementById("alq-recogida").value,
      fecha_devolucion: document.getElementById("alq-devolucion").value,
    });
  },
  "Alquiler registrado correctamente."
);

registrarFormulario(
  "form-editar-devolucion",
  () => {
    const codigo = document.getElementById("alq-edit-codigo").value;
    return enviarPeticion(`/api/alquileres/${codigo}/devolucion`, "PUT", {
      fecha_actual: document.getElementById("alq-fecha-actual").value,
      nueva_fecha_devolucion: document.getElementById("alq-nueva-devolucion").value,
    });
  },
  "Fecha de devolución actualizada correctamente."
);

// Administradores
registrarFormulario(
  "form-admin",
  () =>
    enviarPeticion("/api/administradores", "POST", {
      nombre: document.getElementById("adm-nombre").value,
    }),
  "Administrador creado correctamente."
);

registrarFormulario(
  "form-editar-admin",
  () => {
    const codigo = document.getElementById("adm-edit-codigo").value;
    return enviarPeticion(`/api/administradores/${codigo}`, "PUT", {
      nombre: document.getElementById("adm-edit-nombre").value,
    });
  },
  "Administrador actualizado correctamente."
);

// Estadísticas
registrarFormulario(
  "form-estadistica",
  () =>
    enviarPeticion("/api/estadisticas", "POST", {
      administrador_codigo: Number(document.getElementById("est-admin").value),
      socio_codigo: Number(document.getElementById("est-socio").value),
      mes: Number(document.getElementById("est-mes").value),
      anio: Number(document.getElementById("est-anio").value),
      fecha_creacion: document.getElementById("est-creacion").value,
    }),
  "Estadística mensual generada correctamente."
);

cargarEstado().catch((err) => mostrarNotificacion(err.message, true));