# V110.3.21.3 · SKEL Internal Skeleton

Parte de V110.3.21.2 OpenSim Hamner Full-Body.

## Nueva arquitectura
Piel SKEL + joints SKEL -> esqueleto interno directo.

- Sin atlas externo para posicionar el esqueleto.
- Sin recálculo del fitting.
- Sin regenerar los 75 frames.
- El NPZ existente es suficiente.
- Radios internos estimados de forma conservadora desde la superficie SKEL.
- Longitudes segmentarias derivadas directamente de joints.
- Visor combinado piel + esqueleto.
- OpenSim Hamner se conserva como rama biomecánica opcional.

## FIX incluido
Integra el arreglo de la pestaña 12:
en modo NPZ autónomo se muestran y calculan curvas, ROM, derivadas, simetría,
coordinación, diagramas ángulo-ángulo y trayectorias 3D.

## Limitación
El esqueleto visual es genérico y organizado por anatomía segmentaria.
No es una reconstrucción morfológica individual por CT/MRI.
