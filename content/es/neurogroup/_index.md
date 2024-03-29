---
title: EvoCo
type: landing

# Listing view
view: compact

# Your landing page sections - add as many different content blocks as you like
sections:
  - block: markdown
    id: section-1
    content:
      title: Section 1
      subtitle: A subtitle
      text: Add any **markdown** formatted content here - text, images, videos, galleries - and even HTML code!
  - block: people
    content:
      title: Conoce al equipo
      # Choose which groups/teams of users to display.
      #   Edit `user_groups` in each user's profile to add them to one or more of these groups.
      user_groups:
          - EvoCo
      sort_by: Params.last_name
      sort_ascending: true
    design:
      show_interests: false
      show_role: true
      show_social: true
---
