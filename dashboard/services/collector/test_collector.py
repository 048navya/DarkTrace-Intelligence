import unittest
from unittest.mock import patch
from collector import validate_url, html_record, collect
class CollectorTests(unittest.TestCase):
 def test_allowlist_and_private_addresses(self):
  with self.assertRaises(ValueError): validate_url('https://bad.example.org', {'good.example.org'})
  with patch('socket.getaddrinfo', return_value=[(2,1,6,'',('127.0.0.1',443))]):
   with self.assertRaises(ValueError): validate_url('https://good.example.org', {'good.example.org'})
 def test_onion_proxy_required(self):
  host='a'*56+'.onion'; validate_url('http://'+host,{host},True)
  with self.assertRaises(ValueError): collect({'adapter':'tor-html','url':'http://'+host},{host},'socks5://localhost:9050')
 def test_visible_evidence(self):
  r=html_record('<title>Training</title><script>hidden secret</script><p>Wallet 0x'+'a'*40+'</p>','http://'+'a'*56+'.onion',{'Server':'Example/1'})
  self.assertNotIn('hidden secret',r['text']);self.assertEqual(len(r['wallets']),1);self.assertEqual(r['indicators'][0]['type'],'banner');self.assertFalse(r['synthetic'])
if __name__=='__main__': unittest.main()
