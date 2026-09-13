# V110.3.21.1 · OpenSim bridge fix

Correcciones sobre la prueba real de V110.3.21.0:

1. Descarga de geometrías:
   - .21.0 buscaba las 81 referencias sólo en `Models/Rajagopal/Geometry`.
   - muchas geometrías compartidas están en el `Geometry/` general de opensim-models.
   - .21.1 prueba automáticamente ambas ubicaciones y Rajagopal_OpenSense como tercer fallback.

2. Error `bone_parts is not defined`:
   - eliminado como causa de caída del visor/exportador legado.

3. Registro visual de huesos largos:
   - .21.0 interpretaba mal el eje longitudinal de las mallas OpenSim.
   - los huesos largos OpenSim se anclan ahora desde MAX-Y (proximal) hacia -Y (distal).
   - el extremo proximal coincide con el joint proximal SKEL.
   - el escalado se calcula sólo en frame 0 y no cambia durante el ciclo.

4. Pelvis:
   - deja de tratarse como un hueso largo pelvis→cadera derecha.
   - usa una escala estática basada en anchura inter-caderas y se centra en pelvis SKEL.

5. Sin geometría inventada:
   - VTP no legibles siguen reportándose; no se reemplazan por primitivas.

Limitación:
Este visor todavía NO ejecuta IK OpenSim ni aplica las SpatialTransform completas del
Rajagopal2016. Es una etapa de validación de descarga, geometría y registro visual.
