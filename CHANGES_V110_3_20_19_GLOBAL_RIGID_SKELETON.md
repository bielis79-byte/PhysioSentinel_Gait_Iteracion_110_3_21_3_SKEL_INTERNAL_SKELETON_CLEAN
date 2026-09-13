# V110.3.20.19 · BodyParts3D Global Rigid Skeleton

## Cambio de planteamiento
La V110.3.20.18 demostró que las mallas BodyParts3D reales se descargaban y podían
mostrarse, pero el registro por pieza mediante PCA + estiramiento proximal-distal
producía anatomía incorrecta.

La V110.3.20.19 elimina ese método para el esqueleto.

## Nuevo registro
1. Todas las mallas óseas se mantienen en el sistema de coordenadas común de BodyParts3D.
2. Se calcula una única transformación de similitud global atlas → SKEL en el frame 1:
   - escala global,
   - rotación global,
   - traslación global.
3. Cada hueso recibe sólo una corrección de posición estática en el frame de referencia.
4. Después se expresa como cuerpo rígido respecto a su segmento SKEL.
5. Para cada frame sólo cambia:
   - rotación rígida,
   - traslación.
6. No existe escalado frame a frame y no se estiran los huesos.

## Alcance de esta versión
Se valida PRIMERO el esqueleto:
- pelvis / hip bones
- fémur
- patela
- tibia
- peroné
- astrágalo
- calcáneo
- escápula
- clavícula
- húmero
- radio
- cúbito

Los músculos quedan temporalmente desactivados hasta validar el ensamblaje óseo.

## Rendimiento
Conserva el visor incremental:
- sólo un frame anatómico al navegador;
- LOD sólo para visualización web;
- atlas original intacto;
- NPZ reutilizable sin recalcular los 75 frames.

## Limitación metodológica
Es una anatomía de atlas registrada a SKEL. No es geometría ósea individual del paciente
obtenida mediante CT/MRI.
