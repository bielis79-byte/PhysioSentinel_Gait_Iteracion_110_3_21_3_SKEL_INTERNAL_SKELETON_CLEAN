from __future__ import annotations
from pathlib import Path
import json, xml.etree.ElementTree as ET
import numpy as np
import requests
HAMNER_MODEL_URL="https://raw.githubusercontent.com/opensim-org/opensim-models/master/Models/Hamner/FullBodyModel_Hamner2010_v2_0.osim"
HAMNER_GEOM_BASES=["https://raw.githubusercontent.com/opensim-org/opensim-models/master/Geometry","https://raw.githubusercontent.com/opensim-org/opensim-models/master/Models/Hamner/Geometry"]
CACHE_ROOT=Path("/tmp/physiosentinel_opensim_hamner_v3212")
BODY_MAP={
"pelvis":{"kind":"pelvis"},
"femur_r":{"kind":"long","a":"femur_r","b":"tibia_r"},"femur_l":{"kind":"long","a":"femur_l","b":"tibia_l"},
"tibia_r":{"kind":"long","a":"tibia_r","b":"talus_r"},"tibia_l":{"kind":"long","a":"tibia_l","b":"talus_l"},
"talus_r":{"kind":"block","a":"talus_r","b":"calcn_r"},"talus_l":{"kind":"block","a":"talus_l","b":"calcn_l"},
"calcn_r":{"kind":"foot","a":"calcn_r","b":"toes_r"},"calcn_l":{"kind":"foot","a":"calcn_l","b":"toes_l"},
"toes_r":{"kind":"foot","a":"calcn_r","b":"toes_r","distal":True},"toes_l":{"kind":"foot","a":"calcn_l","b":"toes_l","distal":True},
"torso":{"kind":"torso"},
"humerus_r":{"kind":"long","a":"humerus_r","b":"ulna_r"},"humerus_l":{"kind":"long","a":"humerus_l","b":"ulna_l"},
"ulna_r":{"kind":"long","a":"ulna_r","b":"hand_r"},"ulna_l":{"kind":"long","a":"ulna_l","b":"hand_l"},
"radius_r":{"kind":"long","a":"radius_r","b":"hand_r"},"radius_l":{"kind":"long","a":"radius_l","b":"hand_l"},
"hand_r":{"kind":"hand","a":"radius_r","b":"hand_r"},"hand_l":{"kind":"hand","a":"radius_l","b":"hand_l"}}
def _strip_ns(root):
    for e in root.iter():
        if '}' in e.tag: e.tag=e.tag.split('}',1)[1]
    return root
def _get(url,dst,timeout=45):
    dst=Path(dst); dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists() and dst.stat().st_size>32:return 'cached'
    r=requests.get(url,timeout=timeout); r.raise_for_status(); dst.write_bytes(r.content); return 'downloaded'
def _get_geom(fn,dst,force=False):
    dst=Path(dst)
    if force and dst.exists(): dst.unlink()
    if dst.exists() and dst.stat().st_size>32:return 'cached',None
    errs=[]
    for base in HAMNER_GEOM_BASES:
        try:return _get(f"{base}/{fn}",dst),base
        except Exception as e:
            errs.append(f"{base}: {type(e).__name__}: {e}")
            if dst.exists():
                try:dst.unlink()
                except:pass
    raise RuntimeError(' | '.join(errs))
def _parse_model(path):
    root=_strip_ns(ET.parse(path).getroot()); model=root.find('.//Model')
    meta={'model_name':model.attrib.get('name','3DGaitModelwithSimpleArms') if model is not None else '', 'bodies':{}, 'mesh_files':[]}
    for body in root.findall('.//BodySet/objects/Body'):
        bn=body.attrib.get('name',''); meshes=[]
        for mesh in body.findall('./attached_geometry/Mesh'):
            mf=mesh.find('mesh_file'); sf=mesh.find('scale_factors')
            if mf is None or not (mf.text or '').strip():continue
            fn=(mf.text or '').strip(); sc=[1.,1.,1.]
            if sf is not None and (sf.text or '').strip():
                try:sc=[float(x) for x in sf.text.split()[:3]]
                except:pass
            meshes.append({'file':fn,'scale':sc}); meta['mesh_files'].append(fn)
        meta['bodies'][bn]={'meshes':meshes}
    meta['mesh_files']=sorted(set(meta['mesh_files'])); return meta
