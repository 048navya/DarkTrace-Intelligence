"""Load bundled CSV fixtures only; never download real intelligence."""
import csv, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.database import get_connection

def load():
    conn=get_connection()
    try:
        with conn, conn.cursor() as cur:
            for table in ('actors','platforms','handles','wallets','posts','evidence'):
                with (ROOT/'data'/f'{table}.csv').open(encoding='utf-8') as stream:
                    rows=list(csv.DictReader(stream))
                for row in rows:
                    if table=='actors': row['description']='Bundled fictional sample. Not a real-world identity claim.'
                    if table in ('platforms','handles','posts','evidence'): row['source']='Bundled synthetic CSV fixture'
                    if table=='posts': row['content_hash']=hashlib.sha256(row['content'].encode()).hexdigest()
                    if table=='evidence': row['evidence_type']='synthetic-observation'
                    columns=list(row); placeholders=','.join(['%s']*len(columns))
                    cur.execute(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",tuple(row.values()))
            for table,col in [('actors','actor_id'),('platforms','platform_id'),('handles','handle_id'),('wallets','wallet_id'),('evidence','evidence_id')]:
                cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}','{col}'), COALESCE(MAX({col}),1), COUNT(*)>0) FROM {table}")
        return {'loaded':True,'synthetic':True}
    finally: conn.close()
if __name__=='__main__': print(load())
