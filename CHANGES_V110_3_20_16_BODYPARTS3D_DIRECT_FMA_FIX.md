# V110.3.20.16 · BodyParts3D Direct FMA Fix

## Causa del fallo V110.3.20.15
La V20.15 intentaba descubrir el árbol completo del repositorio mediante GitHub API.
En Streamlit Cloud esa ruta puede fallar por rate-limit / acceso API / respuesta de árbol,
por lo que terminaba con 0 mallas aunque los STL públicos sí existiesen.

## Corrección
- Eliminada la dependencia de GitHub API.
- Eliminada la búsqueda dinámica del árbol.
- Cada estructura usa un FMA ID confirmado y una URL RAW determinista:
  `.../assets/BodyParts3D_data/stl/FMA<ID>.stl`
- Un fallo puntual ya no invalida todo el atlas.
- Se muestran contadores separados de huesos/músculos cargados.
- Se muestra diagnóstico de descarga si falla.

## Atlas inicial
24 huesos reales + >30 piezas musculares reales prioritarias.
No hay cilindros/conos/fusiformes de respaldo.

## Persistencia
Sólo caché temporal runtime.
Nada se sube a Supabase ni se incorpora al NPZ del paciente.
