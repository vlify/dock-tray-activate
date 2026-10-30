import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('activate',Path(__file__).with_name('dock-activate.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class Tests(unittest.TestCase):
 def test_recent_window(self):
  self.assertEqual(a.window_choice([{'id':1,'app_id':'QQ','focus_timestamp':{'secs':2}},{'id':2,'app_id':'QQ','focus_timestamp':{'secs':3}}],['QQ'])['id'],2)
 def test_exact_app(self):
  self.assertIsNone(a.window_choice([{'app_id':'QQ-other'}],['QQ']))
 def test_focused_first(self):
  self.assertEqual(a.window_choice([{'id':1,'app_id':'QQ','is_focused':True},{'id':2,'app_id':'QQ','focus_timestamp':{'secs':3}}],['QQ'])['id'],1)
 def test_tray_path(self):
  self.assertEqual(a.tray_target(':1.2/StatusNotifierItem'),(':1.2','/StatusNotifierItem'))
  self.assertIsNone(a.tray_target('bad'))
 def test_timeout(self):
  with patch.object(a.subprocess,'run',side_effect=subprocess.TimeoutExpired('x',5)):
   self.assertIsNone(a.run(['x']))
 def test_arguments_preserved(self):
  with patch.object(a,'run') as query,patch.object(a,'launch',return_value=0) as launch:
   a.activate({},['https://example.org/a?b=1&c=2'])
   query.assert_not_called();launch.assert_called_once_with({},['https://example.org/a?b=1&c=2'],False)
 def test_focus_success_stops(self):
  with patch.object(a,'run',side_effect=[subprocess.CompletedProcess([],0,'[{"id":5,"app_id":"QQ"}]'),subprocess.CompletedProcess([],0,'')]) as query:
   self.assertEqual(a.activate({'app_ids':['QQ']},[]),0)
   self.assertEqual(query.call_count,2)
 def test_failed_focus_uses_native_launch(self):
  with patch.object(a,'run',side_effect=[subprocess.CompletedProcess([],0,'[{"id":5,"app_id":"QQ"}]'),subprocess.CompletedProcess([],1,''),None]),patch.object(a,'launch',return_value=0) as launch:
   a.activate({'app_ids':['QQ']},[]);launch.assert_called_once()
if __name__=='__main__':unittest.main()
