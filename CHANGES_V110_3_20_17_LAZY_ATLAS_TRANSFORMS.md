# V110.3.20.17 · Lazy Anatomical Atlas + Transform Streaming

## Motivo
V110.3.20.16 descargó correctamente 24 huesos + 40 músculos, pero podía agotar memoria
al materializar 64 mallas anatómicas × 75 frames y serializarlas completas a Plotly.

## Arquitectura nueva
- Una sola malla base real por estructura.
- Por frame sólo se guardan:
  - matriz 3×3,
  - escala,
  - traslación.
- No se crean 75 copias completas de los vértices anatómicos.
- La anatomía se prepara bajo demanda:
  - Piel
  - Huesos reales
  - Músculos reales
  - Todas
- Huesos/Músculos no se cargan hasta seleccionar la capa.
- El navegador aplica las transformaciones frame a frame.
- El exportador MP4 también materializa sólo una estructura/un frame cada vez.

## Resultado esperado
Reducción drástica de RAM y del payload respecto a V20.16.
Se mantiene:
- NPZ autónomo;
- 75 frames SKEL;
- BodyParts3D real;
- sin geometría falsa;
- sin Supabase para mallas;
- exportación de vídeo por capas.
