"""Build a clean GitHub source release; no installed dependencies or private data."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT.parent/'DarkTrace_Integrated_GitHub_Ready.zip'
excluded={'.git','node_modules','.venv','venv','__pycache__','dist','.wrangler','.sites-runtime','.agents','.codex','outputs','artifacts','cache','secrets','downloads'}
allowed_env={'.env.example','.env.collector.example','.env.fabric.example','.dev.vars.example'}
files=[]
for p in ROOT.rglob('*'):
    relative=p.relative_to(ROOT)
    if not p.is_file() or p.is_symlink() or any(x in excluded for x in relative.parts):continue
    if p.name.startswith(('.env','.dev.vars')) and p.name not in allowed_env:continue
    if p.name=='safe_corpus.jsonl' or p.suffix in {'.zip','.pyc','.tsbuildinfo','.pem','.key','.sqlite','.db'}:continue
    files.append(p)
with zipfile.ZipFile(OUTPUT,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):z.write(p,'darktrace-github-ready/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUTPUT) as z:
    assert z.testzip() is None
    names=z.namelist()
    for required in ['README.md','docs/REQUIREMENTS.md','docs/COMPARISON.md','dashboard/app/repository-panel.tsx','darkweb-deanonymization/backend/app/routes/interop.py','.env.example','dashboard/.dev.vars.example']:
        assert 'darktrace-github-ready/'+required in names,required
    assert not any('/node_modules/' in n or '/.git/' in n or n.endswith('/.env') or n.endswith('/.dev.vars') for n in names)
    assert 'project_id' not in json.loads(z.read('darktrace-github-ready/dashboard/.openai/hosting.json'))
print(json.dumps({'file':str(OUTPUT),'files':len(files),'bytes':OUTPUT.stat().st_size,'sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}))
