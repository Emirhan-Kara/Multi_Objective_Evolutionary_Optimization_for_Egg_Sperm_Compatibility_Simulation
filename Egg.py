import random

import Config

class Egg:
    def __init__(self):
        # Fixed  HLA profile (6 alel)
        self.hla_profile = random.sample(Config.HLA_ALLELES, 6)

        # Ideal pH range
        self.ideal_ph_range = (7.2, 8.0)
