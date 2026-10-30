"""Skan plików przed publikacją. Nie wypisuje dopasowanych wartości."""
import json
import re
import subprocess
import sys
from pathlib import Path

RULES = {
    "github": r"gh[pousr]_" + r"[A-Za-z0-9]{20,}",
    "fine_grained": r"github_pat_" + r"[A-Za-z0-9_]{20,}",
    "api_key": r"sk-" + r"[A-Za-z0-9_-]{20,}",
    "private_key": r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY",
    "secret_assignment": r"(?i)(?:token|password|api[_-]?key)\s*[:=]\s*[\"']?[A-Za-z0-9_/-]{24,}",
    "private_home": r"/home/" + "ubuntu",
}

def scan(paths):
    issues=[]
    for p in paths:
        data=Path(p).read_text(errors="replace")
        for name, pattern in RULES.items():
            if re.search(pattern, data):
                issues.append({"file":str(p), "rule":name})
    return issues

if __name__ == "__main__":
    paths=sys.argv[1:] or subprocess.check_output(["git","ls-files"],text=True).splitlines()
    issues=scan(paths)
    print(json.dumps({"files":len(paths), "findings":issues}, ensure_ascii=False))
    sys.exit(bool(issues))
