import {createRequire} from 'node:module';
import fs from 'node:fs/promises';
import {strict as assert} from 'node:assert';
const require=createRequire(import.meta.url);const wr=createRequire(require.resolve('wrangler/package.json'));const {Miniflare}=wr('miniflare');
const files=(await fs.readdir('dist/server',{recursive:true})).filter(p=>/\.m?js$/.test(p));const moduleNames=['index.js',...files.filter(p=>p!=='index.js')];
const modules=await Promise.all(moduleNames.map(async p=>({type:'ESModule',path:process.cwd()+'/dist/server/'+p,contents:await fs.readFile('dist/server/'+p,'utf8')})));
const mf=new Miniflare({modules,modulesRoot:process.cwd()+'/dist/server',compatibilityDate:'2026-05-15',compatibilityFlags:['nodejs_compat'],d1Databases:['DB'],bindings:{DARKTRACE_JOB_TOKEN:'integration-test-secret-at-least-32-characters',COLLECTOR_ALLOWED_HOSTS:'feed.example.org',...(process.env.REPOSITORY_API_URL?{REPOSITORY_API_URL:process.env.REPOSITORY_API_URL,REPOSITORY_API_KEY:process.env.REPOSITORY_API_KEY}:{})},cf:false});
try{
const db=await mf.getD1Database('DB');for(const file of (await fs.readdir('drizzle')).filter(f=>f.endsWith('.sql')).sort()){const sql=await fs.readFile('drizzle/'+file,'utf8');for(const stmt of sql.split('--> statement-breakpoint').map(x=>x.trim()).filter(Boolean))await db.prepare(stmt).run();}
const headers={'oai-authenticated-user-id':'test-user','Content-Type':'application/json'};
async function call(path,body){const res=await mf.dispatchFetch('http://example.test'+path,{method:body?'POST':'GET',headers,body:body?JSON.stringify(body):undefined});const text=await res.text();if(!res.ok)throw new Error(res.status+' '+text);return JSON.parse(text);}
let noAuth=await mf.dispatchFetch('http://example.test/api/workspace');assert.equal(noAuth.status,401);
await call('/api/actions',{action:'seed'});let data=await call('/api/workspace');assert.equal(data.records.length,7);assert.equal(data.relationships.length,4);
await call('/api/actions',{action:'seed'});assert.equal((await call('/api/workspace')).records.length,7);
const link=data.relationships[0];await call('/api/actions',{action:'review',relationshipId:link.id,decision:'accepted',reason:'Two identifier types match; retained as unverified lead.'});assert.equal((await call('/api/workspace')).reviews.length,1);
let c=await call('/api/actions',{action:'compare',a:'demo-ember-atlas',b:'demo-ember-harbor'});assert.equal(c.sufficient,false);
let v=await call('/api/actions',{action:'verify',id:'demo-ember-atlas'});assert.equal(v.valid,true);
await call('/api/actions',{action:'scanAll'});data=await call('/api/workspace');assert.equal(data.scans.filter(s=>s.status==='complete').length,3);
const sample=JSON.parse(await fs.readFile('public/sample-dataset.json','utf8'));await call('/api/actions',{action:'import',name:'Test import',authorized:true,records:sample});assert.equal((await call('/api/workspace')).records.length,8);
const duplicate=await mf.dispatchFetch('http://example.test/api/actions',{method:'POST',headers,body:JSON.stringify({action:'import',name:'Duplicate',authorized:true,records:sample})});assert.equal(duplicate.status,400);
for(const format of ['csv','json','pdf']){const r=await mf.dispatchFetch('http://example.test/api/export?q=ember&format='+format,{headers});assert.equal(r.status,200);const bytes=await r.text();assert(bytes.length>100);if(format==='json')assert.equal(JSON.parse(bytes).records.length,3);if(format==='pdf'){assert(bytes.startsWith('%PDF'));await fs.writeFile('/tmp/darktrace-report-test.pdf',bytes);}}
const source=await call('/api/operations',{action:'addSource',name:'Authorized test feed',url:'https://feed.example.org/data',adapter:'https-json',intervalSeconds:300,authorization:'Controlled integration fixture only'});
const runnerHeaders={'Content-Type':'application/json','x-darktrace-job-token':'integration-test-secret-at-least-32-characters'};
async function runner(body){const r=await mf.dispatchFetch('http://example.test/api/runner',{method:'POST',headers:runnerHeaders,body:JSON.stringify(body)});assert.equal(r.status,200,await r.clone().text());return r.json();}
const denied=await mf.dispatchFetch('http://example.test/api/runner',{method:'POST',headers,body:JSON.stringify({action:'claim'})});assert.equal(denied.status,400);
const jobs=await runner({action:'claim'});assert.equal(jobs.jobs.length,1);assert.equal((await runner({action:'claim'})).jobs.length,0);
const row={...sample[0],id:'versioned-test'};await runner({action:'finish',sourceId:source.id,leaseToken:jobs.jobs[0].lease_token,records:[row],error:null});
await call('/api/operations',{action:'queueSource',sourceId:source.id});const again=await runner({action:'claim'});await runner({action:'finish',sourceId:source.id,leaseToken:again.jobs[0].lease_token,records:[{...row,text:row.text+' A new observation.'}],error:null});
assert.equal((await call('/api/operations',{action:'history',id:source.id+'-'+row.id})).observations.length,2);
const model=await call('/api/operations',{action:'train',synthetic:true});assert.equal(model.metrics.testAuthors,2);assert(Number.isFinite(model.metrics.f1));
const prediction=await call('/api/operations',{action:'predict',a:'demo-ember-atlas',b:'demo-ember-harbor'});assert(prediction.score>=0&&prediction.score<=1);assert.equal(prediction.calibrated,false);
await call('/api/operations',{action:'candidates'});
await call('/api/operations',{action:'entity',name:'Fictional reference',kind:'Organization',source:'Controlled test reference',identifiers:[{type:'wallet',value:'DEMO-WALLET-7A'},{type:'pgp',value:'DEMO-PGP-8F21'}],synthetic:true});
let ops=await call('/api/operations');assert(ops.candidates.some(c=>c.confidence==='Medium'));assert.equal(ops.capabilities.fabricConfigured,false);
await call('/api/operations',{action:'sourcePolicy',sourceId:source.id,reliability:'Medium',reason:'Controlled integration test assessment'});
const ledger=await mf.dispatchFetch('http://example.test/api/operations',{method:'POST',headers,body:JSON.stringify({action:'anchor',id:'demo-ember-atlas'})});assert.equal(ledger.status,400);
console.log('PASS: collection authorization, exclusive job leases, versioned snapshots, model training/evaluation/prediction, entity correlation, source assessment, unconfigured ledger rejection.');
if(process.env.REPOSITORY_API_URL){
 const repository=await call('/api/repository');assert.equal(repository.configured,true);assert(repository.summary.total_posts>=22);assert(repository.personas.length>1);
 const preview=await call('/api/repository',{action:'snapshot',offset:0});assert.equal(preview.records.length,22);
 const imported=await call('/api/repository',{action:'import',offset:0});assert.equal(imported.count,22);
 const after=await call('/api/workspace');assert.equal(after.records.filter(r=>r.sourceId==='repository-postgresql').length,22);
 await call('/api/repository',{action:'import',offset:0});assert.equal((await call('/api/workspace')).records.length,after.records.length);
 const relationship=repository.relationships[0];await call('/api/repository',{action:'review',relationship_id:relationship.relationship_id,decision:'pending',reason:'Reviewed through compiled dashboard bridge; fictional data only.'});
 assert((await call('/api/repository')).reviews.length>=2);
 console.log('PASS: real FastAPI-to-dashboard proxy, original persona analysis, 22-record snapshot, idempotent evidence import, PostgreSQL review writeback.');
}else assert.equal((await call('/api/repository')).configured,false);
const root=await mf.dispatchFetch('http://example.test/',{headers});assert.equal(root.status,200);assert.match(await root.text(),/DarkTrace/);
const badOrigin=await mf.dispatchFetch('http://example.test/api/actions',{method:'POST',headers:{...headers,Origin:'http://attacker.test'},body:JSON.stringify({action:'seed'})});assert.equal(badOrigin.status,400);
console.log('PASS: auth boundary, seed idempotency, saved reviews, comparison, integrity, source scans, import, duplicate rejection, filtered CSV/JSON/PDF exports, root rendering, cross-origin rejection.');
} finally {await mf.dispose();}
