
import numpy as np
from math import pi
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CLASSE PROJÉTIL (MUNIÇÃO)
# =============================================================================

class Projectiles:
    """
    Classe que representa um projétil naval com todas suas características físicas
    e balísticas.
    """
    
    def __init__(self, name="Projétil Naval", mass_kg=None, diameter_m=None,
                 I_P_kg_m2=None, I_T_kg_m2=None, rifling_twist_calibers=25.0):
        """
        Inicializa um projétil.
        
        Parâmetros:
        -----------
        name : str
            Nome/tipo do projétil
        mass_kg : float
            Massa em kg
        diameter_m : float
            Diâmetro em metros
        I_P_kg_m2 : float
            Momento de inércia polar em kg·m²
        I_T_kg_m2 : float
            Momento de inércia transversal em kg·m²
        rifling_twist_calibers : float
            Taxa de rifling em calibres por volta completa
        """
        self.name = name
        self.mass = mass_kg
        self.diameter = diameter_m
        self.I_P = I_P_kg_m2
        self.I_T = I_T_kg_m2
        self.rifling_twist = rifling_twist_calibers
        
        # Área de referência
        if diameter_m is not None:
            self.S = pi * (diameter_m / 2) ** 2
        else:
            self.S = None
    
    @classmethod
    def from_imperial(cls, name, mass_lb, diameter_in, I_P_lbin2, I_T_lbin2, 
                     rifling_twist_calibers=25.0):
        """
        Cria um projétil a partir de unidades imperiais.
        
        Parâmetros:
        -----------
        mass_lb : float
            Massa em libras
        diameter_in : float
            Diâmetro em polegadas
        I_P_lbin2 : float
            Momento de inércia polar em lb·in²
        I_T_lbin2 : float
            Momento de inércia transversal em lb·in²
        """
        LB_TO_KG = 0.453592
        IN_TO_M = 0.0254
        LBIN2_TO_KGM2 = LB_TO_KG * (IN_TO_M ** 2)
        
        mass_kg = mass_lb * LB_TO_KG
        diameter_m = diameter_in * IN_TO_M
        I_P_kg_m2 = I_P_lbin2 * LBIN2_TO_KGM2
        I_T_kg_m2 = I_T_lbin2 * LBIN2_TO_KGM2
        
        return cls(name, mass_kg, diameter_m, I_P_kg_m2, I_T_kg_m2, 
                  rifling_twist_calibers)
    
    def calculate_initial_spin(self, muzzle_velocity):
        """
        Calcula o spin inicial baseado no rifling do canhão.
        
        Parâmetros:
        -----------
        muzzle_velocity_mps : float
            Velocidade na boca do canhão em m/s
            
        Retorna:
        --------
        float : spin inicial em rad/s
        """
        n = self.rifling_twist
        p0 = (2 * np.pi * muzzle_velocity) / (n * self.diameter)
        return p0
    
    def get_info(self):
        """Retorna informações formatadas sobre o projétil."""
        info = f"\n{'='*60}\n"
        info += f"PROJÉTIL: {self.name}\n"
        info += f"{'='*60}\n"
        info += f"  Massa: {self.mass:.2f} kg\n"
        info += f"  Diâmetro: {self.diameter*1000:.1f} mm\n"
        info += f"  I_P: {self.I_P:.6f} kg·m²\n"
        info += f"  I_T: {self.I_T:.6f} kg·m²\n"
        info += f"  I_P/I_T: {self.I_P/self.I_T:.6f}\n"
        info += f"  Área de referência: {self.S:.6f} m²\n"
        info += f"  Rifling twist: {self.rifling_twist:.1f} calibres/volta\n"
        return info

