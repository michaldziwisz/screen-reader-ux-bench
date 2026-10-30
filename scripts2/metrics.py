"""Rachunki wyłącznie na dostarczonych śladach, bez wnioskowania mowy z drzewa."""
import re

def word_stats(phrases,name):
 text=' '.join(phrases)
 pos=text.find(name)
 return {'text':text,'words':len(text.split()),'name_word':len(text[:pos].split())+1 if pos>=0 else None}

def messages(phrases):
 return sorted({int(n) for n in re.findall(r'\bPlik\s+([1-5])\s+z\s+5\b',' '.join(phrases),re.I)})

def walk(tree):
 if not isinstance(tree,dict):return
 yield tree
 for child in tree.get('children',[]):yield from walk(child)

def bursts(result):
 groups={}
 for s in result['steps']:
  if not s['kind'].startswith('burst:'):continue
  _,mode,rep=s['kind'].split(':')
  groups.setdefault(mode,[]).append({'repeat':int(rep),'received':messages(s['phrases']),'phrases':s['phrases']})
 for rows in groups.values():rows.sort(key=lambda x:x['repeat'])
 return groups

def android_state(step):
 rows=[x['payload']['data'] for x in step.get('records',[]) if x['tag']=='UX_APP' and isinstance(x['payload'],dict) and x['payload'].get('kind')=='state']
 return rows[-1] if rows else {}

def android_focus(step):
 return [x['payload'].get('node',{}) for x in step.get('records',[]) if x['tag']=='UX_AX' and isinstance(x['payload'],dict) and x['payload'].get('event')==32768]

def route(result,kind,target,platform):
 rows=[s for s in result['steps'] if s['kind']==kind]
 for i,s in enumerate(rows,1):
  focus=android_state(s).get('focusId') if platform=='android' else s.get('after',{}).get('focus',{}).get('AXIdentifier')
  if focus==target:return {'steps':i,'reached':True,'words':sum(x['words'] for x in rows[:i])}
 return {'steps':None,'reached':False,'attempts':len(rows)}
