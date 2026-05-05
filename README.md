# 🚀 Manila House Hub · Guía de deploy

## Qué acabamos de armar

Una mini-app web mobile-first para el Grupo Vásquez con:

```
manila-hub/
├── index.html                          ← HUB PRINCIPAL (la "app")
├── manila-house-landing.html           ← Landing pública para clientes
├── gv-holdings-dashboard.html          ← Dashboard privado del grupo
└── pdf-01...pdf-10.html                ← 10 fichas de propiedad
```

**URL final (ejemplo):** `https://TU-USUARIO.github.io/manila-hub/`

---

## Paso a paso: subir a GitHub Pages (10 min)

### 1. Crear cuenta GitHub (si no tenés)
Andá a **github.com** → Sign up → creá usuario. Ejemplo: `andresvasquez`.

### 2. Crear el repositorio
- Click en el **+** arriba a la derecha → **New repository**
- Name: `manila-hub`
- Dejá **Public**
- Marcá **Add a README file**
- Click **Create repository**

### 3. Subir los archivos
- En tu nuevo repo, click **Add file** → **Upload files**
- Arrastrá los 13 archivos HTML de esta carpeta
- Abajo: commit message "Initial hub"
- Click **Commit changes**

### 4. Activar GitHub Pages
- En tu repo, click **Settings** (arriba a la derecha)
- Menú izquierdo: **Pages**
- En "Source": elegí **Deploy from a branch**
- Branch: `main` / folder: `/ (root)` → **Save**
- Esperá 1-2 minutos

### 5. Listo
GitHub te muestra arriba: `Your site is live at https://TU-USUARIO.github.io/manila-hub/`
**Ese link es tu app.** Abrilo en el celular.

---

## Cómo usar desde el móvil

### Para VOS (Andrés):
1. Abrí `https://TU-USUARIO.github.io/manila-hub/`
2. **iPhone**: tocá Compartir → "Agregar a pantalla de inicio" → se ve como app
3. **Android**: Chrome menú → "Instalar app"

Desde ahí accedés a: Landing, Dashboard privado, y las 10 fichas.

### Para enviar a CLIENTES:
Mandá SOLO este link por WhatsApp:
`https://TU-USUARIO.github.io/manila-hub/manila-house-landing.html`

El cliente entra directo a la landing pública, **no ve el hub ni el dashboard**.

### Para mostrar una propiedad específica en persona:
Abrí el hub → tocá la propiedad → se ve la ficha completa.
O compartí link directo, ej: `.../pdf-01-pink-house.html`

---

## Cómo editar precios después

**Opción quick (desde el celu):**
1. Entrá al repo en github.com desde el celular
2. Tocá el archivo ej. `pdf-01-pink-house.html`
3. Tocá el lápiz ✏️ → editá el precio → Commit
4. En 30 segundos se ve actualizado en la web

**Opción pro (fase 2):** Google Sheet conectado — te la armo cuando digás.

---

## Próximos pasos sugeridos

- [ ] Subir a GitHub y probar el link
- [ ] Agregar logo Manila House real (reemplazar el SVG inline del icon)
- [ ] Fase 2: Google Sheet para editar precios en vivo
- [ ] Fase 3: Dominio propio `manilahouse.com` ($15/año)
- [ ] Agregar las 30+ propiedades de terceros
