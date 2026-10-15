'use client';
import {useMemo,useState,useId} from 'react';
import {Network,Minus,Plus,RotateCcw} from 'lucide-react';
import {Button} from '@/components/ui/button';
import type {IntelRecord} from '@/lib/engine';

export default function Graph({records,links,onRecord,onLink}:{records:IntelRecord[];links:any[];onRecord:(r:IntelRecord)=>void;onLink:(l:any)=>void}) {
  const [hover,setHover]=useState<string|null>(null),[zoom,setZoom]=useState(1);
  const pattern=useId().replace(/:/g,'');
  const layout=useMemo(()=>{
    const degree=new Map<string,number>();
    links.forEach(l=>{degree.set(l.a,(degree.get(l.a)||0)+1);degree.set(l.b,(degree.get(l.b)||0)+1)});
    const nodes=[...records].sort((a,b)=>(degree.get(b.id)||0)-(degree.get(a.id)||0)||a.id.localeCompare(b.id)).slice(0,24);
    const visible=new Set(nodes.map(r=>r.id));
    const edges=links.filter(l=>visible.has(l.a)&&visible.has(l.b));
    const remaining=new Set(visible),groups:IntelRecord[][]=[],isolated:IntelRecord[]=[];
    for(const r of nodes){
      if(!remaining.has(r.id))continue;
      const ids=[r.id];remaining.delete(r.id);
      for(let i=0;i<ids.length;i++)for(const l of edges){
        if(l.type==='Reported trust')continue;
        const other=l.a===ids[i]?l.b:l.b===ids[i]?l.a:null;
        if(other&&remaining.has(other)){remaining.delete(other);ids.push(other)}
      }
      const cluster=ids.map(id=>nodes.find(n=>n.id===id)!);
      if(cluster.length===1)isolated.push(...cluster);else for(let i=0;i<cluster.length;i+=4)groups.push(cluster.slice(i,i+4));
    }
    for(let i=0;i<isolated.length;i+=4)groups.push(isolated.slice(i,i+4));
    const columns=groups.length===1?1:2,width=840,height=Math.max(320,Math.ceil(groups.length/columns)*290+30);
    const positions=groups.flatMap((group,gi)=>group.map((r,i)=>{
      const cx=(gi%columns+.5)*(width/columns),cy=Math.floor(gi/columns)*290+135;
      const positions=group.length===1?[[0,0]]:group.length===2?[[-85,0],[85,0]]:group.length===3?[[0,-45],[-85,60],[85,60]]:[[-85,-42],[85,-42],[-85,70],[85,70]];
      return {r,x:cx+positions[i][0],y:cy+positions[i][1],group:gi};
    }));
    return {nodes,edges,groups,positions,width,height,columns,degree};
  },[records,links]);
  const connected=new Set([hover,...layout.edges.filter(l=>l.a===hover||l.b===hover).flatMap(l=>[l.a,l.b])]);
  if(!records.length)return <div className="graph-empty"><Network size={36}/><strong>No accounts in this view</strong><p>Adjust your filters to explore the evidence.</p></div>;
  return <div className="graph-surface"><div className="graph-toolbar"><span><span className="status-dot"/>{layout.nodes.length} of {records.length} accounts · {layout.edges.length} visible links</span><div><Button variant="ghost" size="icon" aria-label="Zoom out" disabled={zoom<=1} onClick={()=>setZoom(Math.max(1,zoom-.25))}><Minus size={15}/></Button><span>{Math.round(zoom*100)}%</span><Button variant="ghost" size="icon" aria-label="Zoom in" disabled={zoom>=2} onClick={()=>setZoom(Math.min(2,zoom+.25))}><Plus size={15}/></Button><Button variant="ghost" size="icon" aria-label="Reset graph zoom" onClick={()=>setZoom(1)}><RotateCcw size={14}/></Button></div></div><div className="graph-scroll"><svg className="network-map" style={{width:`${zoom*100}%`,minWidth:660*zoom}} viewBox={`0 0 ${layout.width} ${layout.height}`} role="group" aria-label="Evidence relationship graph. Accounts grouped by shared identifiers, not confirmed identity."><defs><pattern id={pattern} width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="#cddde4"/></pattern></defs><rect width="100%" height="100%" fill={`url(#${pattern})`}/>{layout.groups.map((g,i)=><g key={i}><rect x={i%layout.columns*(840/layout.columns)+15} y={Math.floor(i/layout.columns)*290+14} width={840/layout.columns-30} height="266" rx="16" fill={i%2?'#f0f5fb':'#edf8f7'} fillOpacity=".85" stroke="#d9e7ed" strokeDasharray="4 5"/><text x={i%layout.columns*(840/layout.columns)+32} y={Math.floor(i/layout.columns)*290+39} fontSize="10" letterSpacing="1.4" fill="#728b99">{g.some(r=>layout.edges.some(l=>l.type!=='Reported trust'&&(l.a===r.id||l.b===r.id)))?'IDENTIFIER GROUP':'OTHER ACCOUNTS'} · {String(i+1).padStart(2,'0')}</text></g>)}{layout.edges.map(l=>{
    const a=layout.positions.find(p=>p.r.id===l.a)!,b=layout.positions.find(p=>p.r.id===l.b)!;
    const active=!hover||l.a===hover||l.b===hover,trust=l.type==='Reported trust';
    return <g key={l.id} className="graph-edge" role="button" tabIndex={0} opacity={active?1:.13} aria-label={`Review ${l.type}: ${a.r.handle} and ${b.r.handle}`} onClick={()=>onLink(l)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();onLink(l)}}}><title>{l.type} · {l.confidence} confidence</title><line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="transparent" strokeWidth="16"/><line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={trust?'#9aacc0':'#36a99e'} strokeWidth={hover?2.5:1.8} strokeDasharray={trust?'5 6':undefined}/></g>;
  })}{layout.positions.map(({r,x,y,group})=><g key={r.id} role="button" tabIndex={0} className="graph-node" opacity={!hover||connected.has(r.id)?1:.25} aria-label={`Open ${r.handle}, ${r.platform}, ${layout.degree.get(r.id)||0} connections`} onMouseEnter={()=>setHover(r.id)} onMouseLeave={()=>setHover(null)} onFocus={()=>setHover(r.id)} onBlur={()=>setHover(null)} onClick={()=>onRecord(r)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();onRecord(r)}}}><title>{r.handle} · {r.platform}{r.synthetic?' · Synthetic record':''}</title><circle cx={x} cy={y} r="30" fill="white" stroke={group%2?'#9baacb':'#8ccdc5'} strokeWidth="1.5"/><circle cx={x} cy={y} r="24" fill={group%2?'#e4eaf7':'#dff3ed'}/><text x={x} y={y+5} textAnchor="middle" fill={group%2?'#586b93':'#24796d'} fontSize="14" fontWeight="700">{r.handle.slice(0,2).toUpperCase()}</text><rect x={x-76} y={y+36} width="152" height="38" rx="6" fill="white"/><text x={x} y={y+51} textAnchor="middle" fill="#254659" fontSize="12" fontWeight="600">{r.handle.length>21?r.handle.slice(0,19)+'…':r.handle}</text><text x={x} y={y+66} textAnchor="middle" fill="#8295a3" fontSize="10">{r.platform.length>23?r.platform.slice(0,21)+'…':r.platform}{r.synthetic?' · DEMO':''}</text></g>)}</svg></div><div className="graph-caption"><span>Hover to trace a connection. Select to inspect evidence.</span><span>{records.length>24?'24 most connected accounts shown. Narrow filters for others.':'Grouping indicates shared evidence, not proven identity.'}</span></div></div>;
}
