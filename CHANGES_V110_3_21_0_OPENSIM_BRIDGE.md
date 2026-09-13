# V110.3.21.0 · OpenSim Musculoskeletal Bridge

## Decisión
Se abre una rama nueva basada en OpenSim/Rajagopal2016 en lugar de seguir intentando
convertir BodyParts3D en un modelo biomecánico.

## Qué añade
- Descarga bajo demanda del modelo oficial `Rajagopal2016.osim`.
- Descarga bajo demanda de las geometrías referenciadas por el propio `.osim`.
- Caché temporal del runtime; no se guarda en Supabase ni en el NPZ.
- Parser ligero de geometrías VTP ASCII.
- Primera vista experimental del miembro inferior.
- Mapeo a joints SKEL:
  pelvis, fémur, tibia, astrágalo/calcáneo y pie.
- Escalado sólo en el frame de referencia.
- No hay estiramiento frame-a-frame.

## Qué NO se afirma
- Las geometrías OpenSim no son superficies CT/MRI de alta resolución del paciente.
- No se infieren fuerzas musculares, activación, momentos articulares ni GRF.
- El objetivo de esta rama es aprovechar una estructura musculoesquelética biomecánica
  coherente, no vender la geometría de visualización como anatomía clínica individual.

## Siguiente etapa
- Importar transformaciones articulares del `.osim`.
- Mapear los q(t) SKEL a coordenadas OpenSim.
- Mantener cada body OpenSim como cuerpo rígido.
- Añadir musculotendones como líneas/path points biomecánicos.
