"""Odbiór liczb względem zachowanych artefaktów, nie koloru workflow."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
datasets=load(ROOT/'results/summary.json')
expected={(p,v) for p in ['android','ios','macos','catalyst'] for v in ['GRUPY','PLASKI']}
assert {(d['platform'],d['variant']) for d in datasets}==expected
assert len(datasets)==len(expected)
checks=[]
required={'imie','nazw','kraj','szt','faktura','news','lista','zapisz','anuluj','komunikat','plik','sposob_0','sposob_1','sposob_2'}
targets=['nazw','kraj','szt','faktura','zapisz']
for d in datasets:
 p=ROOT/d['source']['path'];raw=load(p)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==d['source']['sha256']
 assert raw==load(ROOT/f"results/{d['platform']}-{d['variant']}.json")
 assert d['source']['url']==f"https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/{d['source']['run']}"
 for s in d['stops']:assert s['words']==len(s['text'].split())
 if d['platform'] in ['android','macos']:
  assert required.issubset({s['id'] for s in d['stops']})
  assert d['stops'][0]['id']=='imie'
  assert d['summary']['task']['complete']
  position=0;wc=0;positions=[]
  for target in targets:
   next_position=next(i for i in range(position+1,len(d['stops'])) if d['stops'][i]['id']==target)
   wc+=sum(len(s['text'].split()) for s in d['stops'][position+1:next_position+1])
   positions.append(next_position);position=next_position
  assert position==d['summary']['task']['steps']
  assert wc==d['summary']['task']['words']
  assert sum(x['steps'] for x in d['summary']['task']['legs'])==position
  assert sum(x['words'] for x in d['summary']['task']['legs'])==wc
  assert positions==[x['to'] for x in d['summary']['task']['legs']]
  if d['platform']=='android':assert raw['tts_positive'] and raw['reader_positive']
  else:assert raw['positive']
 elif d['platform']=='ios':
  assert required.issubset({s['id'] for s in d['stops']})
  assert len(d['stops'])==len({s['id'] for s in d['stops']})
  positions={s['id']:i for i,s in enumerate(d['stops'])}
  at=positions['imie'];steps=wc=0
  for target in targets:
   end=positions[target];direction=1 if end>at else -1
   wc+=sum(len(d['stops'][i]['text'].split()) for i in range(at+direction,end+direction,direction))
   steps+=abs(end-at);at=end
  assert d['bidirectional_model']['steps']==steps and d['bidirectional_model']['words']==wc
  assert d['evidence']=='accessibility_tree_NOT_speech'
 checks.append({'platform':d['platform'],'variant':d['variant'],'source_hash':True,'json_equal':True,'counts':True})
runs=load(ROOT/'wyniki/runs.json')
assert len(runs)<=25 and all(r['status']=='completed' for r in runs)
assert len({r['databaseId'] for r in runs})==len(runs)
for r in runs:assert any((ROOT/'wyniki').glob(f"*/{r['databaseId']}/workflow.log"))
report=(ROOT/'WYNIK.md').read_bytes()
assert report==(ROOT.parent/'RAPORT.md').read_bytes()
for d in datasets:assert d['source']['run'].encode() in report
assert b'/home/' not in report
assert 'MIT License' in (ROOT/'LICENSE').read_text()
assert (ROOT/'README.md').exists()
result={'datasets':checks,'workflow_count':len(runs),'complete_downloads':True,'report_identical':True,'report_sha256':hashlib.sha256(report).hexdigest(),'passed':True}
(ROOT/'results/verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
