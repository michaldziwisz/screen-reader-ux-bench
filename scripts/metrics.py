"""Koszt z zaobserwowanej sekwencji, bez domyślnego zapętlenia."""
import statistics
TARGETS=["imie","nazw","kraj","szt","faktura","zapisz"]
def words(text):return len(text.split())
def task_path(stops,targets=TARGETS):
 """stops[0] to pozycja startowa. Brak celu => null, nigdy zero."""
 if not stops or stops[0]["id"]!=targets[0]:return {"complete":False,"reason":"Brak startu na Imieniu"}
 at=0;total_words=0;legs=[]
 for target in targets[1:]:
  hit=next((i for i in range(at+1,len(stops)) if stops[i]["id"]==target),None)
  if hit is None:return {"complete":False,"missing":target,"legs":legs,"steps":None,"words":None}
  cost=sum(words(s.get("text","")) for s in stops[at+1:hit+1])
  legs.append({"target":target,"steps":hit-at,"words":cost,"from":at,"to":hit})
  total_words+=cost;at=hit
 return {"complete":True,"steps":at,"words":total_words,"legs":legs}
def first_targets(stops):
 return {target:next((i for i,s in enumerate(stops) if s["id"]==target),None) for target in dict.fromkeys(s["id"] for s in stops if s["id"])}
def summary(stops):
 counts=[words(s.get("text","")) for s in stops]
 return {"stops":len(stops),"words_total":sum(counts),"words_median":statistics.median(counts) if counts else None,"first_steps":first_targets(stops),"task":task_path(stops)}
