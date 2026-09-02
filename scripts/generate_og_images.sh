#!/usr/bin/env bash
# Generates 1200x630 Open Graph / Twitter Card images for CODEC and each semillero,
# used as social-share previews (og:image / twitter:image) in Base.astro.
#
# Requires ImageMagick 7 (`magick`) and the Inter font family.
# Run from anywhere: bash scripts/generate_og_images.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGOS="$REPO_ROOT/public/logos"
OUT="$REPO_ROOT/public/og"
FONTS="$HOME/.local/share/fonts/Inter/extras/otf"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$OUT"

BOLD="$FONTS/Inter-Bold.otf"
MEDIUM="$FONTS/Inter-Medium.otf"
DISPLAY_XBOLD="$FONTS/InterDisplay-ExtraBold.otf"
CODEC_LOGO="$LOGOS/CODEC_claro.png"

gen_card() {
  local slug="$1" color="$2" logo="$3" eyebrow="$4" bigtext="$5" subtitle="$6" badge="${7:-true}"

  # Soft white -> tinted-color gradient wash in the bottom-right corner.
  magick -size 1600x1600 radial-gradient:"${color}"-none \
    -alpha set -channel A -evaluate multiply 0.30 +channel "$WORK/glow.png"
  magick -size 1200x630 xc:white "$WORK/glow.png" \
    -gravity NorthWest -geometry +400-170 -compose over -composite "$WORK/bg.png"

  # Logo badge, scaled to a fixed height, with a soft drop shadow.
  magick "$logo" -resize x480 \
    \( +clone -background black -shadow 45x18+0+14 \) +swap -background none \
    -layers merge +repage "$WORK/logo.png"

  magick "$WORK/bg.png" "$WORK/logo.png" -gravity West -geometry +70+0 \
    -compose over -composite "$WORK/step1.png"

  magick "$WORK/step1.png" \
    -font "$BOLD" -pointsize 26 -fill "$color" -gravity NorthWest \
    -annotate +500+160 "$eyebrow" \
    "$WORK/step2.png"

  magick "$WORK/step2.png" \
    -font "$DISPLAY_XBOLD" -pointsize 92 -fill "#1a1a1a" -gravity NorthWest \
    -annotate +495+195 "$bigtext" \
    "$WORK/step3.png"

  magick -background none -fill "#555555" -font "$MEDIUM" -pointsize 30 -size 620x160 \
    caption:"$subtitle" "$WORK/desc.png"
  magick "$WORK/step3.png" "$WORK/desc.png" -gravity NorthWest -geometry +500+320 \
    -compose over -composite "$WORK/step4.png"

  if [ "$badge" = "true" ]; then
    # "Parte de [CODEC]" badge, tucked into the bottom-right whitespace.
    magick "$CODEC_LOGO" -resize x130 \
      \( +clone -background black -shadow 35x12+0+9 \) +swap -background none \
      -layers merge +repage "$WORK/codec_badge.png"
    magick "$WORK/step4.png" "$WORK/codec_badge.png" -gravity SouthEast -geometry +60+30 \
      -compose over -composite "$WORK/step5.png"
    magick "$WORK/step5.png" \
      -font "$MEDIUM" -pointsize 22 -fill "#9a9a9a" -gravity SouthEast \
      -annotate +65+195 "Parte de" \
      -depth 8 -strip \
      "$OUT/$slug.png"
  else
    magick "$WORK/step4.png" -depth 8 -strip "$OUT/$slug.png"
  fi

  echo "Generated $OUT/$slug.png"
}

gen_card "codec" "#ffb600" "$LOGOS/CODEC_claro.png" \
  "GRUPO DE INVESTIGACIÓN" "CODEC" "Ciencias Cognitivas y del Comportamiento" "false"

gen_card "metaciencia" "#d400aa" "$LOGOS/MetaCiencia_claro.png" \
  "TRANSVERSAL" "MetaCiencia" "Ciencia abierta, reproducible y transparente"

gen_card "dicomh" "#a451ff" "$LOGOS/DiCoMH_claro.png" \
  "NEUROCIENCIAS COGNITIVO-AFECTIVAS" "DiCoMH" "Diferencias Cognitivas entre Mujeres y Hombres"

gen_card "neurogroup" "#00a6b0" "$LOGOS/NeuroGroup_claro.png" \
  "NEUROPSICOLOGÍA" "NeuroGroup" "Neuropsicología del envejecimiento"

gen_card "psicoevo" "#ff5555" "$LOGOS/PsicoEvo_claro.png" \
  "EVOLUCIÓN Y COMPORTAMIENTO HUMANO" "PsicoEvo" "Psicología Evolutiva"

gen_card "sexcog" "#a451ff" "$LOGOS/SexCog_claro.png" \
  "NEUROCIENCIAS COGNITIVO-AFECTIVAS" "SexCog" "Sexualidad y afectividad humana"

gen_card "evoco" "#ff5555" "$LOGOS/EvoCo_claro.png" \
  "LABORATORIO" "EvoCo" "Laboratorio de Evolución y Comportamiento Humano"

gen_card "labpsiexp" "#a451ff" "$LOGOS/LabPsiExp_claro.png" \
  "LABORATORIO" "LabPsiExp" "Laboratorio de Psicología Experimental"
