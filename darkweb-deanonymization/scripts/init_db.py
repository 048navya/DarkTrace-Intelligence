"""Apply the baseline and additive migration without dropping data."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.database import get_connection

def initialize():
    conn=get_connection()
    try:
        with conn,conn.cursor() as cur:
            cur.execute((ROOT/'database/schema.sql').read_text())
            for p in sorted((ROOT/'database/migrations').glob('*.sql')): cur.execute(p.read_text())
    finally:conn.close()
if __name__=='__main__':initialize();print('Schema ready; existing data retained')
