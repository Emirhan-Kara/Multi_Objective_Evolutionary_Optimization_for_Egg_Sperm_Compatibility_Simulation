import random
import copy

from Config import *
import Egg

"""class Sperm:
    def __init__(self):
        # Karar değişkenleri (genetik + biyolojik)
        self.hla_profile = random.sample(HLA_ALLELES, random.randint(3, 6))
        self.dfi = random.uniform(0, 50)              # DNA hasarı (düşük istenir)
        self.motility = random.uniform(30, 100)       # Hareketlilik
        self.morphology = random.uniform(10, 100)     # Şekil
        self.velocity = random.uniform(10, 100)       # Hız
        self.ph_tolerance = random.uniform(6.5, 8.5)  # pH toleransı

        # Objective skorları (başlangıçta boş)
        self.objectives = [0.0, 0.0]  # [genetic_compatibility, biological_quality]

        self.rank = 0
        self.crowding_distance = 0.0

    def copy(self):
        return copy.deepcopy(self)

    def evaluate_objectives(self, egg: Egg):
        self.objectives[0] = self.genetic_compatibility(egg)
        self.objectives[1] = self.biological_quality()

    def genetic_compatibility(self, egg: Egg):
        # HLA benzerlik skoru
        hla_match = len(set(self.hla_profile) & set(egg.hla_profile)) / len(egg.hla_profile)

        # pH uyumu
        if egg.ideal_ph_range[0] <= self.ph_tolerance <= egg.ideal_ph_range[1]:
            ph_score = 1.0
        else:
            dist = min(abs(self.ph_tolerance - egg.ideal_ph_range[0]),
                       abs(self.ph_tolerance - egg.ideal_ph_range[1]))
            ph_score = max(0.0, 1 - dist)  # Normalize edilmiş ters fark

        # Toplam genetik uyum skoru
        return round(0.8 * hla_match + 0.2 * ph_score, 5)

    def biological_quality(self):
        # Değişkenlerin olası min-max aralıkları
        motility_range = (30, 100)
        morphology_range = (10, 100)
        velocity_range = (10, 100)
        dfi_range = (0, 50)

        # Normalize edilmiş değerler
        motility_norm = (self.motility - motility_range[0]) / (motility_range[1] - motility_range[0])
        morphology_norm = (self.morphology - morphology_range[0]) / (morphology_range[1] - morphology_range[0])
        velocity_norm = (self.velocity - velocity_range[0]) / (velocity_range[1] - velocity_range[0])
        dfi_norm = (self.dfi - dfi_range[0]) / (dfi_range[1] - dfi_range[0])

        # Ağırlıklı skor (DFI ters etkili)
        score = (
            0.3 * motility_norm +
            0.25 * morphology_norm +
            0.15 * velocity_norm +
            0.3 * (1 - dfi_norm)  # düşük DFI = yüksek skor
        )

        return round(score, 5)

"""



class Sperm:
    def __init__(self):
        # Total resource budget (fixed)
        self.total_resources = 100
        
        # Resource allocation (must sum to total_resources)
        self.genetic_resources = random.uniform(10, 90)
        self.biological_resources = self.total_resources - self.genetic_resources
        
        # HLA profile size depends on genetic resources
        max_hla = min(6, max(2, int(self.genetic_resources / 15)))
        self.hla_profile = random.sample(HLA_ALLELES, random.randint(2, max_hla))
        
        # Biological parameters depend on biological resources
        resource_factor = self.biological_resources / 100
        self.dfi = random.uniform(0, 50) * (2 - resource_factor)
        self.motility = random.uniform(30, 100) * resource_factor
        self.morphology = random.uniform(10, 100) * resource_factor
        self.velocity = random.uniform(10, 100) * resource_factor
        self.ph_tolerance = random.uniform(6.5, 8.5)

        self.objectives = [0.0, 0.0]
        self.rank = 0
        self.crowding_distance = 0.0

    def copy(self):
        return copy.deepcopy(self)

    def evaluate_objectives(self, egg: Egg, generation_number=0, C=DYNAMIC_PENALTY_FACTOR_C, alpha=DYNAMIC_PENALTY_FACTOR_ALPHA, beta=DYNAMIC_PENALTY_FACTOR_BETA):
        # Calculate objective functions
        genetic_compat = self.genetic_compatibility(egg)
        bio_quality = self.biological_quality()

        # Calculate penalty (g(x) = CONSTRAINT - genetic_compatibility)
        g_violation = max(0.0, CONSTRAINT - genetic_compat)
        penalty = (C * (generation_number ** alpha)) * (g_violation ** beta)

        # Penalzied fitness for objective 1
        penalized_compat = genetic_compat - penalty

        self.objectives[0] = max(0.0, penalized_compat)
        self.objectives[1] = bio_quality


    def genetic_compatibility(self, egg: Egg):
        # HLA match improves with more genetic resources
        hla_match = len(set(self.hla_profile) & set(egg.hla_profile)) / len(egg.hla_profile)
        
        resource_factor = self.genetic_resources / 100
        
        # pH compatibility
        if egg.ideal_ph_range[0] <= self.ph_tolerance <= egg.ideal_ph_range[1]:
            ph_score = 1.0
        else:
            dist = min(abs(self.ph_tolerance - egg.ideal_ph_range[0]),
                       abs(self.ph_tolerance - egg.ideal_ph_range[1]))
            ph_score = max(0.0, 1 - dist)
        
        # Final score with resource influence
        score = (0.7 * hla_match + 0.3 * ph_score) * (0.3 + 0.7 * resource_factor)
        return round(max(0, min(1, score)), 5)

    def biological_quality(self):
        # Biological quality directly depends on biological resources
        resource_factor = self.biological_resources / 100
        
        # Normalized parameters
        motility_norm = max(0, min(1, self.motility / 100))
        morphology_norm = max(0, min(1, self.morphology / 100))
        velocity_norm = max(0, min(1, self.velocity / 100))
        dfi_norm = max(0, min(1, 1 - self.dfi / 50))
        
        # Base score
        base_score = (
            0.3 * motility_norm +
            0.25 * morphology_norm +
            0.15 * velocity_norm +
            0.3 * dfi_norm
        )
        
        # Apply resource constraint
        score = base_score * (0.2 + 0.8 * resource_factor)
        return round(max(0, min(1, score)), 5)