import { defineCollection, reference, z } from 'astro:content';

const researchers = defineCollection({
  type: 'content',
  schema: z.object({
      name:          z.string(),
      academic_role: z.string(),
      codec_role:    z.string(),
      email:         z.string().email(),
      weight:        z.number().default(99),
      avatar:        z.string(),

      bio_short_es:  z.string().optional(),
      bio_short_en:  z.string().optional(),
      interests_es:  z.array(z.string()).optional(),
      interests_en:  z.array(z.string()).optional(),

      education: z.array(z.object({
        degree:      z.string(),
        institution: z.string(),
        year:        z.union([z.number(), z.string()]),
      })).optional(),

      scholar:       z.string().url().optional(),
      orcid:         z.string().optional(),
      scopus:        z.string().url().optional(),
      cvlac:         z.string().url().optional(),
      researchgate:  z.string().url().optional(),
      website:       z.string().url().optional(),
      twitter:       z.string().optional(),
      linkedin:      z.string().url().optional(),
      instagram:     z.string().optional(),
      bluesky:       z.string().optional(),

      labs:       z.array(reference('labs')).optional(),
      semilleros: z.array(reference('semilleros')).optional(),
    }),
});

const labs = defineCollection({
  type: 'content',
  schema: z.object({
    name:          z.string(),
    short_name:    z.string(),
    director:      reference('researchers'),
    founded:       z.number().optional(),
    research_line: z.string(),
    color:         z.string(),
    logo_light:    z.string(),
    logo_dark:     z.string(),

    objective_es:  z.string().optional(),
    objective_en:  z.string().optional(),
    methods_es:    z.array(z.string()).optional(),
    methods_en:    z.array(z.string()).optional(),

    email:         z.string().email().optional(),
    website:       z.string().url().optional(),
    instagram:     z.string().optional(),
    twitter:       z.string().optional(),
  }),
});

const semilleros = defineCollection({
  type: 'content',
  schema: z.object({
    name:          z.string(),
    short_name:    z.string(),
    director:      reference('researchers'),
    lab:           reference('labs').optional(),
    research_line: z.string(),
    color:         z.string(),
    logo_light:    z.string().optional(),
    logo_dark:     z.string().optional(),
    founded:       z.number().optional(),

    objective_es:  z.string().optional(),
    objective_en:  z.string().optional(),
    methods_es:    z.array(z.string()).optional(),
    methods_en:    z.array(z.string()).optional(),

    email:         z.string().email().optional(),
    website:       z.string().url().optional(),
    instagram:     z.string().optional(),
    twitter:       z.string().optional(),
  }),
});

const publications = defineCollection({
  type: 'content',
  schema: z.object({
    title:            z.string(),
    year:             z.number(),
    authors:          z.array(z.string()),
    internal_authors: z.array(reference('researchers')).optional(),
    doi:              z.string().optional(),
    journal:          z.string().optional(),
    volume:           z.string().optional(),
    issue:            z.string().optional(),
    pages:            z.string().optional(),
    abstract:         z.string().optional(),
    pdf:              z.string().url().optional(),
    preprint:         z.string().url().optional(),
    pub_type:         z.enum(['article', 'book-chapter', 'book', 'conference', 'preprint', 'thesis', 'other']).default('article'),
    featured:         z.boolean().default(false),
  }),
});

export const collections = { researchers, labs, semilleros, publications };
