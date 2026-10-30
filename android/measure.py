"""Pomiar w emulatorze CI. Nigdy nie uruchamiać na urządzeniu prywatnym."""
import json, subprocess, time, re, os
if os.environ.get("CI")!="true":raise SystemExit("Pomiar dozwolony wyłącznie w CI")
from pathlib import Path
OUT=Path("out");OUT.mkdir(exist_ok=True)
def adb(*args,check=True):
 r=subprocess.run(["adb",*args],check=False,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
 if check and r.returncode:raise RuntimeError(str(args)+": "+r.stdout)
 return r.stdout
def shell(*args):return adb("shell",*args)
def control(command,label=None):
 args=["am","broadcast","-n","org.uxbench/.Control","--es","command",command]
 if label:args += ["--es","label",label]
 return shell(*args)
def logs():return adb("logcat","-d","-v","epoch","UX_TTS:I","UX_AX:I","UX_TREE:I","UXMARK:I","*:S")
def parse(raw):
 records=[]
 for line in raw.splitlines():
  m=re.match(r"\s*([\d.]+)\s+\d+\s+\d+\s+\w\s+(UX_\w+|UXMARK)\s*: (.*)",line)
  if m:
   ts,tag,payload=m.groups()
   try:payload=json.loads(payload)
   except ValueError:pass
   records.append({"time":float(ts),"tag":tag,"payload":payload})
 return records
if shell("getprop","ro.kernel.qemu").strip()!="1" or not adb("get-serialno").strip().startswith("emulator-"):
 raise SystemExit("Odmowa: wymagany emulator")
# Pierwsze uruchomienie usuwa stan pakietu „stopped” po instalacji.
shell("am","start","-n","org.uxbench/.MainActivity","--es","variant","GRUPY")
time.sleep(2)
shell("settings","put","secure","tts_default_synth","org.uxbench")
shell("settings","put","secure","tts_default_locale","org.uxbench:pl-PL")
shell("settings","put","system","font_scale","1.0")
shell("settings","put","secure","show_ime_with_hard_keyboard","0")
shell("wm","size","1080x2400");shell("wm","density","160")
# Zgoda dotyczy wyłącznie powiadomień systemowego TalkBack w emulatorze.
(OUT/"startup.txt").write_text(adb("shell","pm","grant","com.google.android.marvin.talkback","android.permission.POST_NOTIFICATIONS",check=False))
shell("settings","put","secure","enabled_accessibility_services","org.uxbench/.Observer")
shell("settings","put","secure","accessibility_enabled","1")
for attempt in range(30):
 if "OBSERVER_READY" in logs():break
 time.sleep(1)
else:
 (OUT/"startup-logcat.txt").write_text(adb("logcat","-d","-v","epoch"))
 (OUT/"startup-accessibility.txt").write_text(shell("dumpsys","accessibility"))
 raise RuntimeError("Obserwator nie uruchomił się w czasie kontrolnym")
services="com.google.android.marvin.talkback/.TalkBackService:org.uxbench/.Observer"
shell("settings","put","secure","enabled_accessibility_services",services)
time.sleep(12)
shell("input","keyevent","4");shell("input","keyevent","3")
(OUT/"talkback-package.txt").write_text(shell("dumpsys","package","com.google.android.marvin.talkback"))
(OUT/"accessibility.txt").write_text(shell("dumpsys","accessibility"))
(OUT/"properties.txt").write_text(shell("getprop"))
collector_file=(OUT/"continuous-logcat.txt").open("w")
collector=subprocess.Popen(["adb","logcat","-v","epoch"],stdout=collector_file,stderr=subprocess.STDOUT)
failed=False
for variant in ["GRUPY","PLASKI"]:
 r={"variant":variant,"evidence":"live_reader","steps":[],"error":None}
 def save(): (OUT/(variant+".json")).write_text(json.dumps(r,ensure_ascii=False,indent=2))
 def step(kind,action):
  adb("logcat","-c")
  shell("log","-t","UXMARK",kind)
  action();time.sleep(5 if kind=="tts-control" else 1.3)
  raw=logs();records=parse(raw)
  with (OUT/(variant+"-speech.log")).open("a") as f:f.write("\n# "+kind+"\n"+raw)
  phrases=[x["payload"]["text"] for x in records if x["tag"]=="UX_TTS" and isinstance(x["payload"],dict)]
  mark=next((x["time"] for x in records if x["tag"]=="UXMARK"),None)
  first=next((x["time"] for x in records if x["tag"]=="UX_TTS"),None)
  entry={"kind":kind,"phrases":phrases,"words":len(" ".join(phrases).split()),"marker_to_tts_ms":round((first-mark)*1000,3) if mark and first else None,"records":records}
  r["steps"].append(entry);save();return entry
 try:
  shell("am","start","-f","0x10008000","-n","org.uxbench/.MainActivity","--es","variant",variant)
  time.sleep(3)
  probe=step("tts-control",lambda:control("probe"))
  r["tts_positive"]=any("Kontrola kanału mowy" in x for x in probe["phrases"])
  step("prepare-anchor",lambda:control("focus","Nazwisko"))
  anchor=step("anchor",lambda:control("focus","Imię"))
  # Odrębna kontrola czytnika, nie tylko wywołania TTS z aplikacji.
  r["reader_positive"]=any("Imię" in x for x in anchor["phrases"])
  step("tree",lambda:control("tree"))
  if not r["tts_positive"] or not r["reader_positive"]:
   raise RuntimeError("Positive control failed")
  for i in range(3): step("swipe-next",lambda:shell("input","swipe","350","900","800","900","120"))
  r["swipe_moved"]=any(x["tag"]=="UX_AX" and isinstance(x["payload"],dict) and x["payload"].get("event")==32768 for s in r["steps"] if s["kind"]=="swipe-next" for x in s["records"])
  step("prepare-keyboard",lambda:control("focus","Nazwisko"))
  step("anchor-reader-next",lambda:control("focus","Imię"))
  alt_moved=False
  for i in range(65):
   s=step("Alt-Right",lambda:shell("input","keycombination","57","22"))
   alt_moved=alt_moved or any(x["tag"]=="UX_AX" and isinstance(x["payload"],dict) and x["payload"].get("event")==32768 for x in s["records"])
   if i==2 and not alt_moved:break
  r["alt_moved"]=alt_moved
  if not alt_moved:
   (OUT/"emulator-event-codes.txt").write_text(adb("emu","event","codes","EV_KEY"))
   step("prepare-hardware",lambda:control("focus","Nazwisko"))
   step("anchor-hardware",lambda:control("focus","Imię"))
   def hardware_next():
    adb("emu","event","send","EV_KEY:KEY_LEFTALT:1","EV_KEY:KEY_RIGHT:1","EV_SYN:SYN_REPORT:0")
    time.sleep(0.08)
    adb("emu","event","send","EV_KEY:KEY_RIGHT:0","EV_KEY:KEY_LEFTALT:0","EV_SYN:SYN_REPORT:0")
   hardware_moved=False
   for i in range(65):
    s=step("hardware-Alt-Right",hardware_next)
    hardware_moved=hardware_moved or any(x["tag"]=="UX_AX" and isinstance(x["payload"],dict) and x["payload"].get("event")==32768 for x in s["records"])
    if i==2 and not hardware_moved:break
   r["hardware_moved"]=hardware_moved
  step("anchor-tab",lambda:control("anchor"))
  for i in range(65):step("Tab",lambda:shell("input","keyevent","61"))
  step("shortcut-Ctrl-S",lambda:shell("input","keycombination","113","47"))
  step("dialog-open",lambda:control("dialog"));step("dialog-tree-before",lambda:control("tree"))
  step("dialog-back",lambda:shell("input","keyevent","4"));step("dialog-tree-after",lambda:control("tree"))
 except Exception as e:r["error"]=str(e);failed=True
 finally:
  save();(OUT/(variant+"-activity.txt")).write_text(shell("dumpsys","activity","activities"))
  with (OUT/(variant+".png")).open("wb") as f:subprocess.run(["adb","exec-out","screencap","-p"],stdout=f,check=False)
(OUT/"full-logcat.txt").write_text(adb("logcat","-d","-v","epoch"))
collector.terminate();collector.wait(timeout=10);collector_file.close()
if failed:raise SystemExit(1)
