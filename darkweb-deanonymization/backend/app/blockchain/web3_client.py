"""Optional Ethereum client. Configuration is checked only on ledger requests."""
import json
import os
from functools import lru_cache
from pathlib import Path
from web3 import Web3

@lru_cache(maxsize=1)
def get_context():
    values={k:os.getenv(k) for k in ('LOCAL_RPC_URL','LOCAL_PRIVATE_KEY','CONTRACT_ADDRESS')}
    if not all(values.values()):
        raise RuntimeError('Ethereum is not configured; set LOCAL_RPC_URL, LOCAL_PRIVATE_KEY and CONTRACT_ADDRESS')
    w3=Web3(Web3.HTTPProvider(values['LOCAL_RPC_URL'],request_kwargs={'timeout':10}))
    if not w3.is_connected(): raise RuntimeError('Ethereum RPC is unavailable')
    artifact=Path(__file__).resolve().parents[3]/'blockchain/artifacts/contracts/EvidenceRegistry.sol/EvidenceRegistry.json'
    if not artifact.is_file(): raise RuntimeError('Compile the Ethereum contract to generate its ABI')
    contract=w3.eth.contract(address=Web3.to_checksum_address(values['CONTRACT_ADDRESS']),abi=json.loads(artifact.read_text())['abi'])
    return w3,w3.eth.account.from_key(values['LOCAL_PRIVATE_KEY']),contract

def get_contract(): return get_context()[2]

def get_blockchain_status():
    if not all(os.getenv(k) for k in ('LOCAL_RPC_URL','LOCAL_PRIVATE_KEY','CONTRACT_ADDRESS')):
        return {'configured':False,'connected':False,'message':'Optional Ethereum integration is not configured'}
    w3,account,contract=get_context()
    return {'configured':True,'connected':w3.is_connected(),'chain_id':w3.eth.chain_id,'account':account.address,'contract_address':contract.address}
