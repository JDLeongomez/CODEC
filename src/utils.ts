export const slug = (id: string) => id.replace(/\.md$/, '');

// Convierte un subconjunto mínimo de Markdown en línea (negrita, cursiva, enlaces)
// a HTML, para usarlo en campos de texto plano del front matter (p. ej. abstract).
export function inlineMarkdown(text: string): string {
  const escapeHtml = (s: string) =>
    s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  return escapeHtml(text)
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" class="underline hover:no-underline" target="_blank" rel="noopener noreferrer">$1</a>');
}
