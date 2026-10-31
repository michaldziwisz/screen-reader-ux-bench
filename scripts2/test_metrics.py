import unittest,sys,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from metrics import word_stats,messages,bursts,walk,route,android_table_exit
class MetricsTests(unittest.TestCase):
 def test_words(self):
  self.assertEqual(word_stats(['Stan: gotowy; Nazwa: Faktura marzec'],'Faktura marzec')['name_word'],4)
  self.assertEqual(word_stats([], 'Faktura marzec')['name_word'],None)
 def test_messages_dedup(self):
  self.assertEqual(messages(['Plik 5 z 5 skopiowany','Plik 2 z 5 skopiowany','Plik 5 z 5 skopiowany']),[2,5])
  self.assertEqual(messages(['Kontrola 1 z 5']),[])
 def test_bursts_sort(self):
  self.assertEqual([x['repeat'] for x in bursts({'steps':[{'kind':'burst:high:2','phrases':[]},{'kind':'burst:high:1','phrases':[]}]})['high']],[1,2])
 def test_missing_route_not_zero(self):
  self.assertIsNone(route({'steps':[]},'Tab','search','macos')['steps'])
 def test_plain_node_is_not_speech(self):
  self.assertEqual(len(list(walk({'label':'tekst','children':[{'label':'dziecko'}]}))),2)
 def test_table_anchor_from_observed_focus(self):
  data={'presentation':'RECYCLER','steps':[{'kind':'anchor-table-tab','state':{'focusId':'search'}},*({'kind':'table-exit:Tab','state':{'focusId':i}} for i in ['folder_0','row_0','row_1','after_files'])]}
  result=android_table_exit(data)
  self.assertEqual(result['steps'],2)
  self.assertEqual(result['pre_anchor_steps_excluded'],2)
  self.assertFalse(result['anchor_valid'])
 def test_missing_table_anchor_is_not_count(self):
  data={'presentation':'RECYCLER','steps':[{'kind':'anchor-table-tab','state':{'focusId':'search'}},{'kind':'table-exit:Tab','state':{'focusId':'after_files'}}]}
  self.assertIsNone(android_table_exit(data)['steps'])
 def test_harness_call_signatures(self):
  module=ast.parse((Path(__file__).resolve().parents[1]/'android2/measure.py').read_text())
  methods={n.name for c in module.body if isinstance(c,ast.ClassDef) and c.name=='Harness' for n in c.body if isinstance(n,ast.FunctionDef)}
  for n in ast.walk(module):
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='h':
    self.assertIn(n.func.attr,methods)
    if n.func.attr in ['key','combo']:self.assertTrue(all(isinstance(a,ast.Constant) and isinstance(a.value,str) for a in n.args))
    if n.func.attr=='control':
     for kw in n.keywords:
      if kw.arg in ['action','granularity']:
       assert isinstance(kw.value,ast.Constant)
       self.assertIsInstance(kw.value.value,int)
 def test_device_static_restoration(self):
  # Analiza składni, bez importu lub uruchomienia skryptu telefonu.
  source=(Path(__file__).resolve().parents[1]/'android2/measure_device.py').read_text()
  module=ast.parse(source);self.assertTrue(any(isinstance(n,ast.Try) and any(isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and getattr(x.value.func,'id',None)=='restore' for x in n.finalbody) for n in ast.walk(module)))
  self.assertIn('state[\'serial\']!=args.serial',source)
if __name__=='__main__':unittest.main()
