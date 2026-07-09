# Plan: hacer el sitio bilingüe (ES/EN)

Estado: **planeado, no iniciado**. Este documento es la referencia para retomar el trabajo en una sesión futura con Claude Code.

## Contexto y decisión de alcance

- El sitio (Astro 5, `src/pages/**/*.astro`, contenido en `src/content/**/*.md`) está hoy 100% en español, sin ninguna infraestructura de i18n activa.
- El *schema* de contenido (`src/content/config.ts`) ya anticipa bilingüismo: varios campos existen pareados `_es` / `_en` (`bio_short_es/en`, `interests_es/en`, `objective_es/en`, `methods_es/en`). Ningún `.astro` los usa todavía (0 referencias a `_en` en `src/pages` o `src/components`).
- **Decisión ya tomada (2026-07-09):** las publicaciones (título, abstract, autores, journal, etc.) **no se traducen** — se muestran en su idioma original de publicación, sea cual sea. Esto es clave porque publicaciones son ~130 archivos de contenido, la mayoría del sitio, y quedan fuera del esfuerzo de traducción de contenido. Solo los *labels* fijos alrededor de ellas (secciones, botones, tipos de publicación) entran al diccionario de UI.

Con esa decisión, el trabajo de traducción de **contenido** se reduce a un conjunto pequeño y acotado (ver tabla abajo). El grueso del esfuerzo restante es mecánico: diccionario de UI + activar el ruteo i18n de Astro.

## 1. Ruteo i18n de Astro

Astro 5 tiene i18n nativo, no hace falta librería externa.

- Añadir a `astro.config.mjs`:
  ```js
  i18n: {
    locales: ['es', 'en'],
    defaultLocale: 'es',
    routing: { prefixDefaultLocale: false }, // /es/... sin prefijo, /en/... con prefijo
  }
  ```
- Decidir estructura de páginas: opción recomendada es mover cada página a `src/pages/[...]` duplicada bajo `src/pages/en/[...]`, o usar un helper que genere ambas rutas desde un solo archivo (Astro soporta `getStaticPaths` con locale). Para un sitio de este tamaño (~25 archivos `.astro`, la mayoría con muy poca lógica), duplicar carpeta `en/` que reexporta/parametriza puede ser más simple que abstraer todo con un sistema de traducción dinámico.
- `src/layouts/Base.astro:26` tiene `<html lang="es">` hardcodeado — debe volverse dinámico según el locale de la página (`Astro.currentLocale` o prop pasada al layout).
- Falta añadir selector de idioma en `Nav.astro` (o `Footer.astro`) para que el usuario cambie entre ES/EN.
- Revisar `astro.config.mjs` → `sitemap()` integration: en Astro 5 el plugin de sitemap detecta i18n automáticamente si `i18n` está configurado, pero conviene verificar el sitemap generado tenga las URLs `/en/...` con `hreflang` correcto.

## 2. Diccionario de strings de UI

Los 25 archivos `.astro` (páginas + componentes en `src/pages/` y `src/components/`) tienen texto fijo en español hardcodeado: títulos de sección ("Líneas de Investigación", "Semilleros", "Integrantes"...), labels ("Ver todos →", "Semillero", "Línea 1"...), botones ("Ver publicación →", "Ver libro →"), etc.

Plan:
- Crear `src/i18n/es.ts` y `src/i18n/en.ts` (o un solo `src/i18n/strings.ts` con objeto `{ es: {...}, en: {...} }`) con todas las claves de UI.
- Crear un helper `t(key, locale)` o similar, importado donde se necesite.
- **Caso especial ya detectado**: los labels de `pub_type` (`article`, `book`, `book-chapter`, `preprint`, etc.) están **duplicados como objetos literales en 4 archivos distintos**:
  - `src/pages/index.astro:33`
  - `src/pages/publicaciones/index.astro:32`
  - `src/pages/publicaciones/[slug].astro:37`
  - `src/components/PublicationCard.astro:28`

  Esto se debe centralizar en un solo lugar (parte del diccionario de i18n, con una clave por `pub_type` en cada idioma) — es limpieza de código además de requisito de i18n.
- También revisar `src/components/PublicationsByYear.astro` y `src/components/CitationChart.astro`, que tienen sus propios labels de grupo ("Artículos / Preprints", "Libros / Capítulos") repetidos entre sí — mismo problema de duplicación, mismo fix.

## 3. Contenido a traducir (campos `_en` ya definidos en el schema)

Rellenar los campos `_en` faltantes en `src/content/`. Estado actual:

