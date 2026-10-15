import http from 'node:http';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import * as grpc from '@grpc/grpc-js';
import {connect,signers} from '@hyperledger/fabric-gateway';
const required=['GATEWAY_TOKEN','FABRIC_PEER','FABRIC_TLS_CERT','FABRIC_CLIENT_CERT','FABRIC_CLIENT_KEY','FABRIC_MSP_ID','FABRIC_CHANNEL','FABRIC_CHAINCODE'];
for(const key of required)if(!process.env[key])throw new Error('Missing '+key);
if(process.env.GATEWAY_TOKEN.length<32)throw new Error('Gateway token must have at least 32 characters');
const client=new grpc.Client(process.env.FABRIC_PEER,grpc.credentials.createSsl(await fs.readFile(process.env.FABRIC_TLS_CERT)),process.env.FABRIC_TLS_SERVER_NAME?{'grpc.ssl_target_name_override':process.env.FABRIC_TLS_SERVER_NAME}:{});
const gateway=connect({client,identity:{mspId:process.env.FABRIC_MSP_ID,credentials:await fs.readFile(process.env.FABRIC_CLIENT_CERT)},signer:signers.newPrivateKeySigner(crypto.createPrivateKey(await fs.readFile(process.env.FABRIC_CLIENT_KEY))),evaluateOptions:()=>({deadline:Date.now()+10000}),endorseOptions:()=>({deadline:Date.now()+15000}),submitOptions:()=>({deadline:Date.now()+15000}),commitStatusOptions:()=>({deadline:Date.now()+20000})});
const contract=gateway.getNetwork(process.env.FABRIC_CHANNEL).getContract(process.env.FABRIC_CHAINCODE);
function auth(req){const supplied=req.headers.authorization||'';const expected='Bearer '+process.env.GATEWAY_TOKEN;return supplied.length===expected.length&&crypto.timingSafeEqual(Buffer.from(supplied),Buffer.from(expected));}
const server=http.createServer(async(req,res)=>{res.setHeader('Content-Type','application/json');if(!auth(req)){res.writeHead(401);res.end(JSON.stringify({error:'Unauthorized'}));return;}try{let body='';for await(const chunk of req){body+=chunk;if(body.length>4096)throw new Error('Payload too large');}const b=JSON.parse(body||'{}');if(!/^[a-f0-9]{64}$/.test(b.digest)||typeof b.evidenceId!=='string')throw new Error('Invalid evidence');let bytes;if(req.method==='POST'&&req.url==='/anchor')bytes=await contract.submitTransaction('Anchor',b.evidenceId,b.digest,b.collectedAt);else if(req.method==='POST'&&req.url==='/verify')bytes=await contract.evaluateTransaction('Read',b.evidenceId,b.digest);else{res.writeHead(404);res.end('{}');return;}const receipt=JSON.parse(new TextDecoder().decode(bytes));res.end(JSON.stringify(receipt));}catch(e){res.writeHead(502);res.end(JSON.stringify({error:'Ledger operation failed',detail:e.message}));}});
server.listen(Number(process.env.PORT||8081),'0.0.0.0');
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>server.close(()=>{gateway.close();client.close();process.exit(0);}));
