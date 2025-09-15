from .models.ssi.agent import AgentConfig
import subprocess
import os
from acapy_controller import Controller
from acapy_controller.models import DIDResult
import httpx
import asyncio

script_dir = os.path.dirname(os.path.abspath(__file__))
genesis_path = os.path.join(script_dir, "bootstrap_data", "genesis.txt")

def create_agent_admin_url(agent_config: AgentConfig):
    return f"http://localhost:{agent_config.agent_admin_port}"

async def _check_agent_is_up(agent_admin_url: str):
    ctr = 0
    while ctr < 4:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(agent_admin_url)
        
                return response.status_code < 400
   
        except Exception as e:
            ctr += 1
            print("Agent is not ready, try again ...")
            await asyncio.sleep(0.5)
    
    return False

async def _create_agent_indy_did(agent_config: AgentConfig):
    try:
        agent_admin_url = create_agent_admin_url(agent_config)
        agent_controler = Controller(agent_admin_url)
        
        # Check if the DID is already published
        res = await agent_controler.get("/wallet/did/public", response=DIDResult)
        
        if res.result is None:
            
            # Create the DID            
            res = await agent_controler.post(
                "/did/indy/create",
                json={
                    "options": {
                        "did": agent_config.did,
                        "key_type": "ed25519",
                        "seed": agent_config.seed
                    }
                }
            )
            
            # Publish the DID
            res = await agent_controler.post(
                "/wallet/did/public",
                params={"did": agent_config.did}
            )              
        
    except Exception as e:
        print(e)

async def create_agent(agent_config: AgentConfig):
    cmd = [
        "aca-py",
        "start",
        "--endpoint",
        f"http://{agent_config.host}:{agent_config.agent_port}",
        "--label",
        agent_config.name,
        "--inbound-transport",
        "http",
        "0.0.0.0",
        str(agent_config.agent_port),
        "--outbound-transport",
        "http",
        "--admin",
        "0.0.0.0",
        str(agent_config.agent_admin_port),
        "--admin-insecure-mode",
        "--wallet-type",
        "askar",
        "--wallet-name",
        agent_config.name,
        "--wallet-key",
        agent_config.seed,
        "--preserve-exchange-records",
        "--auto-provision",
        "--ledger-pool-name",
        "testnet",
        "--genesis-file",
        genesis_path,
        "--trace-target",
        "log",
        "--trace-tag",
        "acapy.events",
        "--trace-label",
        "test.agent.trace",
        #"--auto-ping-connection",
        #"--auto-respond-messages",
        #"--auto-accept-invites",
        #"--auto-accept-requests",
        #"--auto-respond-credential-proposal",
        #"--auto-respond-credential-offer",
        #"--auto-respond-credential-request",
        #"--auto-store-credential",
        "--public-invites",
        "--requests-through-public-did",
    ]
    
    try:
        agent_process = subprocess.Popen(cmd)
        print(f"Started aca-py process with PID: {agent_process.pid}")

        agent_is_up = await _check_agent_is_up(create_agent_admin_url(agent_config))
        
        if agent_is_up:
            await _create_agent_indy_did(agent_config)
        else:
            agent_process.kill()
            raise Exception("Failed to create acapy-agent!!!")
        
        return agent_process
    
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        