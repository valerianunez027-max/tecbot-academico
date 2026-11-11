# Sistema de diseño — TecBot Académico

Fuente de verdad visual para `@disenador-web`. Las variables viven en `tecbot-landing/styles.css` (`:root`).

## Paleta (modo oscuro)

| Variable | Valor | Uso |
|---|---|---|
| `--color-fondo` | `#0B1120` | Fondo de página |
| `--color-superficie` | `#111827` | Tarjetas, formulario, resultado |
| `--color-acento` | `#22D3EE` | Enlaces, foco, iconos |
| `--color-acento-2` | `#10B981` | Final del degradado |
| `--color-texto` | `#E5E7EB` | Texto principal |
| `--color-texto-suave` | `#94A3B8` | Texto secundario |
| `--color-borde` | `rgba(148,163,184,.15)` | Bordes sutiles |
| Aviso | `#FDE68A` sobre ámbar translúcido | Aviso didáctico y advertencias |
| Error | borde `rgba(248,113,113,.5)` | Estado de error |

Degradado de marca: `linear-gradient(135deg, #22D3EE, #10B981)`.

## Tipografía

- Plus Jakarta Sans (Google Fonts), pesos 400–800.
- Títulos `h1` con `clamp(2.4rem, 6vw, 4.2rem)`, peso 800.

## Formas y espaciado

- Radio general `--radio: 16px`; botones y chips en píldora (`999px`).
- Ancho máximo `1120px`; formulario de consulta `760px`.
- Secciones con `5rem` de padding vertical.

## Componentes

| Componente | Estados |
|---|---|
| Navbar (glassmorphism, menú hamburguesa ≤768 px solo con CSS) | normal, menú abierto |
| Hero (badge, título con degradado, 2 botones) | — |
| Formulario de consulta (textarea, contador, botón) | vacío, enfocado, enviando (botón deshabilitado) |
| Chips de ejemplo | normal, hover |
| Resultado | carga (spinner), éxito (borde verde + fuentes), sin evidencia (borde ámbar + advertencia), error (borde rojo + reintentar) |
| Tarjetas de características | normal, hover (elevación + brillo cian) |

## Accesibilidad y responsive

- Foco visible: contorno cian de 2 px en `:focus-visible`.
- Resultado con `aria-live="polite"`; etiqueta oculta (`.sr-only`) para el textarea.
- Aviso de material didáctico siempre visible arriba del formulario (RF-09).
- Funciona a 360 px sin scroll horizontal (RNF-04).
