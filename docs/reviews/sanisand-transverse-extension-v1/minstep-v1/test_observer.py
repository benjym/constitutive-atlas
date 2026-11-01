from decimal import Decimal as D,localcontext
from pathlib import Path
import tempfile,unittest
from trace_run import study,Observer

class ObserverTests(unittest.TestCase):
 def test_accepted_arithmetic_unchanged(self):
  with tempfile.TemporaryDirectory() as td,localcontext() as ctx:
   ctx.prec=60
   args=([D(1)],D(0),D('.1'),D('.01'),lambda y:y,[D(1)],D('1e-10'))
   plain=study.advance(*args);observer=Observer(Path(td))
   with observer.active():traced=study.advance(*args)
   self.assertEqual(plain,traced);self.assertGreater(observer.attempts,0);self.assertIsNone(observer.failure)
 def test_rejection_failure_and_state_unchanged(self):
  with tempfile.TemporaryDirectory() as td,localcontext() as ctx:
   ctx.prec=60
   def domain(y):raise study.law.Unsupported('synthetic domain')
   args=([D(1)],D(0),D('.1'),D('.01'),domain,[D(1)],D('1e-10'))
   with self.assertRaisesRegex(ValueError,'diagnostic minimum step'):study.advance(*args)
   observer=Observer(Path(td))
   with observer.active(),self.assertRaisesRegex(ValueError,'diagnostic minimum step'):study.advance(*args)
   self.assertEqual(observer.failure['y'],[D(1)]);self.assertEqual(observer.failure['accepted'],0)
   self.assertTrue(observer.unsupported['synthetic domain']>0);self.assertTrue((Path(td)/'failure.json').exists())
 def test_existing_trace_restored(self):
  import sys
  with tempfile.TemporaryDirectory() as td:
   original=sys.gettrace()
   with Observer(Path(td)).active():self.assertIsNotNone(sys.gettrace())
   self.assertIs(sys.gettrace(),original)
if __name__=='__main__':unittest.main()
