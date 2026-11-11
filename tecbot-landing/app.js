// TecBot Académico · formulario de consulta
// Si la página se abre con doble clic (file://) usa el servidor local; si la sirve FastAPI, usa la misma dirección.
const API_BASE = location.protocol === "file:" ? "http://localhost:8000" : "";
const LIMITE = 1000;

const form = document.getElementById("consulta-form");
const campo = document.getElementById("pregunta");
const contador = document.getElementById("contador");
const boton = document.getElementById("boton-enviar");
const resultado = document.getElementById("resultado");

function mostrar(html, estado) {
  resultado.hidden = false;
  resultado.className = `resultado resultado-${estado}`;
  resultado.innerHTML = html;
}

function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto;
  return div.innerHTML;
}

function pintarRespuesta(data) {
  const fuentes = data.fuentes.length
    ? `<h3>Fuentes</h3><ul class="fuentes">${data.fuentes
        .map(
          (f) => `<li><span class="fuente-doc">${escapar(f.documento)}</span>
                  <span class="fuente-seccion">${escapar(f.seccion)}</span>
                  <blockquote>${escapar(f.fragmento)}</blockquote></li>`
        )
        .join("")}</ul>`
    : "";
  const advertencia = data.advertencia
    ? `<p class="advertencia">⚠️ ${escapar(data.advertencia)}</p>`
    : "";
  mostrar(
    `<p class="respuesta-texto">${escapar(data.respuesta)}</p>${advertencia}${fuentes}`,
    data.fuentes.length ? "exito" : "vacio"
  );
}

async function consultar(pregunta) {
  boton.disabled = true;
  boton.textContent = "Buscando…";
  mostrar('<p class="cargando"><span class="spinner" aria-hidden="true"></span> Buscando en los documentos…</p>', "carga");

  try {
    const respuesta = await fetch(`${API_BASE}/api/consulta`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pregunta }),
    });
    if (respuesta.status === 422) {
      mostrar("<p>Revisa tu pregunta: no puede estar vacía ni pasar de 1,000 caracteres.</p>", "error");
      return;
    }
    if (!respuesta.ok) throw new Error(`HTTP ${respuesta.status}`);
    pintarRespuesta(await respuesta.json());
  } catch (error) {
    mostrar(
      `<p><strong>No pude conectar con TecBot.</strong> Verifica que el servidor esté encendido
       (<code>uvicorn app.main:app --reload</code>) e inténtalo de nuevo.</p>
       <button type="button" class="btn btn-secundario" id="reintentar">Reintentar</button>`,
      "error"
    );
    document.getElementById("reintentar").addEventListener("click", () => consultar(pregunta));
  } finally {
    boton.disabled = false;
    boton.textContent = "Preguntar";
  }
}

campo.addEventListener("input", () => {
  contador.textContent = `${campo.value.length} / ${LIMITE}`;
});

form.addEventListener("submit", (evento) => {
  evento.preventDefault();
  const pregunta = campo.value.trim();
  if (!pregunta) {
    mostrar("<p>Escribe una pregunta antes de enviar.</p>", "error");
    campo.focus();
    return;
  }
  consultar(pregunta);
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    campo.value = chip.textContent;
    campo.dispatchEvent(new Event("input"));
    consultar(chip.textContent);
  });
});
