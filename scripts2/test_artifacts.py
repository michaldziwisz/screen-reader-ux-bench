import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import verify_results as verify

class ArtifactTests(unittest.TestCase):
 def check_mutation(self,mutate,rehash):
  spec=next(x for x in verify.load('manifest.json') if x['target']=='macos-NAZWA.json')
  data=verify.load(spec['target']);mutate(data)
  raw=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode()
  spec=copy.deepcopy(spec)
  if rehash:spec['projection_sha256']=hashlib.sha256(raw).hexdigest()
  folder=verify.ROOT/'wyniki';folder.mkdir(exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='validator-',dir=folder) as temp:
   root=Path(temp);(root/spec['target']).write_bytes(raw);(root/'manifest.json').write_text(json.dumps([spec]))
   with patch.object(verify,'OUT',root):
    with self.assertRaises(AssertionError):verify.run()
 def test_checksum_rejects_changed_evidence(self):
  self.check_mutation(lambda d:d.update(positive=False),False)
 def test_missing_repeat_rejected_after_rehash(self):
  self.check_mutation(lambda d:d['steps'].remove(next(s for s in d['steps'] if s['kind']=='burst:high:6')),True)
 def test_missing_emission_rejected_after_rehash(self):
  def mutate(d):
   ev=next(s for s in d['steps'] if s['kind']=='burst:high:1')['app']['new_events'];ev.remove(next(e for e in ev if e['kind']=='emit'))
  self.check_mutation(mutate,True)
if __name__=='__main__':unittest.main()
