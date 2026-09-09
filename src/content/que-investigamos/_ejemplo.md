---
# PLACEHOLDER — este archivo empieza con "_" así que Astro lo IGNORA (no aparece en /que-investigamos).
# Copia este archivo sin el "_" inicial y complétalo para agregar una pregunta real.
#
# Nombre del archivo: 1-2 palabras clave de la pregunta, en kebab-case (ej. "rostro-atractivo.md"),
#   no "pregunta1.md". El nombre del archivo se vuelve la URL en /respuesta/<id>, así que conviene
#   que sea descriptivo. Si la pregunta tiene un PDF/audio propio en public/que-investigamos/,
#   usa la misma palabra clave en PascalCase para el archivo (ej. "RostroAtractivo.pdf").
#
# investigador y auxiliar: al menos uno de los dos debe estar presente (referencia al id
#   del archivo .md en src/content/researchers/ o src/content/auxiliares/, sin extensión).
#   Pueden usarse ambos a la vez si la pregunta tiene un investigador y un/a auxiliar como autores.
# lab y semillero: opcionales, referencia al id del archivo .md correspondiente. Pueden usarse
#   ambos a la vez si el lab y el semillero comparten línea de investigación (el color de borde
#   de la tarjeta se toma del lab si hay uno; si no, del semillero).
#
# Los tres campos siguientes (respuesta_url, video_url, audio_url) NO son alternativas — si una
# pregunta tiene varios formatos (ej. podcast Y presentación), se definen todos y se muestran
# juntos, en ese orden, en la misma página /respuesta/<id-del-archivo>. El botón "Ver respuesta"
# del acordeón siempre lleva ahí, sin importar cuántos formatos tenga. Al menos uno es obligatorio.
#
# respuesta_url: ruta relativa a un PDF en public/ (ej. "/que-investigamos/RostroAtractivo.pdf") —
#   se embebe en la página. Si es una URL externa (https://...), se muestra como botón "Abrir
#   presentación" que abre esa URL en una pestaña nueva (no se puede embeber un sitio externo).
#
# video_url: opcional. Va la URL del EMBED del reproductor (ej. de Vimeo:
#   "https://player.vimeo.com/video/ID?h=HASH", NO "https://vimeo.com/ID"). Se embebe en la página.
#
# audio_url: opcional (podcast). Ruta a un archivo de audio en public/que-investigamos/ (junto a los PDF,
#   ej. "/que-investigamos/Pregunta5.m4a"). Antes de subirlo, reencodar a AAC mono ~96kbps con ffmpeg si
#   viene en mayor calidad — de sobra para voz hablada y reduce bastante el peso:
#   ffmpeg -i original.m4a -ac 1 -c:a aac -b:a 96k -movflags +faststart public/que-investigamos/PreguntaN.m4a
#
# ia_nota: opcional. Texto de transparencia si se usó IA en el PDF, video o audio (ej. voces de
#   podcast generadas con IA, diapositivas hechas con ayuda de IA). Aparece como un aviso pequeño
#   debajo de los autores, al pie de /respuesta/<id-del-archivo>. Especialmente importante en
#   audio: una voz con acento distinto puede hacer pensar que la respondió alguien más sin dar
#   crédito, así que hay que aclarar que es generada por IA.

pregunta: "¿Ejemplo de pregunta de divulgación?"
investigador: nombre-del-archivo-investigador
respuesta_url: "https://ejemplo.com/respuesta"
orden: 1
---
