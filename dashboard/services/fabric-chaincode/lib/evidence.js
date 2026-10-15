'use strict';
const {Contract}=require('fabric-contract-api');
class Evidence extends Contract {
 async Anchor(ctx,evidenceId,digest,collectedAt){
  if(!/^[a-f0-9]{64}$/.test(digest)||!evidenceId||evidenceId.length>180||!Number.isFinite(Date.parse(collectedAt)))throw new Error('Invalid evidence metadata');
  if(ctx.clientIdentity.getAttributeValue('darktrace.writer')!=='true')throw new Error('Identity lacks darktrace.writer attribute');
  const key=ctx.stub.createCompositeKey('evidence',[evidenceId,digest]);const previous=await ctx.stub.getState(key);if(previous.length)return previous.toString();
  const value={evidenceId,digest,collectedAt,transactionId:ctx.stub.getTxID(),msp:ctx.clientIdentity.getMSPID(),writer:ctx.clientIdentity.getID(),committed:true};
  await ctx.stub.putState(key,Buffer.from(JSON.stringify(value)));ctx.stub.setEvent('EvidenceAnchored',Buffer.from(JSON.stringify({evidenceId,digest})));return JSON.stringify(value);
 }
 async Read(ctx,evidenceId,digest){const key=ctx.stub.createCompositeKey('evidence',[evidenceId,digest]);const value=await ctx.stub.getState(key);if(!value.length)throw new Error('Anchor not found');return value.toString();}
}
module.exports=Evidence;
