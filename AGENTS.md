# AGENTS.md — Landing manilahouse.co

> Protocolo de dos cerebros: **Claude construye · Codex audita.** Coordinación por este archivo.
> Creado 2026-09-29. Documento INTERNO: está en `.vercelignore` y no se publica.

---

## 1. QUÉ ES ESTE PROYECTO

Landing de **Manila House** (hospitalidad e inmuebles de Andrés Vásquez): renta corta, renta mensual amoblada y venta, en Medellín, Envigado, Oriente antioqueño, Santa Fe/Sopetrán, Bogotá y Cartagena. Convierte a WhatsApp (+57 300 713 9578).

**Modelo de negocio (importante para auditar precios):** mezcla de propiedades propias (s1–s11) y **reventa de inventario de terceros** (s12 en adelante: Alta Gama, VIT Luxury, otros hosts de Airbnb). En reventa, el precio publicado lleva margen sobre la tarifa del tercero. **La regla de margen, los proveedores y sus contactos son INTERNOS**: viven en `..\CENTRO DE OPERACIONES\` y nunca en archivos servidos.

## 2. STACK Y CÓMO CORRER

- **Un solo `index.html`** (HTML + CSS + JS vanilla, sin build). Inventario en los arrays JS `shortStayProperties` (s1…) y `monthlyProperties`.
- Galerías: `images/properties/sN.jpg` (hero) + `sN_2..sN_10.jpg`, listadas en `images/gallery-manifest.json` (regenerar tras cambiar fotos).
- Brochures PDF vectoriales (reportlab): `brochures/<slug>.pdf` + copia en `..\CATALOGOS\`.
- Portada: `images/hero/manila-house-hero.mp4` (+ `-mobile.mp4`, `poster.jpg`), montaje ffmpeg sin IA. Script: `..\CENTRO DE OPERACIONES\AGENTES\05-PROPIEDADES-DEV-hero-video-build.py`.
- Deploy: **Vercel, auto-deploy en cada push a `main`** (`andresflpvasquez89/manila-house-propiedades`). `vercel.json` publica la raíz (`outputDirectory: "."`) → **todo archivo nuevo en la raíz es público salvo que esté en `.vercelignore`.**

```bash
# validar que el array de propiedades parsea (obligatorio antes de push)
node -e "let s=require('fs').readFileSync('index.html','utf8'); let m=s.match(/const shortStayProperties = (\[[\s\S]*?\n\]);/); console.log(eval(m[1]).length)"
```

Referencia de conocimiento completa: `MAESTRO-LANDING.md` (interno). Workflow de alta de propiedades: `..\CENTRO DE OPERACIONES\AGENTES\05-PROPIEDADES-DEV-WORKFLOW-fotos-desde-link.md`.

## 3. REGLAS DURAS

1. **Nada se inventa.** Specs, amenities y reglas salen del listing (evidencia cruda guardada); si falta, `PENDIENTE`. La palabra de Andrés gana sobre el listing (se anota la discrepancia).
2. **Precio de reventa** = total de la cotización de Airbnb que manda Andrés ÷ noches × 1.15, redondeado a múltiplo de 5. El cálculo queda en la ficha de la propiedad. Los precios son decisión de Andrés: si uno parece mal, se reporta, no se cambia.
3. **Dirección exacta nunca** en landing ni brochure (solo en visita agendada).
4. **Un solo deploy por tanda** (cada push a `main` es producción). Verificar todo antes, verificar producción después.
5. **Nada interno en archivos servidos.** Todo documento nuevo en la raíz va a `.vercelignore` en el mismo commit; comprobar con `curl` que responde 404 en producción.
6. **IA paga (Higgsfield)** solo dentro del workflow validado (upscale de heroes) o con orden explícita de Andrés.

## 4. 🔴 DEUDA CONOCIDA

- **Enlace a Airbnb — decisión FINAL de Andrés (2026-09-29):** se eliminó la fila visible "Airbnb — Ver →" del modal; en su lugar hay un **"ver" discreto** (`a.amenity-ref`, gris, 11px, sin la palabra "Airbnb") al final de las características, en todas las propiedades con `airbnb`. Motivo: Andrés revisa calendarios desde el celular. **Riesgo aceptado por Andrés:** la URL sigue en el código fuente. No cambiar a botón visible ni eliminar sin su orden. Respaldo de links: `..\CENTRO DE OPERACIONES\PROPIEDADES\_airbnb-links-landing-2026-09-29.json` y columna en `ALIADOS\PROVEEDORES.xlsx`.
- **Contadores del hero** (`data-counter` 70 propiedades · 14 zonas · 48 → "4.8★ Top Rated"): `NO VERIFICADO` contra fuente. No cambiar sin dato de Andrés.
- Precios provisionales heredados: s12, s14 (ver fichas).

## 5. LOG

### 2026-09-29 · Claude · Lote s37–s47 (11 villas de reventa) + cierre de fuga del MAESTRO · `auditar: sí`

- Fuga cerrada: `MAESTRO-LANDING.md`, `about.txt`, `hero-block.txt`, `hero-css.txt` y `*.py` eran públicos en manilahouse.co (el MAESTRO exponía la regla de margen). Se agregó `.vercelignore`.
- Alta de s37–s47 desde links de Andrés con fechas 6–8 oct 2026 (2 noches). Evidencia de precios: scratchpad `precios-s37-s47/prices_raw.json` + `calc_prices.py`; evidencia de listings: `ingesta-sNN/evidence.json` + `listing.html`.
- Para auditar: (a) cada entrada del array contra su `evidence.json`; (b) aritmética de precios; (c) que ningún archivo interno responda 200 en producción.

### 2026-09-29 · Claude · Fallback de fotos rotas (modal + `prop-card`) · `auditar: sí`

- Bug: los `onerror` inline metían el HTML de `generatePlaceholder()` dentro de un string JS dentro de un atributo HTML. **Modal** (`openModal`): solo escapaba `'`, el `"` de `class="..."` cerraba el atributo → nodo de texto `'">` visible en `.modal-img` (reproducido en s36 y s37) y placeholder que nunca aparecía. **`prop-card`** (`renderCollection`): comillas escapadas, pero el placeholder trae saltos de línea → `SyntaxError: Invalid or unexpected token @1:30` al fallar una foto, sin placeholder.
- Arreglo: se eliminaron los `onerror` inline; tras renderizar se engancha `addEventListener('error', …, { once: true })`. Modal: reemplaza `#modalImg` por el placeholder (igual que la rama sin galería). Tarjeta: `img.outerHTML = placeholder` (conserva badges y ♡, igual que la rama sin `p.img`). Se quitó la variable `placeholderHTML` (sin uso). `bento-card` no tiene este patrón (usa `background-image`, sin `onerror`); no se tocó.
- Verificación local (localhost:8765, antes → después): T1 nodos `'">` en `.modal` para s36/s37: 1/1 → 0/0 · T2 modal con foto inexistente: sin placeholder → placeholder "V / Envigado" · T3 tarjeta s32 con foto inexistente: SyntaxError → placeholder con badges y ♡ · errores JS: 1 → 0 (solo quedan los 2 × 404 de las fotos falsas a propósito) · regresión: galería s37 navega 1→2 y da la vuelta a 10/10, 12/12 fotos reales del grid cargan, 0 placeholders espurios · `node -e` del array: 47 · los 3 `<script>` inline compilan.
- Sin commit ni push: va en la misma tanda que s37–s47 (un solo deploy). Para auditar: que no quede ningún `onerror="` en `index.html` y el orden `visible[i]` ↔ `.prop-card` en `renderCollection`.
- Tras la auditoría de Codex (§6): guard `if (galleryImg.isConnected)` en el listener del modal. Batería final T1–T5 + T4b + regresión de galería: `ALL_PASS=true`, 0 errores JS; 0 `onerror="` en `index.html`; array 47; 3/3 scripts compilan. Script y resultados: `..\CENTRO DE OPERACIONES\AUDITORIAS\resultados\2026-09-29-fallback-fotos-rotas_pruebas.js`.

