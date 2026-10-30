"""Wspólny sterownik Androida. Wejście uruchomieniowe dla CI jest niżej."""
import json, subprocess, time, re, os
from pathlib import Path
PKG='org.uxbench2'
TALKBACK='com.google.android.marvin.talkback/.TalkBackService'
OBSERVER=PKG+'/.Observer'
TAGS=['UX_TTS:I','UX_AX:I','UX_TREE:I','UX_APP:I','UX_ACTION:I','UXMARK:I','AndroidRuntime:E','*:S']
def parse(raw):
 records=[]
 for line in raw.splitlines():
  m=re.match(r'\s*([\d.]+)\s+\d+\s+\d+\s+\w\s+(UX_\w+|UXMARK)\s*: (.*)',line)
  if m:
   ts,tag,payload=m.groups()
   try:payload=json.loads(payload)
   except ValueError:pass
   records.append({'time':float(ts),'tag':tag,'payload':payload})
 return records
class Harness:
 def __init__(self,out,serial=None):self.out=Path(out);self.out.mkdir(parents=True,exist_ok=True);self.prefix=['adb']+(['-s',serial] if serial else []);self.seq=0;self.result={}
 def adb(self,*args,check=True,timeout=40):
  r=subprocess.run(self.prefix+list(args),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
  if check and r.returncode:raise RuntimeError(str(args)+': '+r.stdout)
  return r.stdout
 def shell(self,*args):return self.adb('shell',*args)
 def control(self,command,**kw):
  a=['am','broadcast','-n',PKG+'/.Control','--es','command',command]
  for k,v in kw.items():a += ['--ei' if isinstance(v,int) else '--es',k,str(v)]
  return self.shell(*a)
 def logs(self):return self.adb('logcat','-d','-v','epoch',*TAGS)
 def gate(self):
  text=self.shell('dumpsys','window')
  focused=[x for x in text.splitlines() if 'mCurrentFocus=' in x]
  if not any(PKG in x for x in focused):raise RuntimeError('Foreground gate: '+str(focused))
 def key(self,*keys):self.gate();return self.shell('input','keyevent',*keys)
 def combo(self,*keys):self.gate();return self.shell('input','keycombination',*keys)
 def save(self): (self.out/(self.result['variant']+'-'+self.result['presentation']+'.json')).write_text(json.dumps(self.result,ensure_ascii=False,indent=2))
 def step(self,kind,action,seconds=1.5):
  self.seq+=1;marker=f'{self.seq}:{kind}';self.shell('log','-t','UXMARK',marker)
  returned=action();time.sleep(seconds);self.control('state');time.sleep(.15)
  raw=self.logs();records=parse(raw);idx=next((i for i,x in enumerate(records) if x['tag']=='UXMARK' and x['payload']==marker),None)
  if idx is None:raise RuntimeError('Missing measurement marker')
  records=records[idx:]
  phrases=[x['payload']['text'] for x in records if x['tag']=='UX_TTS' and isinstance(x['payload'],dict)]
  e={'kind':kind,'phrases':phrases,'words':len(' '.join(phrases).split()),'records':records,'command_result':returned,'window_seconds':seconds}
  self.result['steps'].append(e);self.save();return e
 def focus(self,target):return self.step('focus:'+target,lambda:self.control('action',target=target,action=64))
 def measure(self,variant='NAZWA',presentation='RECYCLER',bursts=True):
  self.result={'variant':variant,'presentation':presentation,'evidence':'live_reader','steps':[],'error':None}
  try:
   self.shell('am','start','-f','0x10008000','-n',PKG+'/.MainActivity','--es','variant',variant,'--es','presentation',presentation);time.sleep(4)
   p=self.step('positive-tts',lambda:self.control('probe'),5);self.result['tts_positive']=any('Kontrola kanału mowy' in s for s in p['phrases'])
   first='row_0' if presentation=='RECYCLER' else 'cell_0_0'
   self.focus(first);p=self.focus('search');self.result['reader_positive']=any('Szukaj' in s for s in p['phrases'])
   if not self.result['tts_positive'] or not self.result['reader_positive']:raise RuntimeError('Positive speech control failed')
   self.step('tree-initial',lambda:self.control('tree'))
   if bursts:
    self.step('anchor-messages',lambda:self.control('anchor',target='search'));time.sleep(2)
    for mode in ['plain','polite','assertive','toast','snackbar']:
     self.step('single:'+mode,lambda m=mode:self.control('emit',mode=m,count=1),7)
     for repeat in range(1,7):self.step(f'burst:{mode}:{repeat}',lambda m=mode:self.control('emit',mode=m,count=5),20 if mode=='toast' else 9)
   self.focus(first)
   if presentation=='RECYCLER':
    for i in range(1,5):self.focus('row_'+str(i))
    for direction in ['right','up','down']:
     self.focus('search')
     for i in range(3):self.step('gesture:'+direction,lambda d=direction:self.control('gesture',direction=d))
    self.focus('folder_0');self.step('tree:expand-Documenty',lambda:self.control('action',target='folder_0',action=262144));self.focus('folder_1');self.step('tree:expand-Umowy',lambda:self.control('action',target='folder_1',action=262144));self.focus('folder_2');self.focus('folder_3');self.step('tree-expanded',lambda:self.control('tree'));self.step('tree:collapse-Umowy',lambda:self.control('action',target='folder_1',action=524288))
   else:
    for i,j in [(0,1),(0,2),(0,3),(1,0),(1,1)]:self.focus(f'cell_{i}_{j}')
   self.step('anchor-table-tab',lambda:self.control('anchor',target=first))
   for i in range(90):
    e=self.step('table-exit:Tab',lambda:self.key('61'),.6)
    states=[x['payload']['data'] for x in e['records'] if x['tag']=='UX_APP' and isinstance(x['payload'],dict) and x['payload'].get('kind')=='state']
    if states and states[-1].get('focusId')=='after_files':break
   self.step('anchor-details',lambda:self.control('anchor',target='details'));self.focus('details')
   for i in range(4):self.step('details:ArrowDown',lambda:self.key('20'))
   for i in range(3):self.step('details:ACTION_NEXT_LINE',lambda:self.control('action',target='details',action=256,granularity=4))
   self.step('anchor-details-route',lambda:self.control('anchor',target='details'))
   for i in range(16):
    e=self.step('details-to-search:Tab',lambda:self.key('61'),.8)
    states=[x['payload']['data'] for x in e['records'] if x['tag']=='UX_APP' and isinstance(x['payload'],dict) and x['payload'].get('kind')=='state']
    if states and states[-1].get('focusId')=='search':break
   if presentation=='RECYCLER':
    self.focus('search')
    for i in range(3):self.step('heading:Alt-H',lambda:self.combo('57','36'))
   self.focus(first);after=self.focus('search');self.result['reader_positive_after']=any('Szukaj' in s for s in after['phrases'])
  except Exception as e:self.result['error']=str(e)
  finally:
   self.save();(self.out/(variant+'-'+presentation+'-logcat.txt')).write_text(self.logs())
  return self.result

def main():
 if os.environ.get('CI')!='true':raise SystemExit('Ten punkt wejścia wymaga CI i emulatora; telefon: measure_device.py')
 h=Harness('out')
 if h.shell('getprop','ro.kernel.qemu').strip()!='1' or not h.adb('get-serialno').strip().startswith('emulator-'):raise SystemExit('Required emulator')
 (h.out/'startup-launch.txt').write_text(h.shell('am','start','-W','-n',PKG+'/.MainActivity'));time.sleep(4)
 h.shell('settings','put','secure','tts_default_synth',PKG);h.shell('settings','put','secure','tts_default_locale',PKG+':pl-PL')
 h.shell('settings','put','secure','show_ime_with_hard_keyboard','0');h.shell('wm','size','1080x2400');h.shell('wm','density','160')
 h.adb('shell','pm','grant','com.google.android.marvin.talkback','android.permission.POST_NOTIFICATIONS',check=False)
 h.shell('settings','put','secure','enabled_accessibility_services',OBSERVER);h.shell('settings','put','secure','accessibility_enabled','1')
 for attempt in range(60):
  if 'OBSERVER_READY' in h.logs():break
  if attempt==25:
   h.shell('settings','put','secure','enabled_accessibility_services','')
   h.shell('am','start','-W','-n',PKG+'/.MainActivity')
   h.shell('settings','put','secure','enabled_accessibility_services',OBSERVER)
  time.sleep(1)
 else:
  (h.out/'startup-logcat.txt').write_text(h.adb('logcat','-d','-v','epoch'))
  (h.out/'startup-accessibility.txt').write_text(h.shell('dumpsys','accessibility'))
  raise RuntimeError('Observer not ready')
 h.shell('settings','put','secure','enabled_accessibility_services',TALKBACK+':'+OBSERVER);time.sleep(12)
 h.shell('input','keyevent','4');h.shell('input','keyevent','3')
 for name,args in [('talkback-package.txt',('dumpsys','package','com.google.android.marvin.talkback')),('accessibility.txt',('dumpsys','accessibility')),('properties.txt',('getprop',))]:(h.out/name).write_text(h.shell(*args))
 if os.environ.get('BENCH_TOAST_ONLY')=='true':
  for variant in ['NAZWA','STAN']:
   h.result={'variant':variant,'presentation':'TOAST','evidence':'live_reader','steps':[],'error':None}
   h.shell('am','start','-f','0x10008000','-n',PKG+'/.MainActivity','--es','variant',variant);time.sleep(4)
   p=h.step('positive-tts',lambda:h.control('probe'),5);h.result['tts_positive']=any('Kontrola kanału mowy' in x for x in p['phrases'])
   h.focus('row_0');p=h.focus('search');h.result['reader_positive']=any('Szukaj' in x for x in p['phrases'])
   if not h.result['tts_positive'] or not h.result['reader_positive']:raise RuntimeError('Toast controls failed')
   h.step('single:toast',lambda:h.control('emit',mode='toast',count=1),20)
   for repeat in range(1,7):h.step(f'burst:toast:{repeat}',lambda:h.control('emit',mode='toast',count=5),20)
   h.focus('row_0');p=h.focus('search');h.result['reader_positive_after']=any('Szukaj' in x for x in p['phrases']);h.save()
  return
 if os.environ.get('BENCH_GESTURES_ONLY')=='true':
  h.result={'variant':'GESTY','presentation':'EXTRA','evidence':'live_reader','steps':[],'error':None}
  h.shell('am','start','-f','0x10008000','-n',PKG+'/.MainActivity');time.sleep(4)
  h.focus('row_0');control=h.focus('search')
  h.result['reader_positive']=any('Szukaj' in s for s in control['phrases'])
  if not h.result['reader_positive']:raise RuntimeError('Gesture positive control failed')
  for target,setting in [('search','headings'),('details','lines')]:
   h.focus(target);selected=False
   for i in range(16):
    s=h.step('reading-control:'+setting,lambda:h.control('gesture',direction='cycle'))
    if any(setting.lower() in x.lower() for x in s['phrases']):selected=True;break
   h.result[setting+'_selected']=selected
   if selected:
    for i in range(6):h.step('reading-'+setting+':down',lambda:h.control('gesture',direction='down'))
  h.save();return
 failed=[]
 for v,p,b in [('NAZWA','RECYCLER',True),('STAN','RECYCLER',True),('NAZWA','TABLE',False)]:
  r=h.measure(v,p,b)
  if r['error']:failed.append(r['error'])
 # Inna droga wstrzyknięcia. Możliwy restart celu, stąd po podstawowych seriach.
 (h.out/'instrumentation.txt').write_text(h.adb('shell','am','instrument','-w',PKG+'/.GestureProbe',check=False,timeout=120))
 (h.out/'instrumentation-logcat.txt').write_text(h.logs())
 (h.out/'final-accessibility.txt').write_text(h.shell('dumpsys','accessibility'))
 if failed:raise SystemExit('; '.join(failed))
if __name__=='__main__':main()
