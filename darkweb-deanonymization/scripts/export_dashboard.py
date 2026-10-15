"""Export a paginated repository snapshot as dashboard import JSON files."""
import argparse,json,os,urllib.request
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2]/'.env')
p=argparse.ArgumentParser();p.add_argument('--api',default='http://127.0.0.1:8000');p.add_argument('--output',default='outputs/repository-snapshot');args=p.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True);offset=0;page=1
while True:
    req=urllib.request.Request(args.api.rstrip('/')+f'/interop/snapshot?offset={offset}&limit=50',headers={'x-api-key':os.environ['DARKTRACE_API_KEY']})
    with urllib.request.urlopen(req,timeout=30) as response:result=json.load(response)
    path=out/f'page-{page:03}.json';path.write_text(json.dumps(result['records'],indent=2),encoding='utf-8')
    print(f'{path}: {len(result["records"])} records; {result["skippedMissingDate"]} missing-date rows skipped')
    if result['nextOffset'] is None:break
    offset=result['nextOffset'];page+=1