def prepare_hamner(force=False):
    root=CACHE_ROOT; root.mkdir(parents=True,exist_ok=True); mp=root/'FullBodyModel_Hamner2010_v2_0.osim'
    if force and mp.exists():mp.unlink()
    try:_get(HAMNER_MODEL_URL,mp); meta=_parse_model(mp)
    except Exception as e:return {'ok':False,'error':f'{type(e).__name__}: {e}','root':str(root)}
    gdir=root/'Geometry'; gdir.mkdir(exist_ok=True); downloaded=cached=failed=0; errs=[]
    for fn in meta['mesh_files']:
        try:
            st,_=_get_geom(fn,gdir/fn,force=force); downloaded+=st=='downloaded'; cached+=st=='cached'
        except Exception as e:failed+=1; errs.append(f'{fn}: {type(e).__name__}: {e}')
    man={'meta':meta,'downloaded':downloaded,'cached':cached,'failed':failed,'errors':errs}
    (root/'manifest.json').write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'ok':True,'root':str(root),'model':meta['model_name'],'mesh_count':len(meta['mesh_files']),'downloaded':downloaded,'cached':cached,'failed':failed,'errors':errs}
def hamner_status():
    mp=CACHE_ROOT/'manifest.json'
    if not mp.exists():return {'ready':False,'root':str(CACHE_ROOT)}
    try:
        man=json.loads(mp.read_text(encoding='utf-8')); files=man.get('meta',{}).get('mesh_files',[])
        present=sum((CACHE_ROOT/'Geometry'/f).exists() for f in files)
        return {'ready':present>0,'root':str(CACHE_ROOT),'present':present,'mesh_count':len(files),'model':man.get('meta',{}).get('model_name','')}
    except:return {'ready':False,'root':str(CACHE_ROOT)}
def _parse_vtp_ascii(path):
    try:root=_strip_ns(ET.parse(path).getroot())
    except:return np.empty((0,3),np.float32),np.empty((0,3),np.int32)
    piece=root.find('.//Piece')
    if piece is None:return np.empty((0,3),np.float32),np.empty((0,3),np.int32)
    da=piece.find('./Points/DataArray')
    if da is None or da.attrib.get('format','ascii').lower()!='ascii':return np.empty((0,3),np.float32),np.empty((0,3),np.int32)
    vals=np.fromstring(da.text or '',sep=' ',dtype=np.float32)
    if vals.size%3:return np.empty((0,3),np.float32),np.empty((0,3),np.int32)
    V=vals.reshape(-1,3); polys=piece.find('./Polys')
    if polys is None:return V,np.empty((0,3),np.int32)
    conn=offs=None
    for x in polys.findall('./DataArray'):
        nm=(x.attrib.get('Name','') or '').lower(); arr=np.fromstring(x.text or '',sep=' ',dtype=np.int64)
        if 'connect' in nm:conn=arr
        elif 'offset' in nm:offs=arr
    if conn is None or offs is None:return V,np.empty((0,3),np.int32)
    faces=[]; st=0
    for en in offs:
        poly=conn[st:int(en)]; st=int(en)
        if len(poly)==3:faces.append(poly.tolist())
        elif len(poly)>3:
            for k in range(1,len(poly)-1):faces.append([int(poly[0]),int(poly[k]),int(poly[k+1])])
    return V,np.asarray(faces,dtype=np.int32)
def load_hamner_bodies():
    st=hamner_status()
    if not st.get('ready'):return {'bodies':{},'unsupported':[]}
    man=json.loads((CACHE_ROOT/'manifest.json').read_text(encoding='utf-8')); out={}; unsupported=[]
    for body,bmeta in man.get('meta',{}).get('bodies',{}).items():
        if body not in BODY_MAP:continue
        VV=[];FF=[];off=0
        for mm in bmeta.get('meshes',[]):
            V,F=_parse_vtp_ascii(CACHE_ROOT/'Geometry'/mm['file'])
            if V.size==0 or F.size==0:unsupported.append(mm['file']);continue
            V=(V*np.asarray(mm.get('scale',[1,1,1]),np.float32)).astype(np.float32); VV.append(V);FF.append(F+off);off+=len(V)
        if VV:out[body]={'V':np.vstack(VV).astype(np.float32),'F':np.vstack(FF).astype(np.int32),**BODY_MAP[body]}
    return {'bodies':out,'unsupported':unsupported}
