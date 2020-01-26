import os
import requests
import json

from dotenv import load_dotenv
from WantedModels import WantedModels


def run():
    load_dotenv()

    WANTED_REGION = os.getenv('WANTED_REGION')
    wanted_models = WantedModels(os.getenv('WANTED_MODELS'))

    # Get Data
    response = requests.get(os.getenv('API_URL'))
    models = json.loads(response.text)

    # Search for aviable wanted models
    aviable_models = {}
    for model in models:
        hardware_code = model["hardware"][-4:]
        
        if model["region"] == WANTED_REGION and wanted_models.has_hardware(hardware_code):
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
        print("Notify")


if __name__ == '__main__':
    run()
