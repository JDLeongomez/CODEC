---
# Leave the homepage title empty to use the site title
title:
type: landing

sections:

  - block: about.biography
    id: about
    content:
      title: Acerca del grupo
      # Choose a user profile to display (a folder name within `content/authors/`)
      username: codec

  - block: people
    content:
      title: Laboratorios y semilleros de investigación
      # Choose which groups/teams of users to display.
      #   Edit `user_groups` in each user's profile to add them to one or more of these groups.
      user_groups:
          - Laboratorios y Semilleros
      sort_by: .Weight
      sort_ascending: true
    design:
      show_interests: false
      show_role: true
      show_social: true

  - block: skills
    content:
      title: 
      text: ''
      # Choose a user to display skills from (a folder name within `content/authors/`)
      username: codec
    design:
      columns: '1'

  - block: people
    content:
      title: Investigadoras e investigadores
      # Choose which groups/teams of users to display.
      #   Edit `user_groups` in each user's profile to add them to one or more of these groups.
      user_groups:
          - Investigadoras e investigadores
      sort_by: .Weight
      sort_ascending: true
    design:
      show_interests: false
      show_role: true
      show_social: true
  
  - block: portfolio
    id: projects
    content:
      title: Proyectos
      filters:
        folders:
          - project
      # Default filter index (e.g. 0 corresponds to the first `filter_button` instance below).
      default_button_index: 0
      # Filter toolbar (optional).
      # Add or remove as many filters (`filter_button` instances) as you like.
      # To show all items, set `tag` to "*".
      # To filter by a specific tag, set `tag` to an existing tag name.
      # To remove the toolbar, delete the entire `filter_button` block.
      buttons:
        - name: Todos
          tag: '*'
        - name: Rostro humano
          tag: Rostro humano
        - name: Voz humana
          tag: Voz humana
        - name: Modulación de la voz
          tag: Modulación de la voz
        - name: Inmunocompetencia
          tag: Inmunocompetencia
        - name: Niveles hormonales
          tag: Niveles hormonales
        - name: Potenciales evocados
          tag: Potenciales evocados
        - name: Sexo
          tag: Sexo
        - name: Atractivo
          tag: Atractivo
        - name: Mortalidad
          tag: Mortalidad
        - name: Evolución
          tag: Evolución
          
    design:
      # Choose how many columns the section has. Valid values: '1' or '2'.
      columns: '2'
      view: showcase
      # For Showcase view, flip alternate rows?
      flip_alt_rows: false
      
  - block: tag_cloud
    content:
      title: Temas populares
    design:
      columns: '2'
      font_size_min: 0.7
      font_size_max: 1.5
---
