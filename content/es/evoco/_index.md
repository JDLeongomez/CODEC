---
title: EvoCo
type: landing

# Listing view
view: compact

# Your landing page sections - add as many different content blocks as you like
sections:
  - block: hero
    content:
      title: '<p style="color:#FF8080";><strong><i>EvoCo</i></strong>: Laboratorio de Evolución y Comportamiento Humano</p>'
      image:
        filename: Logo_EvoCo.png
      text: |
        <br>
        
        ***EvoCo*** es una iniciativa en curso que busca constituirse como centro de investigación. Fue fundado en 2015[^1] por su director {{% mention "oscar-r.-sanchez" %}}. Principalmente estudiamos el comportamiento humano desde una perspectiva evolutiva. Realizamos proyectos experimentales (y algunos de minería de datos) sobre diversos temas, desde elección de pareja hasta efectos hormonales en el comportamiento, incluyendo análisis de voces y rostros.
        [^1]: Inicialmente se llamó "*Laboratorio de Análisis del Comportamiento Humano (LACH)*".
  
  - block: markdown
    content:
      title: Objetivo
      subtitle: texto
      text: '+ Aportar a la comprensión del comportamiento y la cognición humana, a partir de modelos que incorporan perspectivas evolutivas y consideran los contextos socioculturales específicos de las poblaciones estudiadas'
    design:
      columns: '1'
  
  - block: people
    content:
      title: Investigadores
      # Choose which groups/teams of users to display.
      #   Edit `user_groups` in each user's profile to add them to one or more of these groups.
      user_groups:
          - EvoCo
      sort_by: Params.last_name
      sort_ascending: false
    design:
      show_interests: false
      show_role: true
      show_social: true
---
