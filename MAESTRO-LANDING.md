# 🏛️ MAESTRO — Landing manilahouse.co
> Documento maestro de conocimiento. Todo lo aprendido construyendo y operando la landing.
> Creado: 2026-07-29 · Mantener vivo: cada vez que se descubra algo nuevo, agregarlo acá.
> Autor operativo: agente PROPIEDADES-DEV (Manila House). Fuente de verdad técnica del sitio.

---

## 0. TL;DR (si solo lees una cosa)

- El sitio es **un solo `index.html`** (HTML+CSS+JS inline) en **Vercel**. El catálogo son **arrays JS**; las galerías salen de un **manifest JSON**.
- **Andrés pega un link de Airbnb → se ejecuta el workflow completo sin preguntar** (extraer → curar 10 → Higgsfield → publicar → ficha → brochure → verificar en producción).
- **Regla de imágenes de oro:** TODA imagen se sirve **local desde nuestro dominio**. Nunca hotlink a Airbnb (`muscache.com`) — Airbnb rota esas URLs y la imagen muere → huecos en el sitio.
- **Precio landing = tarifa Airbnb × 1.15** (regla fija de Andrés). Precios en USD (TRM ~4.000).
- **Nada se inventa.** Amenities/specs salen del listing real; lo que falta se marca pendiente, no se rellena.

---

## 1. QUÉ ES Y DÓNDE VIVE

| Cosa | Detalle |
|---|---|
| **URL** | https://www.manilahouse.co |
| **Repo** | `github.com/andresflpvasquez89/manila-house-propiedades` |
| **Código local** | `...\AF GROUP\Manila House\manila-house-propiedades landing\` |
| **Deploy** | Vercel (auto-deploy en cada push a `main`), dominio en Namecheap |
| **Archivo núcleo** | `index.html` — monolito HTML+CSS+JS (~3.2k líneas, ~400KB) |
| **Config deploy** | `vercel.json` (cleanUrls, CSP y cabeceras de seguridad) |

**Estructura de carpetas del repo:**
```
manila-house-propiedades landing/
├── index.html                      ← TODO el sitio (código + estilos + lógica)
├── vercel.json                     ← deploy + headers + CSP
├── images/
│   ├── properties/                 ← sN.jpg (hero) + sN_2..sN_10.jpg (galería)
│   └── gallery-manifest.json       ← { "sN": ["sN.jpg","sN_2.jpg", ...] }
├── brochures/                      ← {slug}.pdf (uno por propiedad)
└── index.html.pre-*.bak            ← backups antes de cambios grandes
```

---

## 2. ARQUITECTURA DE DATOS (cómo funciona por dentro)

### 2.1 El inventario = arrays JS en `index.html`
- `const shortStayProperties = [ ... ]` — las 21 propiedades short-stay (s1–s21).
- `const monthlyProperties = [ ... ]` — renta mensual (m1–m60), COP.

**Campos de una entrada short-stay (modelo real):**
```js
{ id:'s1', name:'Pink House', zone:'El Poblado', type:'house',
  guests:16, rooms:6, beds:10, bathrooms:7.5, price:1275, rating:'5.0',
  featured:true, pool:true, jacuzzi:true,
  img:'/images/properties/s1.jpg',
  airbnb:'https://es-l.airbnb.com/rooms/<roomId>',
  pdf:'/brochures/pink-house.pdf',
  desc_en:'...', desc_es:'...',
  amenities:['Piscina','Jacuzzi', ...] }
