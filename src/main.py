import asyncio
import datetime

import aiohttp

from v209s_gateway import V209SGateway
from yaml_manager import Yaml


async def trade_information():
    gateway = V209SGateway(Yaml('amnor_client/src/config.yaml'))
    gateway.init_v209s_parameters()
    headers = {'content-type': 'application/json'}
    while True:
        try:
            _dict = {"data": await gateway.read()}
            if _dict.get('data'):
                print(datetime.datetime.now(), bytearray(_dict['data']).hex(' ').upper())
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.post(gateway.get_server_api_path(), headers=headers, json=_dict) as response:
                    _json = await response.json()
                    if _json.get('data'):
                        print(f"{datetime.datetime.now()} JSON:", _json)
                        if _json['description'].startswith('Set GW Call address to'):
                            gateway.set_call_address(bytearray(_json['data']).decode('utf-8'))
                            print('Call address was set')
                        elif _json['description'].startswith('Set GW Hops to '):
                            gateway.set_hops(_json['data'][0])
                            print('Hops was set')
                        elif _json['description'].startswith('Set GW Net to '):
                            gateway.set_net_id(_json['data'][0])
                            print('Net was set')
                        else:
                            await gateway.write(bytearray(_json['data']))
                            await asyncio.sleep(gateway.time_out*2*0.8)
                    else:
                        await asyncio.sleep(1)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(trade_information())
