import {runnerGuard,claimJobs,finishJob} from '@/lib/operations';
import {fail} from '@/lib/server';
import {z} from 'zod';
export async function POST(req:Request){try{await runnerGuard(req);const text=await req.text();if(text.length>1200000)throw new Error('Payload exceeds limit');const b=JSON.parse(text);if(b.action==='claim')return Response.json({jobs:await claimJobs(),serverTime:new Date().toISOString()});if(b.action==='finish'){const p=z.object({sourceId:z.string(),leaseToken:z.string(),records:z.array(z.unknown()).max(100).nullable(),error:z.string().max(1000).nullable()}).parse(b);return Response.json(await finishJob(p.sourceId,p.leaseToken,p.records,p.error));}throw new Error('Unknown runner operation');}catch(e){return fail(e);}}
