"""Pobierz wszystkie zakończone przebiegi wyłącznie kampanii 2, limit 30."""
import json,subprocess
from pathlib import Path
repo='michaldziwisz/screen-reader-ux-bench'
def gh(*a):return subprocess.check_output(['gh',*a],text=True)
runs=[]
for workflow in ['macos2.yml','android2.yml','ios2.yml']:
 for r in json.loads(gh('run','list','-R',repo,'--workflow',workflow,'--limit','100','--json','databaseId,status,conclusion,url,headSha,createdAt')):r['workflow']=workflow;runs.append(r)
assert len(runs)<=30, 'Budget exceeded'
root=Path('wyniki/campaign2');root.mkdir(parents=True,exist_ok=True)
(root/'runs.json').write_text(json.dumps(runs,indent=2))
for r in runs:
 if r['status']!='completed':continue
 dest=root/str(r['databaseId']);dest.mkdir(exist_ok=True)
 if not (dest/'downloaded.json').exists():
  p=subprocess.run(['gh','run','download',str(r['databaseId']),'-R',repo,'-D',str(dest)],text=True,capture_output=True)
  (dest/'download-result.txt').write_text(p.stdout+p.stderr)
  if p.returncode==0:(dest/'downloaded.json').write_text(json.dumps(r,indent=2))
  (dest/'workflow.log').write_text(gh('run','view',str(r['databaseId']),'-R',repo,'--log'))
print(json.dumps(runs,indent=2))
