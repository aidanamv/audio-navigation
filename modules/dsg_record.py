# Affichage des valeurs du DSG à 5Hz

import argparse
from bleak import BleakClient
from bleak import _logger as logger
from bleak.uuids import uuid16_dict
import asyncio
from bluetooth import *
import time

uuid16_dict = {v: k for k, v in uuid16_dict.items()}
RSC_MEASUREMENT_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(uuid16_dict.get("RSC Measurement"))





def notification_handler(sender, data):
    filename = identifier + '.txt'
    file_path = os.path.join('/home/aidana/PycharmProjects/vat-capture/data_dsg', filename)
    with open(file_path, mode='a') as f:
        g = list(data)
        dsg = g[4] + (g[5] * 255)
        output = str(dsg) + ','
        timestamp = time.time()
        output += str(timestamp) + '\n'
        f.write(output)


async def run(address, debug=False):
    async with BleakClient(address) as client:
        x = await client.is_connected()
        logger.info("Connected: {0}".format(x))
        logger.info("collectiiiiiing")
        await client.start_notify(RSC_MEASUREMENT_UUID, notification_handler)
        await asyncio.sleep(100.0)
        await client.stop_notify(RSC_MEASUREMENT_UUID)


# ----------------------------------------------------------------------------------------------------------------------------------------

##### PROGRAMME PRINCIPAL #####




if __name__ == "__main__":
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--v', type=str, default='L1_right')
    args = parser.parse_args()
    identifier=args.v
    address = "8C:F6:81:75:17:46"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address, True))
