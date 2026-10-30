"""Kontrola pozytywna skanera oraz nienaruszenia pomiaru 1 przed każdym push."""
import sys,json,subprocess,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from scan_public import scan
baseline='d7b8429'
old=subprocess.check_output(['git','ls-tree','-r','--name-only',baseline],cwd=ROOT,text=True).splitlines()
changed=[p for p in old if subprocess.check_output(['git','show',baseline+':'+p],cwd=ROOT)!= (ROOT/p).read_bytes()]
probe=ROOT/'out'/'scanner-positive.txt';probe.parent.mkdir(exist_ok=True)
probe.write_text('gh'+'p_'+'A'*32)
positive=scan([probe]);probe.unlink()
files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
issues=scan([ROOT/p for p in set(files)])
result={'baseline':baseline,'protected_files':len(old),'changed_protected':changed,'positive_detected':bool(positive),'scanned':len(set(files)),'findings':issues}
print(json.dumps(result,ensure_ascii=False,indent=2))
if changed or issues or not positive:sys.exit(1)
