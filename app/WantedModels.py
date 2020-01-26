
class WantedModels:

    hardware_codes = {
        "ks1": "sk12",
        "ks2": "sk13",
        "ks3": "sk14",
        "ks4": "sk15",
        "ks5": "sk16",
        "ks6": "sk17",
        "ks7": "sk18",
        "ks8": "sk19",
        "ks9": "sk20",
        "ks10": "sk21",
        "ks11": "sk22",
        "ks12": "sk23"
    }

    def __init__(self, wanted_models):

        input_keys = wanted_models.split(',')

        # Normalize and filter valid keys
        self.wanted_keys = []
        for key in input_keys:
            key = key.replace("-", "").lower().strip()

            if key in self.hardware_codes:
                self.wanted_keys.append(key)

    def has_hardware(self, hardware):
        for key in self.wanted_keys:
            if(hardware == self.hardware_codes[key]):
                return True

        return False

    def get_key_by_hardware_code(self, hardware_code):
        for key in self.wanted_keys:
            if (hardware_code == self.hardware_codes[key]):
                return key

        return False
