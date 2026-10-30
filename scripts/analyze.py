"""Wyliczenia tylko z pobranych artefaktów. Jawne źródło każdej serii."""
import argparse,hashlib,json,statistics
from pathlib import Path
from metrics import words,summary,TARGETS

def walk(n):
 yield n
 for c in n.get("children",[]):yield from walk(c)
def load(p):return json.loads(Path(p).read_text())
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
def source(p,rid):return {"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"run":rid,"url":f"https://github.com/michaldziwisz/screen-reader-ux-bench/actions/runs/{rid}"}
def text(s):return " ".join(x for x in s.get("phrases",[]) if x)
def stop_mac(s):
 f=s["after"].get("focus",{})
 return {"id":f.get("AXIdentifier",""),"role":f.get("AXRole",""),"label":f.get("AXDescription",f.get("AXTitle","")),"value":f.get("AXValue",""),"text":text(s),"words":words(text(s)),"action":s["kind"],"api_ms":s.get("api_ms"),"item":s["item"]}
def macos(rid):
 out=[]
 for v in ["GRUPY","PLASKI"]:
  p=Path(f"wyniki/macos/{rid}/macos-measure/{v}.json");d=load(p)
  assert d["positive"] and not d["error"],"Nieudany pomiar macOS"
  seq=[stop_mac(next(s for s in d["steps"] if s["kind"]=="probe"))]+[stop_mac(s) for s in d["steps"] if s["kind"]=="Tab"]
  assert seq[0]["id"]=="imie"
  data={"platform":"macos","variant":v,"evidence":"live_reader","source":source(p,rid),"stops":seq,"summary":summary(seq),"vo":[stop_mac(s) for s in d["steps"] if s["kind"].startswith("VO")],"dialog_closed":not any(n.get("AXTitle")=="Tak" for n in walk(d["dialog_after"]["tree"])),"shortcut_saved":any(n.get("AXTitle")=="UXPomiar zapisano" for n in walk(d["dialog_before"]["tree"]))}
  assert data["summary"]["task"]["complete"],"Za krótka sekwencja do ukończenia zadania"
  cycle=next(i for i,s in enumerate(seq[1:],1) if s["id"]=="imie")
  data["cycle_length"]=cycle;data["cycle_words_median"]=statistics.median(s["words"] for s in seq[1:cycle+1])
  save(f"results/macos-{v}.json",d);out.append(data)
 return out

ROLES={1:"other/group",9:"button",25:"table",26:"table",40:"cell",48:"staticText",49:"textField",75:"switch"}
def ios(rid):
 out=[]
 for p in Path(f"wyniki/ios/{rid}/ios-measure/attachments").glob("*.json"):
  d=load(p)
  if not isinstance(d,dict) or "variant"not in d:continue
  seq=[];ids=set()
  for n in walk(d["tree"]):
   id=n["id"]
   if not id or id in ids:continue
   ids.add(id)
   label=n["label"] or next((c["label"] for c in walk(n) if c["label"]),"")
   value=n["value"];t=" ".join(x for x in [label,value] if x)
   seq.append({"id":id,"label":label,"value":value,"role":ROLES.get(n["role"],str(n["role"])),"role_raw":n["role"],"enabled":n["enabled"],"selected":n["selected"],"text":t,"words":words(t)})
  pos={s["id"]:i for i,s in enumerate(seq)};start=pos["imie"]
  forward=summary(seq[start:])["task"]
  at=start;steps=0;wc=0;legs=[]
  for target in TARGETS[1:]:
   hit=pos[target];delta=1 if hit>at else -1
   route=[seq[i] for i in range(at+delta,hit+delta,delta)]
   cost=sum(s["words"] for s in route);steps+=len(route);wc+=cost
   legs.append({"target":target,"steps":len(route),"words":cost,"direction":"next" if delta==1 else "previous"});at=hit
  data={"platform":"ios","variant":d["variant"],"evidence":"accessibility_tree_NOT_speech","source":source(p,rid),"stops":seq,"index_of_name":start,"distance_from_name":{s["id"]:abs(i-start) for i,s in enumerate(seq)},"forward_task":forward,"bidirectional_model":{"steps":steps,"words":wc,"legs":legs},"dialog_closed":d["escape_closed_dialog"],"shortcut_saved":any(n["value"]=="Zapisano zamówienie" for n in walk(d["after_shortcut"])),"audit_issues":d["audit_issues"],"tree_groups":[n["label"] for n in walk(d["tree"]) if n["role"]==1 and n["label"]]}
  save(f"results/ios-{d['variant']}.json",d);out.append(data)
 assert len(out)==2
 return sorted(out,key=lambda x:x["variant"])

LABELS={"imię":"imie","nazwisko":"nazw","kraj":"kraj","liczba sztuk":"szt","wystaw fakturę":"faktura","zapisz na newsletter":"news","kurier":"sposob_0","paczkomat":"sposob_1","odbiór osobisty":"sposob_2","ostatnie zamówienia":"lista","zapisz zamówienie":"zapisz","anuluj":"anuluj","pokaż komunikat":"komunikat","zapisz jako plik":"plik"}
def android_id(n):
 t=(n.get("label") or n.get("text","")).casefold()
 if t.startswith("zamówienie "):return "order_"+t.split()[-1]
 return LABELS.get(t,t)
def android_records(s,tag):return [r for r in s["records"] if r["tag"]==tag and isinstance(r["payload"],dict)]
def android_text(s):
 mark=next((r["time"] for r in s["records"] if r["tag"]=="UXMARK"),None)
 return " ".join(r["payload"]["text"] for r in android_records(s,"UX_TTS") if mark is None or r["time"]>=mark)
def android(rid):
 out=[]
 for v in ["GRUPY","PLASKI"]:
  p=Path(f"wyniki/android/{rid}/android-measure/{v}.json");d=load(p)
  assert d["tts_positive"] and d["reader_positive"] and not d["error"]
  def sequence(kind,anchor_name):
   anchor=next(s for s in d["steps"] if s["kind"]==anchor_name)
   candidates=android_records(anchor,"UX_AX")
   node=next((r["payload"]["node"] for r in reversed(candidates) if r["payload"].get("event") in [8,32768]),{"label":"Imię","role":"android.widget.EditText"})
   seq=[{"id":"imie","label":"Imię","role":"android.widget.EditText","text":android_text(anchor),"words":words(android_text(anchor)),"action":anchor_name,"anchor_requested":True}]
   for s in d["steps"]:
    if s["kind"]!=kind:continue
    records=android_records(s,"UX_AX")
    events=[r["payload"]["node"] for r in records if r["payload"].get("event")== (8 if kind=="Tab" else 32768) and "node"in r["payload"]]
    if not events:events=[r["payload"]["node"] for r in records if r["payload"].get("event")==32768 and "node"in r["payload"]]
    if events:node=events[-1]
    t=android_text(s)
    seq.append({"id":android_id(node),"label":node.get("label",node.get("text","")),"value":node.get("text",""),"role":node["role"],"text":t,"words":words(t),"action":kind,"focus_event":bool(events),"marker_to_tts_ms":s["marker_to_tts_ms"],"state":{k:node.get(k) for k in ["enabled","checked","selected"]}})
   return seq
  seq=sequence("Tab","anchor-tab")
  next_mode="hardware-Alt-Right" if any(s["kind"]=="hardware-Alt-Right" for s in d["steps"]) else "Alt-Right"
  alt=sequence(next_mode,"anchor-hardware" if next_mode=="hardware-Alt-Right" else "anchor-reader-next") if any(s["kind"]==next_mode for s in d["steps"]) else []
  tree=[r["payload"] for s in d["steps"] if s["kind"]=="tree" for r in android_records(s,"UX_TREE")]
  before=[r["payload"] for s in d["steps"] if s["kind"]=="dialog-tree-before" for r in android_records(s,"UX_TREE")]
  after=[r["payload"] for s in d["steps"] if s["kind"]=="dialog-tree-after" for r in android_records(s,"UX_TREE")]
  nswipes=sum(s["kind"]=="swipe-next" for s in d["steps"])
  moved=sum(any(r["payload"].get("event")==32768 for r in android_records(s,"UX_AX")) for s in d["steps"] if s["kind"]=="swipe-next")
  lat=[s["marker_to_tts_ms"] for s in seq[1:] if s["marker_to_tts_ms"] is not None and s["marker_to_tts_ms"]>=0]
  data={"platform":"android","variant":v,"evidence":"live_reader_TTS_input","source":source(p,rid),"stops":seq,"summary":summary(seq),"reader_next":alt,"reader_next_mode":next_mode,"reader_next_summary":summary(alt),"tree":tree,"swipe_attempts":nswipes,"swipe_focus_events":moved,"dialog_closed":any(n["text"]=="TAK" for n in before) and not any(n["text"]=="TAK" for n in after),"shortcut_saved":any("Zapisano zamówienie"in android_text(s) for s in d["steps"] if s["kind"]=="shortcut-Ctrl-S"),"marker_to_tts_median_ms":statistics.median(lat) if lat else None,"marker_to_tts_n":len(lat)}
  data["cycle_length"]=next((i for i,s in enumerate(seq[1:],1) if s["id"]=="imie"),None)
  cycle=seq[1:data["cycle_length"]+1] if data["cycle_length"] else seq[1:]
  data["cycle_words_median"]=statistics.median(s["words"] for s in cycle)
  save(f"results/android-{v}.json",d);out.append(data)
 return out

def catalyst(rid):
 out=[]
 for v in ["GRUPY","PLASKI"]:
  p=Path(f"wyniki/catalyst/{rid}/catalyst-measure/catalyst-{v}.json");d=load(p)
  seq=[stop_mac(s) for s in d["steps"]]
  data={"platform":"catalyst","variant":v,"source":source(p,rid),"evidence":"live_macos_reader_NOT_iOS_partial","stops":seq,"focused_ids":sorted(set(s["id"] for s in seq)),"empty_windows":sum(not s["text"] for s in seq),"positive":d.get("positive"),"error":d.get("error")}
  save(f"results/catalyst-{v}.json",d);out.append(data)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--macos");ap.add_argument("--ios");ap.add_argument("--android");ap.add_argument("--catalyst");a=ap.parse_args()
 out=[]
 if a.macos:out+=macos(a.macos)
 if a.ios:out+=ios(a.ios)
 if a.android:out+=android(a.android)
 if a.catalyst:out+=catalyst(a.catalyst)
 save("results/summary.json",out)
 for d in out:print(d["platform"],d["variant"],len(d["stops"]),d.get("summary",d.get("bidirectional_model")))
if __name__=="__main__":main()
