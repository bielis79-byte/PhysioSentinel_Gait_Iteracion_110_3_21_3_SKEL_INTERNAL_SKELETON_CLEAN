# V110.3.20.18 · Incremental Anatomical Viewer

## Problema resuelto
V110.3.20.17 eliminó la duplicación Python de 64 mallas × 75 frames, pero el navegador
todavía recibía demasiada geometría anatómica a la vez y Streamlit podía bloquearse.

## Nueva arquitectura
- El NPZ sigue reutilizando sus 75 frames: no hay que recalcularlos.
- BodyParts3D sigue siendo la fuente de geometría anatómica real.
- El visor ya NO recibe anatomía para los 75 frames.
- Se transmite únicamente el frame anatómico actualmente seleccionado.
- Huesos y músculos se preparan sólo cuando se seleccionan.
- Para navegador se aplica LOD de caras preservando la geometría BodyParts3D:
  - huesos: hasta ~1400 caras por estructura
  - músculos: hasta ~900 caras por estructura
- Se compactan vértices no utilizados tras el muestreo de caras.
- La malla original no se modifica y sigue disponible para exportación MP4 offline.
- El movimiento de frame se controla desde el slider Streamlit; cada cambio reconstruye
  sólo ese frame.
- La piel también se transmite sólo para el frame actual.

## Ventaja
Reduce radicalmente:
- memoria del navegador,
- JSON enviado al componente,
- carga Plotly,
- riesgo de caída de Streamlit.

## Conservado
- NPZ autónomo
- 75 frames SKEL
- 24 joints
- 46 q(t)
- atlas BodyParts3D real
- sin geometría procedural/falsa
- sin almacenar atlas en Supabase
- exportador MP4 offline