def _frame(a,b,lr):
    z=np.asarray(b,float)-np.asarray(a,float); z=z/max(np.linalg.norm(z),1e-9); x=np.asarray(lr,float)-np.dot(lr,z)*z
    if np.linalg.norm(x)<1e-6:x=np.array([0.,0.,1.])-np.dot(np.array([0.,0.,1.]),z)*z
    x=x/max(np.linalg.norm(x),1e-9); y=np.cross(z,x); y=y/max(np.linalg.norm(y),1e-9); return x,y,z
def build_hamner_fullbody_frame(bodies,joints,joint_names,frame=0):
    J=np.asarray(joints,np.float32); nm={str(n):i for i,n in enumerate(joint_names)}; parts=[]
    hipr=nm.get('femur_r');hipl=nm.get('femur_l');lr=(J[frame,hipr]-J[frame,hipl]) if hipr is not None and hipl is not None else np.array([1.,0.,0.]);lr=lr/max(np.linalg.norm(lr),1e-9)
    for body,p in bodies.items():
        V=np.asarray(p['V'],np.float32);F=np.asarray(p['F'],np.int32);kind=p['kind']
        if kind=='pelvis':
            pel=nm.get('pelvis');lum=nm.get('lumbar_body');th=nm.get('thorax')
            if pel is None or hipr is None or hipl is None:continue
            width=float(np.linalg.norm(J[0,hipr]-J[0,hipl])); span=max(float(np.ptp(V[:,2])),float(np.ptp(V[:,0])),1e-6); scale=np.clip((width*1.35)/span,.35,3.)
            X=(V-np.mean(V,axis=0))*scale; up=(J[frame,lum]-J[frame,pel]) if lum is not None else (J[frame,th]-J[frame,pel] if th is not None else np.array([0,1,0]));up=up/max(np.linalg.norm(up),1e-9);ap=np.cross(lr,up);ap=ap/max(np.linalg.norm(ap),1e-9)
            W=J[frame,pel]+X[:,0,None]*ap+X[:,1,None]*up+X[:,2,None]*lr
        elif kind=='torso':
            th=nm.get('thorax');lum=nm.get('lumbar_body');head=nm.get('head')
            if th is None:continue
            lo=J[frame,lum] if lum is not None else J[frame,th];hi=J[frame,head] if head is not None else J[frame,th]+np.array([0,.5,0]);target=max(float(np.linalg.norm(hi-lo)),.2);yspan=max(float(np.ptp(V[:,1])),1e-6);scale=np.clip(target/yspan,.35,3.);X=(V-np.mean(V,axis=0))*scale;up=hi-lo;up=up/max(np.linalg.norm(up),1e-9);ap=np.cross(lr,up);ap=ap/max(np.linalg.norm(ap),1e-9);W=.5*(lo+hi)+X[:,0,None]*ap+X[:,1,None]*up+X[:,2,None]*lr
        elif kind=='long':
            ai=nm.get(p['a']);bi=nm.get(p['b'])
            if ai is None or bi is None:continue
            a0,b0=J[0,ai],J[0,bi];at,bt=J[frame,ai],J[frame,bi];L=max(float(np.linalg.norm(b0-a0)),1e-6);scale=L/max(float(np.ptp(V[:,1])),1e-6);X=V*scale;longitudinal=float(X[:,1].max())-X[:,1];tx=X[:,0]-np.median(X[:,0]);tz=X[:,2]-np.median(X[:,2]);x,y,z=_frame(at,bt,lr);W=at+longitudinal[:,None]*z+tx[:,None]*x+tz[:,None]*y
        else:
            ai=nm.get(p['a']);bi=nm.get(p['b'])
            if ai is None or bi is None:continue
            a0,b0=J[0,ai],J[0,bi];at,bt=J[frame,ai],J[frame,bi];L=max(float(np.linalg.norm(b0-a0)),.06);Xc=V-np.mean(V,axis=0);_,_,vt=np.linalg.svd(Xc,full_matrices=False);B=vt.T;proj=Xc@B[:,0];scale=np.clip(L/max(float(np.ptp(proj)),1e-6),.35,3.);local=(Xc*scale)@B;x,y,z=_frame(at,bt,lr);center=bt if p.get('distal') or kind=='hand' else .5*(at+bt);W=center+local[:,0,None]*z+local[:,1,None]*x+local[:,2,None]*y
        parts.append({'id':body,'body':body,'V':np.asarray(W,np.float32),'F':F})
    return parts
