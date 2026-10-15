"""Real disposable PostgreSQL integration test. Does not touch the user's database."""
import importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from urllib.parse import urlsplit,parse_qs,unquote
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'darkweb-deanonymization'
sys.path.insert(0,str(PROJECT/'backend'))

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.getenv('DARKTRACE_DISPOSABLE_TEST_DB') != '1':
            raise RuntimeError('Run through node tests/run_repository_tests.mjs to create a disposable database')
        os.environ['DARKTRACE_API_KEY']='repository-integration-test-secret-32-characters'
        for name in ('LOCAL_RPC_URL','LOCAL_PRIVATE_KEY','CONTRACT_ADDRESS'):os.environ.pop(name,None)
        module(PROJECT/'scripts/init_db.py','schema_init').initialize()
        loader=module(PROJECT/'scripts/load_samples.py','sample_loader');loader.load();loader.load()
        from fastapi.testclient import TestClient
        from app.main import app
        cls.client=TestClient(app);cls.headers={'x-api-key':os.environ['DARKTRACE_API_KEY']}
    @classmethod
    def tearDownClass(cls):cls.client.close()
    def test_01_health_auth_samples(self):
        self.assertEqual(self.client.get('/health').status_code,200)
        self.assertEqual(self.client.get('/actors/').status_code,401)
        r=self.client.get('/actors/',headers=self.headers);self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['actors']),3)
        self.assertEqual(self.client.get('/blockchain/status',headers=self.headers).json()['configured'],False)
        from app.crud import fetch_one
        self.assertEqual(fetch_one('SELECT count(*) AS n FROM wallets')['n'],4)
        self.assertEqual(fetch_one('SELECT count(*) AS n FROM evidence')['n'],3)
        module(PROJECT/'scripts/init_db.py','repeat_init').initialize()
        self.assertEqual(fetch_one('SELECT count(*) AS n FROM posts')['n'],4)
    def test_02_snapshot_filters_and_provenance(self):
        r=self.client.get('/interop/snapshot?limit=2',headers=self.headers);self.assertEqual(r.status_code,200);d=r.json();self.assertEqual(len(d['records']),2);self.assertEqual(d['nextOffset'],2)
        self.assertTrue(all(x['synthetic'] for x in d['records']));self.assertTrue(all(not x['wallets'] for x in d['records']))
        self.assertIn('Source:',d['records'][0]['text'])
        self.assertEqual(self.client.get('/interop/snapshot?date_from=2025-01-01',headers=self.headers).json()['total'],0)
        self.assertEqual(self.client.get('/interop/snapshot?date_from=2026-01-01&date_to=2024-01-01',headers=self.headers).status_code,422)
        from app.routes.interop import normalize_post
        self.assertIsNone(normalize_post({'post_id':'no-date'}))
    def test_03_corpus_analysis_and_reviews(self):
        env={**os.environ,'DARKTRACE_DATASET_PATH':str(PROJECT/'data/synthetic_corpus.jsonl'),'DARKTRACE_SOURCE_NAME':'Bundled synthetic corpus fixture'}
        result=subprocess.run([sys.executable,str(PROJECT/'ingestion/darkforums_loader.py')],env=env,capture_output=True,text=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stderr)
        from app.crud import fetch_one
        self.assertEqual(fetch_one('SELECT count(*) AS n FROM posts')['n'],22)
        result=subprocess.run([sys.executable,str(PROJECT/'ai/feature_extraction.py')],env=env,capture_output=True,text=True,timeout=120)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        summary=self.client.get('/intelligence/summary',headers=self.headers).json()['summary'];self.assertGreater(summary['total_personas'],1)
        links=self.client.get('/intelligence/relationships',headers=self.headers).json()['relationships'];self.assertGreater(len(links),0)
        r=self.client.post('/interop/reviews',headers=self.headers,json={'relationship_id':links[0]['relationship_id'],'decision':'pending','reason':'Fictional fixture; requires independent evidence.'});self.assertEqual(r.status_code,200)
        self.assertEqual(len(self.client.get('/interop/reviews',headers=self.headers).json()['reviews']),1)
        self.assertEqual(self.client.post('/interop/reviews',headers=self.headers,json={'relationship_id':999999,'decision':'accepted','reason':'Test invalid reference'}).status_code,404)
        for route in ['/actors/','/handles/','/posts/','/search/?q=fictional','/intelligence/personas','/intelligence/clusters']:
            self.assertEqual(self.client.get(route,headers=self.headers).status_code,200,route)
    def test_04_compiled_dashboard_bridge(self):
        if os.getenv('TEST_DASHBOARD_BRIDGE')!='1': self.skipTest('Set TEST_DASHBOARD_BRIDGE=1 after building dashboard')
        import socket,time,urllib.request
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        env={**os.environ,'REPOSITORY_API_URL':f'http://127.0.0.1:{port}','REPOSITORY_API_KEY':os.environ['DARKTRACE_API_KEY']}
        proc=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(port)],cwd=PROJECT/'backend',env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            for _ in range(60):
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=1):break
                except Exception:time.sleep(.2)
            else:self.fail('Test API failed to start')
            result=subprocess.run(['node','tests/integration.mjs'],cwd=ROOT/'dashboard',env=env,capture_output=True,text=True,timeout=90)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            print(result.stdout)
        finally:proc.terminate();proc.wait(timeout=10)
    def test_05_uploaded_corpus(self):
        path=os.getenv('DARKTRACE_CORPUS_TEST_PATH')
        if not path:self.skipTest('No external corpus supplied')
        env={**os.environ,'DARKTRACE_DATASET_PATH':path,'DARKTRACE_SOURCE_NAME':'User provided corpus test'}
        for _ in range(2):
            result=subprocess.run([sys.executable,str(PROJECT/'ingestion/darkforums_loader.py')],env=env,capture_output=True,text=True,timeout=90)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        from app.crud import fetch_one
        row=fetch_one("SELECT count(*) AS posts,count(DISTINCT handle_id) AS labels FROM posts WHERE source='User provided corpus test'")
        self.assertEqual(row['posts'],154);self.assertEqual(row['labels'],154)
        row=fetch_one("SELECT count(*) AS threads,count(*) FILTER(WHERE created_at IS NULL) AS undated FROM threads WHERE source='User provided corpus test'")
        self.assertEqual(row['threads'],201);self.assertEqual(row['undated'],82)
        self.assertEqual(fetch_one("SELECT created_at FROM posts WHERE post_id='11185'")['created_at'].strftime('%Y-%m-%d'),'2023-08-04')
        print('PASS: 201 uploaded threads, 154 posts, 154 non-identifying post labels, 82 unresolved thread dates, idempotent repeat import.')
if __name__=='__main__':unittest.main()

