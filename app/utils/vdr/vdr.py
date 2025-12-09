from nacl.signing import SigningKey
from indy_vdr import ledger, open_pool
from ..utils import get_genesis_txns

async def change_verkey(seed: str, new_verkey: str, did: str) -> bool:
    pool = await open_pool(transactions=get_genesis_txns())

    request = ledger.build_nym_request(
        submitter_did=did,
        dest=did,
        verkey=new_verkey,
        alias=None,
        role="ENDORSER"
    )

    seed = seed.encode("utf-8")
    sk = SigningKey(seed)

    sig_input = request.signature_input
    signed = sk.sign(sig_input)
    signature_bytes = signed.signature
    request.set_signature(signature_bytes)
    
    try:
        response = await pool.submit_request(request)
        print("NYM transaction response:", response)

        return True
    
    except Exception as e:
        print("Error submitting NYM transaction:", e)
        return False
    finally:
        pool.close()