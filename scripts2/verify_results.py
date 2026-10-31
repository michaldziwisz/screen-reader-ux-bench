"""Weryfikuj pochodzenie, kontrole, pełność serii i liczby publikowanego pomiaru 2."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from metrics import word_stats,messages,walk,bursts,route,android_table_exit
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results2'
def load(name):return json.loads((OUT/name).read_text())
def run():
 manifest=load('manifest.json');summary={}
 for spec in manifest:
  p=OUT/spec['target'];assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['projection_sha256']
  d=json.loads(p.read_text());key=spec['target'];m={'run_url':spec['run_url']}
  if spec['platform'] in ['android','macos']:
   assert d.get('error') is None,(key,d.get('error'))
   if spec['platform']=='android':assert d['reader_positive']
   else:assert d['positive'] and any('Szukaj' in x for x in d['rawCaptureControl']['phrases'])
   if d.get('presentation') not in ['EXTRA','TABLE','READONLY']:
    if spec['platform']=='android':assert d['tts_positive'] and d['reader_positive_after']
    groups=bursts(d);expected={'plain','polite','assertive','toast','snackbar'} if spec['platform']=='android' else {'plain','low','medium','high'}
    if d.get('presentation')=='TOAST':expected={'toast'}
    assert set(groups)==expected
    for mode,rows in groups.items():
     assert [r['repeat'] for r in rows]==list(range(1,7)),(key,mode)
     for s in [x for x in d['steps'] if x['kind'].startswith('burst:'+mode+':')]:
      ev=[x['payload'] for x in s['evidence_records'] if x['tag']=='UX_APP'] if spec['platform']=='android' else s['app']['new_events']
      ev=[x for x in ev if x.get('kind')=='emit']
      assert len(ev)==5 and messages([x['data']['text'] for x in ev])==[1,2,3,4,5],(key,s['kind'],'emitted')
    excluded=spec.get('exclude_burst_modes',[])
    m['excluded_burst_modes']=excluded
    m['bursts']={k:[r['received'] for r in rows] for k,rows in groups.items() if k not in excluded}
   if d.get('presentation') not in ['EXTRA','TOAST','READONLY']:
    m['search_route']=route(d,'details-to-search:Tab','search',spec['platform'])
    m['table_exit']=route(d,'table-exit:Tab','after_files' if spec['platform']=='android' else 'details',spec['platform'])
    if spec['platform']=='android':
     m['table_exit']=android_table_exit(d)
     assert m['table_exit']['reached'],(key,'table route not established')
    step=next((s for s in d['steps'] if s['kind']==('focus:row_1' if spec['platform']=='android' else 'table:ArrowDown')),None)
    if step:
     m['record_primary']=word_stats(step['phrases'][:1],'Faktura marzec');m['record_window']=word_stats(step['phrases'],'Faktura marzec')
     assert m['record_primary']['name_word'] is not None,(key,'record not spoken')
   if d.get('presentation')=='READONLY':
    assert d['tts_positive'] and d['reader_positive_after']
    tree=next(s for s in d['steps'] if s['kind']=='readonly:tree')
    node=next(x['payload'] for x in tree['evidence_records'] if x['tag']=='UX_TREE' and x['payload']['id'].endswith(':id/details'))
    assert node['editable'] is False and node['role']=='android.widget.TextView'
    step=next(s for s in d['steps'] if s['kind']=='readonly:SET_TEXT')
    action=next(x['payload'] for x in step['evidence_records'] if x['tag']=='UX_ACTION' and isinstance(x['payload'],dict) and x['payload'].get('action')==2097152)
    assert action['ok'] is False
    expected=json.loads((ROOT/'shared2/fixture.json').read_text())['details']
    assert all(s['state']['detailsText']==expected for s in d['steps'])
    m['readonly']={'editable':node['editable'],'role':node['role'],'set_text_allowed':action['ok'],'unchanged':True}
   if spec['platform']=='macos':
    m['paced_control']=next(s['phrases'] for s in d['steps'] if s['kind']=='positive-paced-announcements')
    assert {int(x) for x in re.findall(r'Kontrola (\d) z 5',' '.join(m['paced_control']))}=={1,2,3,4,5},(key,'paced control')
  elif spec['platform']=='ios':
   if 'bursts' in d:
    assert 'unavailable' in d['reader']
    assert len(d['bursts'])==6
    m['record_label']=word_stats([next(x['label'] for x in walk(d['initial']) if x['id']=='row_1')],'Faktura marzec')
    ids={x['id'] for stage in ['initial','files_scrolled'] for x in walk(d[stage]) if x['id'].startswith('row_')};assert len(ids)==20
    m['unique_records']=len(ids)
    m['outline_by_stage']={stage:sorted({x['id'] for x in walk(d[stage]) if x['id'].startswith('folder_')}) for stage in ['initial','expanded_Dokumenty','expanded_Umowy']}
   else:
    assert next(x for x in d['events'] if x['kind']=='ready')['data']['voiceOverRunning'] is False
    m['emission_count']=sum(x['kind']=='emit' for x in d['events']);assert m['emission_count']==32
    m['header_count']=sum(bool(x['header']) for x in walk(d['semantics']));assert m['header_count']==4
  summary[key]=m
 return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
 result=run();content=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
 if args.write:(OUT/'summary.json').write_text(content)
 else:assert load('summary.json')==result,'summary differs'
 print(json.dumps({'status':'PASS','verified_sources':len(result),'summary':'results2/summary.json'}))
