import unittest,sys,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from metrics import word_stats,messages,bursts,walk,route
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
 def test_device_static_restoration(self):
  # Analiza składni, bez importu lub uruchomienia skryptu telefonu.
  source=(Path(__file__).resolve().parents[1]/'android2/measure_device.py').read_text()
  module=ast.parse(source);self.assertTrue(any(isinstance(n,ast.Try) and any(isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and getattr(x.value.func,'id',None)=='restore' for x in n.finalbody) for n in ast.walk(module)))
  self.assertIn('state[\'serial\']!=args.serial',source)
if __name__=='__main__':unittest.main()