### 2026-09-29 · Claude · Decisiones de Andrés aplicadas tras la auditoría · `auditar: sí`
- Botón/URL de Airbnb retirados de reventa (s12–s47) → **luego revertido por decisión final de Andrés**: los 36 `airbnb` se restauraron desde el respaldo y el acceso quedó como "ver" discreto (ver §4).
- s40/s41/s46 recalculados sobre el **precio original** (sin descuento): 1375 / 1225 / 1190 (ANULADOS: 710 / 955 / 690).
- s39 se publica a 605 con fechas 6–8 oct (aprobado por Andrés).

### 2026-10-06 · Claude · Alta de s48 (Nomad Studio — Laureles) · `auditar: sí`
- Link de Andrés con fechas 2–4 nov: USD 241 / 2 × 1.15 → 140. Apartaestudio 2 huéspedes, anfitrión Tree House (proveedor nuevo).
- Jacuzzi y estacionamiento NO publicados: están en la lista de Airbnb pero no en fotos ni descripción (piso 4 sin ascensor). Confirmar con el anfitrión.
- Zona "Laureles" (ya existía en renta mensual). Hero con upscale Higgsfield 4K desde el original de 1200×1581.
- Motor de brochures: temporales y QC ahora en la carpeta de trabajo (`Path.cwd()`), ya no en `AGENTES\`.

### 2026-10-12 · Claude · Lote s49–s53 (5 apartamentos de un mismo anfitrión, sector Provenza) · `auditar: sí`
- Links de Andrés SIN fechas → precio de referencia leído por Claude en el panel de Airbnb (2–4 y 2–5 nov 2026), marcado "fechas elegidas por Claude". No se publica hasta que Andrés confirme.
- Base de cotización: estadía mínima de cada listing (2 noches; 3 en s49 y s53, donde Airbnb respondió "La estadía mínima es de 3 noches"). En estos listings el total trae un cargo fijo: el precio por noche baja ~11% al cotizar 3 noches en vez de 2 (evidencia en `precios-s49-s53/otras_lecturas.json`).
- Ingesta con verificador independiente por listing (workflow de 10 agentes): specs re-derivados, cada chip y frase contra el HTML, hero contra `photos.json`. 2 correcciones medias aplicadas (s50 BBQ/reglas, s51 "jacuzzi en el balcón").
- Nombres públicos sin la marca del proveedor; el alias interno ("Casa Oded #N") vive en fichas y en `PROVEEDORES.xlsx`. Regla nueva: el nombre del proveedor no aparece en ningún archivo servido.
- Heroes: Higgsfield 4K desde el original de 2560 px (10 créditos), cada uno comparado con la foto real antes de reemplazar.
- Herramienta nueva: `..\CENTRO DE OPERACIONES\AGENTES-PROPIEDADES-DEV-alta-lote.py` (valida y aplica el alta: index, fichas, Excel, config de brochures).

## 6. AUDITORÍAS DE CODEX

*(Codex escribe aquí sus hallazgos; Claude responde debajo de cada uno.)*

### 2026-09-29 · Codex (CLI `codex exec -m gpt-5.6-sol -s read-only`) · Lote s37–s47 · VEREDICTO: BLOQUEADO
Solicitud y fuentes crudas: `..\CENTRO DE OPERACIONES\AUDITORIAS\solicitudes6-09-29-lote-s37-s47\` · salida completa: `..\AUDITORIAS
esultados6-09-29-lote-s37-s47_codex.txt`.

1. **s41** "12 min de Provenza" contradicho por la descripción (15 min). → **Claude: ACEPTADO.** Ahora "cerca de Provenza" (array + brochure).
2. **s43** `pool:false` con piscina compartida del edificio. → **Claude: ACEPTADO** por precedente (s14, piscina de edificio, está `pool:true`); la bandera no se renderiza, el chip y la descripción ya dicen "del edificio".
3. **s45** "Sala de Fiestas" no sustentado como tal; la fuente dice "área de discoteca". → **Claude: ACEPTADO.** Chip, descripción y brochure dicen "área de discoteca".
4. **s47** "Solo adultos" más fuerte que la fuente ("No apto para niños ni bebés"). → **Claude: ACEPTADO.** Ahora "No apto para niños" / "Not suitable for children".
5. **Precios:** aritmética OK en los 11; el `raw` es copia de Claude desde el navegador (no reconsultable) y s39 usa fechas elegidas por Claude. → **Claude:** de acuerdo; queda declarado en fichas y se le pregunta a Andrés.
6. **Botón "Airbnb — Ver"** en reventa (s12–s47) expone el listing original y su precio. → **Claude:** es decisión de negocio de Andrés (existe desde s12); se le presenta antes del deploy. No se publica hasta su respuesta.
7. Brochures: OK (19 PDFs, huéspedes/hab/camas y "mínimo 3 noches" solo en s29–s36).

### 2026-09-29 · Codex (CLI `codex exec -m gpt-5.6-sol -s read-only`) · Fallback de fotos rotas · VEREDICTO: CONDICIONADO
Solicitud: `..\CENTRO DE OPERACIONES\AUDITORIAS\solicitudes\2026-09-29-fallback-fotos-rotas\SOLICITUD.md` · salida completa: `..\CENTRO DE OPERACIONES\AUDITORIAS\resultados\2026-09-29-fallback-fotos-rotas_codex.txt`.
Sin hallazgos críticos ni medios. Sin hallazgo: 0 `onerror` inline; sin carrera al enganchar el listener; `visible[i]` ↔ `.prop-card` alineado; `setGalleryImg` y `renderFeatured` sin regresión.

1. **Menor — listener obsoleto en el modal:** si falla tarde la foto de una propiedad ya cerrada, el callback (que captura `imgEl`, vivo) reemplaza la galería de la propiedad abierta. → **Claude: ACEPTADO, reproducido antes de arreglar** (T4: con s36 abierta, el error tardío de s37 dejó el placeholder "V" de s37). Guard `if (galleryImg.isConnected)`; T4 pasa y T4b confirma que la foto rota de la propiedad abierta sigue cayendo al placeholder. En `prop-card` no aplica: la `<img>` vieja conserva su padre dentro del subárbol separado (T5: sin excepción, 0 placeholders en el grid). El `onerror` viejo no tenía este efecto (`closest()` en un nodo separado da `null`); lo introdujo el arreglo.
2. **Menor — el LOG cita resultados de ejecución no verificables desde el código.** → **Claude: ACEPTADO.** El script de pruebas y sus resultados antes/después quedan en `..\CENTRO DE OPERACIONES\AUDITORIAS\resultados\2026-09-29-fallback-fotos-rotas_pruebas.js` para correrlo de nuevo.

### 2026-09-29 · Codex (CLI) · Ronda 3 — enlace discreto "ver" · VEREDICTO: APROBADO
36 links restaurados = respaldo JSON; sin texto "Airbnb" visible; `amenity-ref` condicionado a `p.airbnb` con `rel="noopener noreferrer nofollow"`; cero cambios en precios/specs/amenities; array 47/47. Salida: `..\CENTRO DE OPERACIONES\AUDITORIASesultados6-09-29-lote-s37-s47_codex_R3.txt`.

### 2026-09-29 · Claude · DEPLOY `aedf4f2` (orden de Andrés) · verificado en producción
11/11 propiedades nuevas en vivo; precios s39=605 · s40=1375 · s41=1225 · s46=1190 · s47=1605; 19/19 brochures 200 (el primer 404 de villa-club-envigado.pdf fue propagación del CDN); MAESTRO-LANDING.md, AGENTS.md, about.txt, hero-*.txt, *.py → 404; robots/sitemap/video 200; modal s45 sin "Airbnb", con "ver" y PDF; 0 errores de consola. Nota: `googledf73c3ac78ab4eeb.html` responde 308 → versión sin extensión (200) por `cleanUrls`, preexistente.

### 2026-10-06 · Codex (CLI) · Alta de s48 · VEREDICTO: APROBADO
Specs/textos sustentados (jacuzzi y estacionamiento no publicados), precio 241÷2×1.15→140, array 48/48 sin regresiones, brochure "HASTA 2 HUÉSPEDES" sin "mínimo 3 noches". Salida: `..\CENTRO DE OPERACIONES\AUDITORIASesultados6-10-06-s48_codex.txt`.

### 2026-10-12 · Codex (CLI) · Lote s49–s53 · VEREDICTO: BLOQUEADO
Solicitud: `..\CENTRO DE OPERACIONES\AUDITORIAS\solicitudes6-10-12-lote-s49-s53\` · salida: `..\CENTRO DE OPERACIONES\AUDITORIASesultados6-10-12-lote-s49-s53_codex.txt`.
OK: specs, chips, precios (aritmética), regresiones (53/53) y brochures.
1. **Bloqueante — marca del proveedor en fotos:** `s49_10.jpg` ("CASA ODED" en el tapete) y `s50_10.jpg` (logo bordado en la bata). → **Claude: ACEPTADO.** Reemplazadas por fotos sin baño ni ropa de cama marcada: s49 #29 "Habitación 3 imagen 2" (habitación que no estaba en la galería) y s50 #20 "Habitación 3 imagen 1". Antes/después revisado en grande. Trazabilidad en `ingesta-s49/picks.json` y `ingesta-s50/picks.json`. Regla nueva para la curaduría: en listings de marca hotelera, baños y batas se revisan en grande antes de elegirlos.
2. **"El Poblado" en s49 y s52** no está literal en sus anuncios (sí en s50, s51 y s53). → **Claude: ACEPTADO.** desc_es/desc_en y kicker del brochure dicen "Provenza, Medellín" en s49 y s52. La `zone` del array sigue "El Poblado" porque es la taxonomía del filtro del sitio (Provenza está dentro de El Poblado; el mismo anfitrión lo escribe así en sus otros tres anuncios).
3. **s52 "discoteca privada con vista a la ciudad"** sería más fuerte que la fuente. → **Claude: REBATIDO con cita literal** de `ingesta-s52/listing.html`, sección "SALA DE DISCOTECA": *"Disfruta de impresionantes vistas a la ciudad a través de las ventanas del suelo al techo mientras bailas con un potente sistema de sonido."* Se mantiene.
4. **"mayores de 18" vs `childrenAllowed:true`** en metadatos de Airbnb. → **Claude: se mantiene la regla escrita del anfitrión** ("No se permite la entrada de menores de 18 años", literal en los cinco anuncios): es la condición más estricta y evita vender a familias a las que no dejarían entrar. La contradicción queda anotada en las fichas.
5. **Mínimo de s49 con una sola lectura; precios no reproducibles.** → **Claude: de acuerdo.** Se re-leen estadía mínima y precios en el panel de Airbnb justo antes del deploy; los precios siguen PENDIENTES de confirmación de Andrés.

### 2026-10-14 · Codex (CLI) · Lote s49–s53, ronda 2 · VEREDICTO: CONDICIONADO
OK: textos s49/s52 ("Provenza, Medellín"), rebatido de s52 aceptado (cita literal de la sala de discoteca), `zone:'El Poblado'` aceptable como taxonomía, regresiones 53/53, ninguna marca del proveedor legible en las 50 fotos. Condición: comparación reproducible de las dos fotos reemplazadas y trazabilidad en `picks_*.json`. Salida: `..\CENTRO DE OPERACIONES\AUDITORIASesultados6-10-12-lote-s49-s53_codex_R2.txt`.
→ **Claude: CUMPLIDA.** Fuentes descargadas y guardadas (`AUDITORIAS\solicitudes6-10-12-lote-s49-s53-R2uentes\FUENTE_*.jpg`), comparación a 400×267: s49_10 = 1,44 y s50_10 = 0,88 (controles contra otra foto de la galería: 58,97 y 41,44) en `comparacion_reemplazos.json`; `picks_s49.json` y `picks_s50.json` con `fetched_url`/`downloaded` del origen nuevo.

### 2026-10-14 · Claude · Precios confirmados y DEPLOY del lote s49–s53 (orden de Andrés) · `auditar: sí`
- Andrés aprobó la cotización de referencia (2026-10-14). Relectura del panel antes del deploy (`fuentes/precios/relectura_2026-10-14.json`): s49 mínimo 3 noches confirmado (segunda lectura) y sin cambio de precio; s51 y s52 iguales; s53 subió a USD 1,850 / 3 noches; s50 bajó a USD 1,000 / 2 noches.
- Decisión de Andrés: s53 → 710 (regla sobre la lectura de hoy; ANULADO 670); s50 se mantiene en 605 (la regla daría 575; 605 solo amplía el margen).
- Precios publicados: s49=785 · s50=605 · s51=605 · s52=720 · s53=710.

