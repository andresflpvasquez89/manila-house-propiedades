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

