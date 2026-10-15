"""Authenticated bridge: preserve repository provenance; never invent identity evidence."""
import hashlib
import json
from datetime import date, datetime, timezone
from typing import Literal
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.crud import fetch_all, fetch_one, execute_query
router=APIRouter(prefix='/interop',tags=['Dashboard bridge'])

def normalize_post(row):
    observed=row.get('created_at')
    if observed is None: return None
    if isinstance(observed,str): observed=datetime.fromisoformat(observed.replace('Z','+00:00'))
    if isinstance(observed,date) and not isinstance(observed,datetime): observed=datetime.combine(observed,datetime.min.time())
    assumed=observed.tzinfo is None
    if assumed: observed=observed.replace(tzinfo=timezone.utc)
    source=row.get('source') or 'Unspecified repository source'
    category=row.get('category') or 'Other'
    supported={'Data exposure','Account trading','Malware discussion','Infrastructure','Other'}
    provenance=f"\n\nRepository post: {row['post_id']} | Source: {source} | Original category: {category}."
    if assumed: provenance+=' Source timezone absent; UTC assumed by bridge.'
    raw=row.get('content') or ''
    if len(raw)>11000: provenance+=' Text truncated to 11,000 characters; original retained in PostgreSQL.'
    return {'id':'repo-post-'+hashlib.sha256(str(row['post_id']).encode()).hexdigest()[:32],
      'handle':str(row.get('username') or ('unknown-post-'+str(row['post_id'])))[:100],
      'platform':str(row.get('platform_name') or row.get('forum_name') or 'Repository source')[:100],
      'category':category if category in supported else 'Other',
      'observedAt':observed.astimezone(timezone.utc).isoformat().replace('+00:00','Z'),
      'text':raw[:11000]+provenance[:900], 'wallets':[], 'pgp':[], 'trusts':[], 'service':'', 'indicators':[], 'entityLead':'',
      'synthetic':'synthetic' in source.lower()}

@router.get('/snapshot')
def snapshot(offset:int=Query(0,ge=0),limit:int=Query(50,ge=1,le=100),q:str=Query('',max_length=200),date_from:date|None=None,date_to:date|None=None):
    if date_from and date_to and date_from>date_to: raise HTTPException(422,'date_from must precede date_to')
    where='WHERE (%s=\'\' OR p.content ILIKE %s OR COALESCE(h.username,\'\') ILIKE %s) AND (%s::date IS NULL OR p.created_at::date >= %s::date) AND (%s::date IS NULL OR p.created_at::date <= %s::date)'
    params=(q,'%'+q+'%','%'+q+'%',date_from,date_from,date_to,date_to)
    rows=fetch_all('''SELECT p.post_id,p.content,p.created_at,p.source,h.username,pl.name AS platform_name,t.category,t.forum_name
      FROM posts p LEFT JOIN handles h ON h.handle_id=p.handle_id LEFT JOIN platforms pl ON pl.platform_id=h.platform_id LEFT JOIN threads t ON t.thread_id=p.thread_id '''+where+' ORDER BY p.post_id LIMIT %s OFFSET %s',params+(limit,offset))
    total=fetch_one('SELECT count(*) AS total FROM posts p LEFT JOIN handles h ON h.handle_id=p.handle_id '+where,params)['total']
    records=[r for row in rows if (r:=normalize_post(row)) is not None]
    return {'records':records,'total':total,'offset':offset,'nextOffset':offset+limit if offset+limit<total else None,
      'skippedMissingDate':len(rows)-len(records),'note':'Explicit snapshot, not live database synchronization. Unknown dates are skipped. Actor-level wallet assignments and cluster labels are not copied as independently observed identity evidence.'}

class Review(BaseModel):
    relationship_id:int=Field(gt=0)
    decision:Literal['accepted','rejected','pending']
    reason:str=Field(min_length=8,max_length=1500)

@router.post('/reviews')
def save_review(body:Review):
    if not fetch_one('SELECT relationship_id FROM persona_relationships WHERE relationship_id=%s',(body.relationship_id,)):
        raise HTTPException(404,'Relationship not found')
    if len(body.reason.strip())<8: raise HTTPException(422,'A meaningful review reason is required')
    execute_query('INSERT INTO repository_reviews(relationship_id,decision,reason) VALUES(%s,%s,%s)',(body.relationship_id,body.decision,body.reason.strip()))
    return {'saved':True}

@router.get('/reviews')
def reviews():return {'reviews':fetch_all('SELECT * FROM repository_reviews ORDER BY created_at DESC LIMIT 100')}
