"""Zmniejsz ślady przez usunięcie powtórzeń, zachowując dowody i pochodzenie."""
import argparse,copy,hashlib,json,statistics
from pathlib import Path
from metrics import android_state,android_focus
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results2'

def project(data,platform):
 d=copy.deepcopy(data)
 if platform=='macos':
  previous=0
  for s in d['steps']:
   events=s['app'].pop('events',[])
   s['app']['new_events']=events[previous:];previous=len(events)
   capture=s.get('captureResult')
   if capture and 'samples' in capture:
    samples=capture.pop('samples');gaps=[b['ms']-a['ms'] for a,b in zip(samples,samples[1:])]
    changes=[];last=None
    for x in samples:
     value=x.get('text',x.get('error'))
     if value!=last:changes.append(x);last=value
    capture['sample_changes']=changes
    capture['sample_statistics']={'count':len(samples),'error_count':sum('error' in x for x in samples),'gap_median_ms':statistics.median(gaps) if gaps else None,'gap_max_ms':max(gaps) if gaps else None}
 elif platform=='android':
  for s in d['steps']:
   s['state']=android_state(s);s['accessibility_focus']=android_focus(s)
   records=s.pop('records')
   s['evidence_records']=[x for x in records if x['tag'] in ['UX_ACTION','UX_TREE','UX_TTS'] or (x['tag']=='UX_APP' and isinstance(x['payload'],dict) and x['payload'].get('kind')=='emit')]
 return d

def encode(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def digest(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');args=p.parse_args()
 specs=json.loads((OUT/'sources.json').read_text());manifest=[]
 for spec in specs:
  source=ROOT/spec['source'];raw=source.read_bytes()
  data=project(json.loads(raw),spec['platform']);output=encode(data)
  target=OUT/spec['target']
  if args.verify:
   assert target.read_bytes()==output,f'Projection differs: {target}'
  else:target.write_bytes(output)
  run=json.loads((ROOT/f"wyniki/campaign2/{spec['run']}/downloaded.json").read_text())
  assert run['status']=='completed' and run['conclusion']=='success'
  manifest.append({**spec,'head_sha':run['headSha'],'source_sha256':digest(raw),'projection_sha256':digest(output),'run_url':f"https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/{spec['run']}"})
 if args.verify:assert json.loads((OUT/'manifest.json').read_text())==manifest
 else:(OUT/'manifest.json').write_bytes(encode(manifest))
 print(json.dumps({'projections_verified':len(manifest),'raw_sources_verified':len(manifest),'status':'PASS'}))
if __name__=='__main__':main()
