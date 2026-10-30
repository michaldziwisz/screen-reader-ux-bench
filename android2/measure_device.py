"""Późniejszy pomiar na telefonie. Tego pliku nie uruchamiano na urządzeniu.
Jeden APK zawiera aplikację, silnik TTS i obserwatora. Zmiany wymagają jawnej zgody.
"""
import argparse,json,sys,time,signal
from pathlib import Path
from measure import Harness,PKG,TALKBACK,OBSERVER
KEYS=['tts_default_synth','tts_default_locale','enabled_accessibility_services','accessibility_enabled']
def get(h,key):return h.shell('settings','get','secure',key).strip()
def put(h,key,value):
 if value=='null':h.shell('settings','delete','secure',key)
 else:h.shell('settings','put','secure',key,value)
def restore(h,state):
 # Odbuduj połączenie TalkBack z poprzednim TTS, nie wyłączaj innych usług.
 before=state['settings']
 for key in ['tts_default_synth','tts_default_locale']:put(h,key,before[key])
 current=get(h,'enabled_accessibility_services')
 keep=[s for s in current.split(':') if s and not s.startswith('com.google.android.marvin.talkback/') and not s.startswith(PKG+'/')]
 put(h,'enabled_accessibility_services',':'.join(keep));time.sleep(2)
 put(h,'enabled_accessibility_services',before['enabled_accessibility_services']);put(h,'accessibility_enabled',before['accessibility_enabled']);time.sleep(5)
 actual={k:get(h,k) for k in KEYS};report={'restored':actual==before,'actual':actual,'expected':before}
 (h.out/'restoration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 if not report['restored']:raise RuntimeError('Nie przywrócono wszystkich ustawień; zachowaj saved-settings.json i użyj --restore')
 print('Przywrócono ustawienia TTS i usług dostępności; potwierdzenie: restoration.json',flush=True)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--serial',required=True,help='Jawny identyfikator urządzenia z adb devices')
 p.add_argument('--apk',type=Path)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--restore',type=Path,help='Przywrócenie z saved-settings.json bez pomiaru')
 p.add_argument('--confirm-settings-change',action='store_true',help='Zgoda na czasowe przełączenie TTS i TalkBack')
 args=p.parse_args();h=Harness(args.output,args.serial)
 if h.adb('get-state').strip()!='device':raise SystemExit('Urządzenie nie jest autoryzowane')
 if args.restore:
  state=json.loads(args.restore.read_text())
  if state['serial']!=args.serial:raise SystemExit('Plik ustawień pochodzi z innego urządzenia')
  restore(h,state);return
 if not args.confirm_settings_change:raise SystemExit('Wymagana jawna zgoda --confirm-settings-change. Silnik pomiarowy oddaje ciszę zamiast dźwięku.')
 if args.serial.startswith('emulator-') or h.shell('getprop','ro.kernel.qemu').strip()=='1':raise SystemExit('Ta ścieżka służy wyłącznie do telefonu fizycznego')
 if not args.apk or not args.apk.is_file():raise SystemExit('Podaj --apk z pobranego artefaktu Android2')
 if int(h.shell('getprop','ro.build.version.sdk').strip())<30:raise SystemExit('Wymagany Android API 30 lub nowszy')
 if not h.shell('pm','path','com.google.android.marvin.talkback').strip():raise SystemExit('Brak zainstalowanego TalkBack. Skrypt go nie instaluje.')
 saved=h.out/'saved-settings.json'
 if saved.exists():raise SystemExit('Użyj nowego katalogu --output; nie nadpisuję poprzedniego stanu przywracania')
 state={'serial':args.serial,'settings':{k:get(h,k) for k in KEYS}}
 saved.write_text(json.dumps(state,ensure_ascii=False,indent=2));saved.chmod(0o600)
 print('Po awarii: python3 android2/measure_device.py --serial '+repr(args.serial)+' --output '+repr(str(args.output))+' --restore '+repr(str(saved)),flush=True)
 # APK ma jeden pakiet; nie instalujemy pomocniczego serwera, test APK ani zewnętrznego TTS.
 h.adb('install','-r',str(args.apk.resolve()),timeout=120)
 def interrupted(*_):raise KeyboardInterrupt()
 signal.signal(signal.SIGTERM,interrupted)
 try:
  h.shell('am','start','-n',PKG+'/.MainActivity');time.sleep(3)
  put(h,'tts_default_synth',PKG)
  old=state['settings']['enabled_accessibility_services'];services=[] if old=='null' else [x for x in old.split(':') if x]
  if not any(x.startswith('com.google.android.marvin.talkback/') for x in services):services.append(TALKBACK)
  if OBSERVER not in services:services.append(OBSERVER)
  put(h,'enabled_accessibility_services',':'.join(services));put(h,'accessibility_enabled','1');time.sleep(12)
  (h.out/'talkback-package.txt').write_text(h.shell('dumpsys','package','com.google.android.marvin.talkback'))
  # Nie zapisujemy całego dumpsys telefonu ani pełnego logcat z danymi innych aplikacji.
  for variant in ['NAZWA','STAN']:
   r=h.measure(variant,'RECYCLER',True)
   if r['error']:raise RuntimeError(r['error'])
  # Osobna seria gestów fizycznych. ACTION_ACCESSIBILITY_FOCUS to tylko kotwica.
  h.result={'variant':'GESTY_FIZYCZNE','presentation':'RECYCLER','evidence':'live_reader','steps':[],'error':None}
  h.focus('row_0');check=h.focus('search')
  if not any('Szukaj' in x for x in check['phrases']):raise RuntimeError('Kontrola TalkBack przed gestami nieudana')
  for repeat in range(1,7):
   h.focus('search')
   def physical():
    input(f'Próba {repeat}: po tym komunikacie przesuń palcem w prawo na telefonie, następnie naciśnij Enter w terminalu. ')
   h.step(f'physical-right:{repeat}',physical,2)
  h.save()
 finally:restore(h,state)
if __name__=='__main__':main()
