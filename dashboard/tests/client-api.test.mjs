import {readFileSync} from 'node:fs';
import ts from 'typescript';
import {strict as assert} from 'node:assert';
const source=ts.transpileModule(readFileSync('lib/client-api.ts','utf8'),{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
const {readApiResponse,apiRequest}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
assert.deepEqual(await readApiResponse(Response.json({records:[]})),{records:[]});
await assert.rejects(readApiResponse(new Response('<!DOCTYPE html><html>Session</html>',{headers:{'content-type':'text/html'}})),/page instead of workspace data/);
await assert.rejects(readApiResponse(new Response('<html>Sign in</html>',{status:401})),/Sign in again/);
await assert.rejects(readApiResponse(new Response('<html>Unavailable</html>',{status:502})),/temporarily unavailable/);
await assert.rejects(readApiResponse(new Response('{',{headers:{'content-type':'application/json'}})),/incomplete data/);
await assert.rejects(readApiResponse(Response.json({error:'Duplicate ID'},{status:400})),/Duplicate ID/);
const originalFetch=globalThis.fetch;let calls=0;
try{
 globalThis.fetch=async(url,opts)=>{calls++;assert.equal(opts.credentials,'same-origin');assert.equal(opts.cache,'no-store');assert.equal(opts.headers.Accept,'application/json');return new Response('<html>Error</html>',{status:503});};
 await assert.rejects(apiRequest('/api/actions',{action:'import'}),/temporarily unavailable/);
 assert.equal(calls,1,'Mutations must not be automatically replayed');
}finally{globalThis.fetch=originalFetch;}
console.log('PASS: JSON response, HTML/session/gateway recovery, malformed JSON, server errors, credentialed requests, no mutation replay.');
