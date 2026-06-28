export const LINES = {
  line1: {
    id: 'line1',
    name_es: 'Evolución y Comportamiento Humano',
    name_en: 'Evolution and Human Behavior',
    color: '#ff5555',
  },
  line2: {
    id: 'line2',
    name_es: 'Neurociencias cognitivo-afectivas',
    name_en: 'Cognitive-Affective Neurosciences',
    color: '#a451ff',
  },
  line3: {
    id: 'line3',
    name_es: 'Neuropsicología',
    name_en: 'Neuropsychology',
    color: '#00a6b0',
  },
  transversal: {
    id: 'transversal',
    name_es: 'Transversal',
    name_en: 'Transversal',
    color: '#d400aa',
  },
} as const;

export type LineId = keyof typeof LINES;
