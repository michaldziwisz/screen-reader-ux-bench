import unittest
from metrics import task_path,words,summary
class MetricsTests(unittest.TestCase):
 def test_missing_not_zero(self):
  self.assertIsNone(task_path([{"id":"imie"}])["steps"])
 def test_no_implied_wrap(self):
  ids=["zapisz","lista","nazw","news","szt","komunikat","imie","sposob","anuluj","kraj","faktura","plik"]
  self.assertFalse(task_path([{"id":s} for s in ids[6:]])["complete"])
 def test_reference_paths(self):
  # Dane jednostkowe, NIE pomiar. Kontrola definicji sześciu celów.
  a=["imie","nazw","sposob","kraj","szt","faktura","news","lista","zapisz","anuluj","komunikat","plik"]
  self.assertEqual(task_path([{"id":s} for s in a])["steps"],8)
  b=["zapisz","lista","nazw","news","szt","komunikat","imie","sposob","anuluj","kraj","faktura","plik"]
  repeated=(b*4)[6:]
  self.assertEqual(task_path([{"id":s} for s in repeated])["steps"],30)
 def test_words(self):self.assertEqual(words("Imię  pole\nedycji"),3)
 def test_leg_accounting(self):
  s=[{"id":x,"text":"dwa słowa"} for x in ["imie","nazw","kraj","szt","faktura","zapisz"]]
  self.assertEqual(task_path(s)["words"],10)
if __name__=="__main__":unittest.main()
