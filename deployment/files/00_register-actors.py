#!/usr/bin/env python3

import httpx
import json
from pathlib import Path
import asyncio

von_network_web_url = "http://ssi-cloud:9000"

seeds = {
    'authoritiesrepresentation': "authoritiesrepresentation0000000",
    'cloudagent': "cloudagent0000000000000000000000",
    'carcorp': "carcorp0000000000000000000000000",
    'dronecorp': "dronecorp00000000000000000000000",
    'edgeoperatoralpha': "edgeoperatoralpha000000000000000",
    'edgeoperatorbeta': "edgeoperatorbeta0000000000000000",
    'edgealpha': "edgealpha00000000000000000000000",
    'edgebeta': "edgebeta000000000000000000000000",
    'cartwin': "cartwin0000000000000000000000000",
    'dronetwin': "dronetwin00000000000000000000000",
    'car': "car00000000000000000000000000000",
    'drone': "drone000000000000000000000000000"
}

async def register():
    infos = {}

    async with httpx.AsyncClient() as client:
        for actor, seed in seeds.items():
            try:
                response = await client.post(
                    f"{von_network_web_url}/register",
                    json={
                        "seed": seed,
                        "role": "ENDORSER"
                    }
                )
                response.raise_for_status()
                print(response.json())
                infos[actor] = response.json()
            except httpx.HTTPStatusError as e:
                print(f"Error for {actor}: {e.response.status_code} - {e.response.text}")
                infos[actor] = {"error": str(e)}
            except Exception as e:
                print(f"Unhandled error for {actor}: {str(e)}")
                infos[actor] = {"error": str(e)}

    output_path = Path("actors.json")
    output_path.write_text(json.dumps(infos, indent=2))
    print(f"Results saved to {output_path.resolve()}")

# Run the async function
asyncio.run(register())