```
- `price` es **USD** (el modal renderiza `'$'+price+' USD'`).
- `beds` alimenta la fila "Camas" del modal (i18n `label_beds`).
- `pdf` hace aparecer la fila "Brochure → Descargar PDF ↓" en el modal (si el campo no está, no se muestra).
- `featured:true` → sale también en la sección Destacadas.

### 2.2 Galería = `gallery-manifest.json` (fetch en runtime)
- `index.html` hace `fetch('/images/gallery-manifest.json')` y arma el carrusel de cada propiedad desde `{ "sN": [archivos] }`.
- **Naming obligatorio:** `sN.jpg` = hero, `sN_2.jpg … sN_10.jpg` = resto. El manifest ordena hero primero.
- El regex del manifest agrupa por `^s\d+`; monthly (`m`) NO lleva galería.

### 2.3 Funciones JS clave del modal
`openModal(id)`, `closeModal()`, `setGalleryImg/prev/next`, `openWhatsApp*`, `setAboutImage()`.
La sección "Sobre Nosotros" carga su foto de fondo vía `const aboutImage = '/images/properties/s1.jpg'` (Pink House, insignia).

---

## 3. WORKFLOW ESTÁNDAR — Propiedad desde link (el corazón)

> Andrés pega link(s) de Airbnb (con fechas) → esto corre **sin pedir permiso**.
> Doc operativo detallado: `CENTRO DE OPERACIONES\AGENTES\05-PROPIEDADES-DEV-WORKFLOW-fotos-desde-link.md`.

**1. EXTRAER** (navegador real sobre la página de Airbnb)
**2. CURAR** las 10 que más venden (lo hace el agente)
**3. HIGGSFIELD** — mejorar 4 fotos clave
**4. PROCESAR** a 2560px + regenerar manifest
**5. PUBLICAR** — array + ficha + brochure, sincronizados
**6. VERIFICAR** en producción

Los detalles finos de cada paso están en las secciones 4–9.

---

## 4. EXTRACCIÓN DE AIRBNB — todas las trampas (¡lo más frágil!)

**Fotos — el regex DEBE cubrir estas 4 variantes o se pierden fotos:**
1. **Dos patrones de ID:** `Hosting-{roomId numérico}` **Y** `Hosting-{base64 de "StaySupplyListing:roomId"}` (empieza `U3RheVN1…`, a veces URL-encoded `%3D%3D`). Muchos listings mezclan ambos; el interior suele estar en el base64.
2. **Dos rutas de CDN:** `im/pictures/hosting/` **Y** `im/pictures/miso/` (listings viejos).
3. **Dos extensiones:** `.jpeg` **Y** `.png` (listings viejos usan png).
4. **Lazy-load:** abrir `?modal=PHOTO_TOUR_SCROLLABLE` y **scrollear** el diálogo para hidratar todas las fotos.

**Amenities REALES:** abrir "Mostrar los N servicios" y leer el modal completo, **incluida la sección "No incluidos"** — ahí es donde Airbnb confirma qué NO tiene (A/C, calefacción, agua caliente…). ⚠️ **NUNCA heredar amenities del array viejo de la landing** (así se propagó el bug del "A/C fantasma").

**Precio:** mandar los links **con fechas** (`check_in`/`check_out`) para que Airbnb muestre la tarifa. Leerla del bloque `"$X COP por 1 noche"`. Sin fechas, el precio no aparece.

**Specs COMPLETAS:** verificar **los 4 números** (huéspedes / camas / hab / baños) del summary — la capacidad del listing puede diferir de lo que dice la landing (nos pasó: s9 eran 14 huéspedes/19 camas, no 19 huéspedes; s10 eran 5 no 6).

**Estorbos del navegador:**
- Aparece un modal de **traducción** de Airbnb que tapa todo (`body.innerText` da 18 chars) → cerrarlo antes de leer.
- Los **screenshots del navegador interno se cuelgan** en páginas pesadas → **verificar por DOM/JS** (`read_page`, `javascript_tool`), no por captura.
- Si el tab no hidrata, hacer `fetch()` server-side del HTML también trae specs, precio y fotos (el summary viene en el HTML inicial).

---

## 5. CURADURÍA — la hace el agente (instrucción fija de Andrés)

- El agente **elige las 10 que más venden**, sin esperar selección manual. Mostrar lo elegido pero ejecutar de una.
- **Criterio:** 1 hero potente (piscina/fachada/amenity estrella) → sala → cocina/comedor → 2-3 habitaciones DISTINTAS → baño solo si es de diseño → amenities diferenciadores.
- **Cero duplicados:** los hosts suben ráfagas de la misma toma; elegir UNA por espacio (este fue un reclamo real).
- **Descartar SIEMPRE:** fotos turísticas de la ciudad, marcas de agua/copyright de terceros (ej. ©Wandersmiles), parqueaderos, borrosas.
- Herramienta interna: hoja de contacto 4-col con miniaturas numeradas (`sheet_maker.py`) para decidir rápido.

---

## 6. HIGGSFIELD (mejora IA) — config fija

- **4 fotos por propiedad:** hero + sala + amenity estrella + habitación principal. (+ rescates si el original viene <1000px.)
- Flujo: `media_import_url` → `upscale_image` **4K**.
- ⚠️ **El backend 4K se cae a ratos.** Si un job falla 2 veces → **fallback a 2K** (2160px+; sirve igual porque servimos a 2560). Lanzar de a 1-2 con pausa, **no 10 en ráfaga** (rate limit).
- Costo ~2 créditos/foto. Con el encargo del link se entiende aprobado el gasto estándar; cualquier extra se consulta (regla `aprobar-antes-de-generar`).
- **`reveal-not-invent`:** mejorar lo que hay, nunca inventar espacios que la propiedad no tiene.
- Los originales de Airbnb suelen venir a **1200×800** → el upscale a 4K/2K sí aporta de verdad (no es redundante).

---

## 7. PROCESAMIENTO DE IMÁGENES

- Todas las fotos publicadas → **fit a 2560×1707 (3:2), JPEG q85 progresivo** (Pillow `ImageOps.fit`).
- Nombrar por orden de galería: `sN.jpg`, `sN_2.jpg` … `sN_10.jpg` en `images/properties/`.
- Borrar galerías viejas completas antes de re-curar (incluye `_11`, `_12` legacy del pipeline viejo).
- Regenerar `gallery-manifest.json` tras cualquier cambio de fotos (agrupa por `^s\d+`, hero primero).
- Peso típico: ~4–8 MB por galería de 10. El hero 4K→2560 queda ~500–750 KB (aceptable mobile).

---

## 8. BROCHURES PDF — vectoriales

- **Texto SIEMPRE vectorial con `reportlab`** — NUNCA rasterizar texto con Pillow (se pixela; fue un reclamo real). Fotos sí van como imagen (crops con Pillow).
- **Trampa crítica `setCharSpace`:** el "character spacing" (Tc) **persiste** en el content stream de reportlab entre bloques de texto. Si no se resetea explícitamente en CADA bloque, el texto sale desparramado. → llamar `t.setCharSpace(tr)` SIEMPRE (con 0 cuando no se quiere tracking).
- **Fuentes** (de `C:\Windows\Fonts`): Palatino (`palab`/`pala`) como display serif + Segoe UI (`segoeui`/`seguisb`/`segoeuil`/`segoeuisl`) para texto. Sustitutos de Cormorant/Outfit que no están instaladas.
- **Estructura 3 páginas:** portada full-bleed (foto + degradados raster + texto vectorial encima, chips de specs huéspedes·hab·**camas**·baños) → experiencia (feature + 2-up + lead + amenities chips) → espacios (banner + grid 2×2 + tarjeta CTA oscura con pill dorado de WhatsApp).
- **NO llevan precio** — dicen "consultar por WhatsApp". Por eso un cambio de precio NO obliga a regenerarlos, y los descuentos tácticos no amarran.
- **Doble destino:** `brochures/{slug}.pdf` en el repo (para el botón del modal, campo `pdf:`) **y** `CATALOGOS\{Nombre}-sN.pdf` (archivo comercial de Andrés).
- **QC:** rasterizar con `pypdfium2` y revisar las páginas antes de dar por bueno.
- Motor reutilizable: `build_brochures_*.py` (config por propiedad + motor común). Se parametriza con `repr(P)` para evitar heredocs gigantes que rompen el shell.

---

## 9. PRECIOS

- **Regla fija de Andrés:** precio landing = **tarifa Airbnb × 1.15**, convertir a USD (TRM ~4.000) y redondear. Anotar el cálculo en la ficha.
- Ajustes globales se piden en pesos pero el array está en USD → convertir (ej. "+300.000 pesos" = **+$75 USD** a TRM 4.000). **Confirmar la conversión antes de tocar precios en vivo** (el impacto % es muy disparejo entre una villa de $1.300 y un glamping de $140).
- **Precio público ≠ precio de cierre.** Descuentos tácticos no tocan el array ni las fichas.
- **Precios faltantes se marcan pendientes, nunca se inventan.**

---

## 10. 🔴 BUG CLASE #1 — Hotlinks de Airbnb muertos

**Síntoma:** un espacio del sitio (hero de una propiedad, o el recuadro "Sobre Nosotros") aparece vacío/crema.
**Causa raíz:** el código apuntaba a una URL de imagen de `a0.muscache.com` (CDN de Airbnb). **Airbnb rota esas URLs** cada cierto tiempo; cuando la foto muere, no carga, el `onload` nunca dispara y el placeholder se queda pegado.
**Ocurrió en:** el hero del Manila Dúplex (s3) y en la foto de la sección "Sobre Nosotros" (apuntaba a una foto de Manila 5).
**REGLA PERMANENTE:** **ninguna imagen del sitio puede depender de `muscache.com`.** Todo se descarga y se sirve local desde `/images/`. Barrido de control: `curl manilahouse.co | grep muscache` debe dar **0**.

---

## 11. DEPLOY & VERIFICACIÓN (no negociable)

1. **Backup** `index.html` antes de cambios grandes (`cp index.html index.html.pre-<algo>.bak`).
2. **Verificar en local** antes de push: `python -m http.server` + validar por JS (array parsea, galería 10/10, links del modal, HEAD 200 del PDF y del hero). Validar el array con `node -e "eval(...)"` para cazar errores de sintaxis antes de romper producción.
3. **Mobile-first 375px** — >80% del tráfico es móvil (WhatsApp/Instagram).
4. `git add` + `commit` + `push origin main` → Vercel auto-deploya.
5. **Verificar en producción SIEMPRE:** esperar el deploy (`until curl … grep <señal>; do sleep 5; done`) y confirmar contenido en vivo + HTTP 200 de assets nuevos. Push = deploy: nunca dar por hecho sin comprobar.

---

## 12. REGLAS DE INTEGRIDAD (transversales)

1. **Nada se inventa.** Amenities/specs del listing real; lo que falta se pregunta o se marca pendiente.
2. **La palabra de Andrés gana** sobre el listing y la ficha — y la discrepancia se **anota** (ej. Manila 1: Andrés dice A/C sí, listing no lo lista → acción NEXUS de agregarlo en Airbnb).
3. **Sincronizar 3 niveles** en cada cambio: landing (array) + ficha (`PROPIEDADES\`) + brochure. Que no queden desalineados.
4. **Verificar los 4 números** de specs en cada ingesta (huéspedes/camas/hab/baños).
5. **Screenshots del navegador interno fallan** → verificar por DOM.

---

## 13. ESTADO ACTUAL DEL CATÁLOGO (2026-07-29)

**21 propiedades short-stay** (s1–s21). Precios ya con el +$75 global aplicado:

| ID | Propiedad | Zona | Precio USD |
|---|---|---|---|
| s1 | Pink House (insignia, 5.0 ★) | El Poblado | 1.275 |
| s2 | Villa Envigado | Envigado | 575 |
| s3 | Manila Dúplex | El Poblado | 425 |
| s4 | Manila 5 (Basketball) | El Poblado | 425 |
| s5 | Manila 1 (Galería) | El Poblado | 305 |
| s6 | Manila 3 (Tropical) | El Poblado | 305 |
| s7 | Manila 2 (Nómadas) | El Poblado | 235 |
| s8 | Casa Rionegro | Rionegro | 325 |
| s9 | Granja Santa Fe | Santa Fe | 525 |
| s10 | Loft Bogotá | Bogotá | 275 |
| s11 | Volcana | El Poblado | 1.375 |
| s12 | Villa Épica 11 Hab | El Poblado | 1.375 |
| s13 | Casa Provenza | El Poblado | 1.075 |
| s14 | Luxury Flat frente al mar | Cartagena | 325 |
| s15 | Glamping Bosque & Malla | Sopetrán/Santa Fe | 215 |
| s16 | Finca Villa Cavil | Sopetrán/Santa Fe | 335 |
| s17 | Glamping Cascada | Sopetrán/Santa Fe | 235 |
| s18 | Finca Villa Cerat | Sopetrán/Santa Fe | 305 |
| s19 | Glamping El Bosque | Sopetrán/Santa Fe | 215 |
| s20 | Glamping A-Frame | Sopetrán/Santa Fe | 215 |
| s21 | Villa los Pinos | Sopetrán/Santa Fe | 315 |

Cada una: galería de 10 (2560px, hero mejorado con IA), ficha en `CENTRO DE OPERACIONES\PROPIEDADES\`, y brochure PDF vectorial en repo + CATALOGOS.

---

## 14. PENDIENTES CONOCIDOS (deuda abierta)

- ⚠️ **Sin analytics.** La CSP habilita GA4 y Meta Pixel pero **no hay ningún script instalado** → no se mide ni una conversión ni se puede pautar rentable. Es lo más caro de no tener. (Prerrequisito de toda pauta de MIDAS.)
- **Precios de s12 y s14** entraron provisionales; confirmar tarifa real con Andrés.
- **Manila 1 (s5):** agregar A/C al listing de Airbnb (Andrés confirma que sí tiene; el listing no lo lista → se está regalando el filtro de búsqueda).
- **Lote Santa Fe (s15–s21):** son del corredor de terceros → confirmar comisión/acuerdo antes de vender en directo. Técnicamente están en **Sopetrán** (se agruparon bajo "Santa Fe"). s20 solo tenía 12 fotos.
- **Idea de cross-sell:** módulo a Manila Transportes en landing + brochures (ingreso propio con el tráfico que ya llega). Recomendado sobre AdSense.
- `README.md` del repo está desactualizado (describe un hub viejo de GitHub Pages).
- Los scripts `process-photos-v3.py` / `update-manifest.py` del repo tienen rutas viejas (de antes de mover el repo a `AF GROUP\`).

---

## 15. ÍNDICE RÁPIDO DE GOTCHAS (para cazar en 5 segundos)

| Problema | Causa / Fix |
|---|---|
| Faltan fotos de un listing | Regex no cubre las 4 variantes (base64 id, `miso/`, `.png`, lazy-load) |
| A/C u otro amenity mal | Se heredó del array viejo → leer del modal "Mostrar servicios" + "No incluidos" |
| Precio no aparece | Falta `check_in`/`check_out` en el link |
| `body.innerText` = 18 chars | Modal de traducción de Airbnb tapando la página → cerrarlo |
| Screenshot se cuelga | Navegador interno + página pesada → verificar por DOM |
| Texto del PDF pixelado | Se rasterizó con Pillow → usar reportlab (vectorial) |
| Texto del PDF desparramado | `setCharSpace` no reseteado por bloque en reportlab |
| Recuadro/hero vacío en el sitio | Hotlink muerto de muscache → servir local |
| Fotos duplicadas en galería | Se usó orden crudo del listing → curar 1 por espacio |
| Specs mal (huésp/camas) | No se verificaron los 4 números contra el listing |

---
*Fin del maestro. Cualquier aprendizaje nuevo va acá, con fecha.*

## HERO EN VIDEO (desde 2026-08-28)
- La portada es `images/hero/manila-house-hero.mp4` (1920×1080, 24.6 s, 12 propiedades × 2 s, Ken Burns alternado + xfade 0.6 s, sin audio) (1600×900, 3.4 MB) y `manila-house-hero-mobile.mp4` (960×540, 1.5 MB) para ≤720 px; `poster.jpg` es el respaldo (no-JS, reduced-motion, primer paint).
- **Sin IA, sin créditos**: se arma con ffmpeg desde los heroes reales. Script: `CENTRO DE OPERACIONES\AGENTES-PROPIEDADES-DEV-hero-video-build.py` (lista `SEQ` = orden y menciones). Para cambiar propiedades: editar `SEQ`, correr, y actualizar el mismo `SEQ` en el `<script>` del final de `index.html` (menciones sincronizadas cada 2 s, tope derecho).
- El `<video>` no lleva `<source>`: un inline script elige 1080/720 por `innerWidth` antes de cargar (evita doble descarga; Chrome ignora `media` en `<source>` de video).
- Se eliminó el webp base64 de 250 KB que vivía en el CSS del hero → HTML 422 KB → 173 KB.
- Lote Alta Gama s29–s36 (2026-08-28): cotizaciones de 3 noches ÷ 3 × 1.15; proveedor en `ALIADOS\PROVEEDORES.xlsx`. Truco para el pase IA de heroes sin transcribir URLs presignadas: publicar primero y usar `media_import_url` desde el sitio en vivo.
- Gotcha de verificación: Chrome **difiere la carga y el autoplay de `<video>` en pestañas ocultas** (`document.visibilityState === 'hidden'`) → readyState 0 y buffer vacío no significan bug; probar en una pestaña visible (el panel del navegador de Claude sirve).
