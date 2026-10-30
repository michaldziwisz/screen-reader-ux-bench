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

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--macos");ap.add_argument("--ios");a=ap.parse_args()
 out=[]
 if a.macos:out+=macos(a.macos)
 if a.ios:out+=ios(a.ios)
 save("results/summary.json",out)
 for d in out:print(d["platform"],d["variant"],len(d["stops"]),d.get("summary",d.get("bidirectional_model")))
if __name__=="__main__":main()
