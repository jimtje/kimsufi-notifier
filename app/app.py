import os
import requests
import json
import time
import logging

from dotenv import load_dotenv
from WantedModels import WantedModels


def run():
    time_start = int(time.time())

    # HeathChecks start ping
    HEALTH_CHECK_URL = os.getenv('HEALTH_CHECK_URL')
    requests.get(HEALTH_CHECK_URL+ "/start")

    wanted_models = WantedModels(os.getenv('WANTED_MODELS'))

    # Get Data
    response = requests.get(os.getenv('API_URL'))
    models = json.loads(response.text)

    # Search for aviable wanted models
    aviable_models = {}
    for model in models:
        hardware_code = model["hardware"][-4:]

        if model["region"] == os.getenv('WANTED_REGION') and wanted_models.has_hardware(hardware_code):
            aviable = False
            for datacenter in model["datacenters"]:
                if (not datacenter["availability"] == 'unavailable'):
                    aviable = True
                    break

            if (aviable and not hardware_code in aviable_models.values()):
                key = wanted_models.get_key_by_hardware_code(hardware_code)
                aviable_models[key] = model["hardware"]

    # Notify
    if (len(aviable_models) > 0):
        NOTIFICATIONS_URL = os.getenv('NOTIFICATIONS_URL')
        EMAIL_FROM = os.getenv('EMAIL_FROM')
        KIMSUFI_BUY_URL = os.getenv('KIMSUFI_BUY_URL')

        headers = {
            'user-agent': 'kimsufi-notifier',
            'Content-Type': 'application/json',
            'X-Api-Key': os.getenv('NOTIFICATIONS_API_KEY')
        }

        # Get handlers from env
        handlers = os.getenv('NOTIFICATIONS_HANDLERS').split(',')
        handlers = map(lambda handler: handler.lower().strip(), handlers)
        handlers = list(handlers)

        # Send notification
        buffers_file = 'buffers.json'
        for key, hardware in aviable_models.items():
            if (is_to_notify(buffers_file, key)):
                payload = {
                    "handlers": handlers,
                    "emailFrom": EMAIL_FROM,
                    "subject": f"Kimsufi {key} Aviable!",
                    "message": f"The Kimsufi {key} server is aviable, grab it here: {KIMSUFI_BUY_URL}?reference={hardware}"
                }

                res = requests.post(
                    NOTIFICATIONS_URL,
                    headers=headers,
                    data=json.dumps(payload)
                )

                # If one notification succeeded save time to file
                res_data = res.json()
                if (res_data['oneSucceeded']):
                    save_notification_time(buffers_file, key)
    
    # HeathChecks end ping
    requests.get(HEALTH_CHECK_URL)

    # Wait interval
    enlapsed_time = int(time.time()) - time_start
    if(enlapsed_time < INTERVAL):
        time.sleep(INTERVAL-enlapsed_time)


def save_notification_time(buffers_file, key):
    with open(buffers_file, 'r+', encoding='utf-8') as json_file:
        # Load buffer dictionary
        buffers = {}
        if (len(json_file.read()) > 0):
            json_file.seek(0)
            buffers = json.load(json_file)

        # Save time
        buffers[key] = int(time.time())
        json_file.seek(0)
        json.dump(buffers, json_file, ensure_ascii=False, indent=4)


def is_to_notify(buffers_file, key):
    # Check if file exists
    if (not os.path.isfile(buffers_file)):
        open(buffers_file, 'a').close()
        return True

    # Read
    with open(buffers_file, 'r+', encoding='utf-8') as json_file:
        json_file.seek(0)
        buffers = json.load(json_file)

        if(not key in buffers):
            return True
        else:
            buffer_minutes = int(os.getenv('NOTIFICATIONS_BUFFER'))
            maxTime = time.time() - buffer_minutes*60

            return buffers[key] < maxTime


if __name__ == '__main__':
    load_dotenv()
    INTERVAL = int(os.getenv('INTERVAL'))

    while True:
        try:
            run()
        except Exception as e:
            # Handle all errors to avoid execution stop
            logging.exception(e)
