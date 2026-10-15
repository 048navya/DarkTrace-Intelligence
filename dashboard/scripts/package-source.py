"""Create a portable source archive without secrets, dependencies or Site identity."""
from pathlib import Path
import json
import zipfile
root=Path(__file__).resolve().parent.parent
folders=['app','lib','db','drizzle','components','hooks','scripts','build','vendor','public','tests','docs','types','services']
root_names=['package.json','pnpm-lock.yaml','pnpm-workspace.yaml','tsconfig.json','next.config.ts','vite.config.ts','drizzle.config.ts','postcss.config.mjs','components.json','eslint.config.mjs','README.md','.gitignore','.env.collector.example','.env.fabric.example','compose.services.yaml']
exclude={'node_modules','__pycache__','.venv','downloads','.git','.wrangler','.sites-runtime','secrets'}
files=[root/n for n in root_names if (root/n).is_file()]
for folder in folders:
 for p in (root/folder).rglob('*'):
  relative=p.relative_to(root)
  if p.is_file() and not any(x in exclude for x in relative.parts) and p.suffix not in {'.pyc','.tsbuildinfo'} and not p.name.startswith('.env'):
   files.append(p)
output=root/'public/downloads/darktrace-source.zip';output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(set(files)):
  z.write(p,'darktrace-intelligence/'+p.relative_to(root).as_posix())
 z.writestr('darktrace-intelligence/.openai/hosting.json',json.dumps({'d1':'DB','r2':None},indent=2)+'\n')
print(f'{output}: {len(files)+1} files, {output.stat().st_size} bytes')
