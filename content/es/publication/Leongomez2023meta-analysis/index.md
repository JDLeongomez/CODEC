---
title: "Meta-análisis de correlaciones y meta-regresión en R: Guía práctica"
authors:
- juan-david-leongomez
author_notes:
#- Autor de correspondencia
#- Autor de correspondencia
date: "2023-04-07 00:00:00"
doi: "10.31222/osf.io/yaxd4"

# Schedule page publish date (NOT publication's date).
publishDate: ""

# Publication type.
# Accepts a single type but formatted as a YAML list (for Hugo requirements).
# Enter a publication type from the CSL standard.
publication_types: ["doc"]

# Publication name and optional abbreviated publication name.
publication: "*MetaArXiv*"
publication_short: ""

abstract: "El meta-análisis es un método ampliamente utilizado para sintetizar los
  datos de diferentes estudios. Sin embargo, a menudo estudiantes, profesionales e
  investigadores carecemos de conocimientos prácticos para hacer e interpretar un
  meta-análisis. Esta guía presenta una variedad de herramientas para realizar meta-análisis
  de correlaciones en R, mediante el uso de ejemplos reales. Incluye desde análisis
  simples y su interpretación, hasta el análisis de moderadores (meta-regresión),
  usando los paquetes metafor (Viechtbauer, 2010) y metaviz (Kossmeier et al., 2020).
  También incluye explicaciones para la transformación de coeficientes r de Pearson
  a z de Fisher (y viceversa), creación de gráficos de bosque (forest plots) y gráficos
  de embudo (funnel plots), análisis de heterogeneidad y diagnósticos de influencia,
  así como estrategias para detectar posibles sesgos de publicación utilizando el
  paquete weightr (Coburn & Vevea, 2019), y para determinar el poder estadístico de
  un meta-análisis utilizando metameta (Quintana, 2022). Con esta guía, los lectores
  podrán adquirir las habilidades necesarias para realizar meta-análisis de correlaciones
  de manera efectiva en R y obtener resultados confiables."

# Summary. An optional shortened abstract.
# summary: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis posuere tellus ac convallis placerat.

tags:
- Meta-analisis
- Correlación
- Tamaño de efecto
- Tamaño de muestra
- Error tipo I
- Error tipo II
- R
- Tutorial

featured: false

# links:
# - name: ""
#   url: ""
url_pdf: https://osf.io/preprints/metaarxiv/yaxd4/
url_dataset: ''
url_code: https://osf.io/na4p9/
url_poster: ''
url_preprint: ''
url_project: ''
url_slides: ''
url_source: ''
url_video: ''

# Featured image
# To use, add an image named `featured.jpg/png` to your page's folder. 
image:
# caption: 'Image credit: [**Unsplash**](https://unsplash.com/photos/jdD8gXaTZsc)'
  focal_point: ""
  preview_only: false

# Associated Projects (optional).
#   Associate this publication with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `internal-project` references `content/project/internal-project/index.md`.
#   Otherwise, set `projects: []`.
projects: []

# Slides (optional).
#   Associate this publication with Markdown slides.
#   Simply enter your slide deck's filename without extension.
#   E.g. `slides: "example"` references `content/slides/example/index.md`.
#   Otherwise, set `slides: ""`.
slides: ''
---
{{< metrics >}}