| Colección | Total archivos | Con `_en` ya relleno | Pendientes |
|---|---|---|---|
| `researchers` | 7 | 2 (`juan-david-leongomez.md`, `milena-vasquez-amezquita.md`) | `ana-maria-salazar.md`, `andres-felipe-reyes.md`, `fidel-mauricio-bonilla.md`, `miguel-puentes-escamilla.md`, `oscar-sanchez.md` |
| `labs` | 2 | 0 | `evoco.md`, `labpsiexp.md` |
| `semilleros` | 5 | 0 | `dicomh.md`, `metaciencia.md`, `neurogroup.md`, `psicoevo.md`, `sexcog.md` |
| `auxiliares` | 1 | 0 | `valentina-cepeda.md` |
| `publications` | 130 | N/A | **no se traducen** (decisión tomada, ver arriba) |

Campos a rellenar por entrada (donde aplique): `bio_short_en`, `interests_en`, `objective_en`, `methods_en`.

**Decisión tomada (2026-07-09): sí se traducen.** Los siguientes campos hoy son un solo string en el schema (sin `_es`/`_en`) y deben convertirse en pares, igual que `bio_short_es/en`:

- `academic_role` (ej. "Profesor Titular" → `academic_role_es` / `academic_role_en`).
- `codec_role` (ej. "Líder CODEC, Investigador EvoCo, Director MetaCiencia" → `codec_role_es` / `codec_role_en`).
- `education[].degree` (ej. "Psicología", "Especialización en Ansiedad y Estrés" → `degree_es` / `degree_en` dentro de cada objeto de `education`).

Esto implica:

1. Actualizar `config.ts`: en `researchers` y `auxiliares`, separar `academic_role` → `academic_role_es`/`academic_role_en`, `codec_role` → `codec_role_es`/`codec_role_en` (mantener default en `auxiliares` como `codec_role_es` con default `'Auxiliar de Investigación'`, y agregar el default en inglés), y en el objeto de `education`, separar `degree` → `degree_es`/`degree_en`.
2. Actualizar todos los `.md` de `researchers` y `auxiliares` (7 + 1 = 8 archivos) para usar los nuevos nombres de campo y rellenar la variante `_en`.
3. Actualizar cualquier `.astro` que lea `academic_role`, `codec_role` o `education[].degree` (revisar `ResearcherCard.astro`, `AuxiliarCard.astro`, `investigadores/[slug].astro`, `auxiliares/[slug].astro`) para leer el campo según el locale activo.

Las instituciones de `education[].institution` (ej. "University of Stirling (Stirling, Reino Unido)") sí incluyen la ciudad/país traducida en español dentro del mismo string — pendiente de decidir si eso también se separa en `_es`/`_en`, o si se deja como está y solo se traduce el nombre del país en el diccionario de UI si se quiere consistencia total. No decidido aún.

Los textos largos "bio larga" en `INFO/info.md` no están en el frontmatter del `.md` de contenido (solo existen en el documento informativo, no se renderizan en el sitio) — si en el futuro se agregan al sitio, deberán nacer ya como par `bio_long_es`/`bio_long_en`.

## 4. Orden de trabajo sugerido

1. Activar i18n en `astro.config.mjs` y volver dinámico `lang` en `Base.astro`.
2. Actualizar `config.ts`: separar `academic_role` → `academic_role_es`/`academic_role_en`, `codec_role` → `codec_role_es`/`codec_role_en`, y `education[].degree` → `degree_es`/`degree_en` (ver punto 3; incluye decidir qué hacer con `education[].institution`).
3. Construir el diccionario de UI (`src/i18n/`) y reemplazar strings hardcodeados en los 25 `.astro`, centralizando de paso los `pub_type` labels duplicados.
4. Duplicar/generar rutas `/en/...` para cada página existente.
5. Rellenar campos `_en` pendientes en researchers/labs/semilleros/auxiliares: `bio_short_en`, `interests_en`, `objective_en`, `methods_en`, `academic_role_en`, `codec_role_en`, `degree_en` (contenido, no código).
6. Añadir selector de idioma en Nav/Footer (propuesta: toggle de texto "ES | EN" a la derecha del nav de escritorio, fila propia en el menú móvil — ver discusión en la conversación del 2026-07-09, aún no confirmado).
7. Verificar sitemap y `hreflang`.
8. Probar navegación completa en ambos idiomas antes de dar por cerrado (`/verify` o revisión manual en navegador).

## Notas

- Astro version en uso: `^5.0.0` (soporta i18n routing nativo).
- No hay librerías de i18n instaladas todavía (`package.json` no tiene `astro-i18next`, `i18next`, etc.) — no se necesitan, Astro nativo alcanza para este tamaño de sitio.
- Este documento fue generado explorando el código el 2026-07-09; si el schema de `config.ts` o la estructura de `src/pages` cambian antes de retomar esto, revalidar los conteos y rutas de archivo citados aquí.
