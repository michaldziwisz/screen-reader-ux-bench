"""Pobiera ukończone przebiegi i zachowuje historię prób lokalnie."""
import json,subprocess
from pathlib import Path

def gh(*args):return subprocess.check_output(["gh",*args],text=True)
runs=json.loads(gh("run","list","--limit","100","--json","databaseId,status,conclusion,workflowName,url,headSha,createdAt,updatedAt"))
assert len(runs)<=25, "Przekroczono budżet CI"
platforms={"Android TalkBack":"android","iOS drzewo dostępności":"ios","macOS VoiceOver":"macos","Catalyst przybliżenie":"catalyst","Rozpoznanie CI":"scout"}
base=Path("wyniki");base.mkdir(exist_ok=True)
(base/"runs.json").write_text(json.dumps(runs,ensure_ascii=False,indent=2))
for r in runs:
 if r["status"]!="completed":continue
 folder=base/platforms[r["workflowName"]]/str(r["databaseId"]);folder.mkdir(parents=True,exist_ok=True)
 (folder/"run.json").write_text(json.dumps(r,ensure_ascii=False,indent=2))
 if not (folder/"workflow.log").exists():
  subprocess.run(["gh","run","download",str(r["databaseId"]),"-D",str(folder)],check=False)
  (folder/"workflow.log").write_text(gh("run","view",str(r["databaseId"]),"--log"))
 print(r["databaseId"],r["workflowName"],r["conclusion"])
print("Przebiegów:",len(runs),"; ukończonych:",sum(r["status"]=="completed" for r in runs))
