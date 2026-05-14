"""
_summary_

Returns:
_type_: _description_
"""

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
                 i_p_kg_m2=None, i_t_kg_m2=None, rifling_twist_calibers=25.0):
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
        i_p_kg_m2 : float
            Momento de inércia polar em kg·m²
        i_t_kg_m2 : float
            Momento de inércia transversal em kg·m²
        rifling_twist_calibers : float
            Taxa de rifling em calibres por volta completa
        """
        self.name = name
        self.mass = mass_kg
        self.diameter = diameter_m
        self.i_p = i_p_kg_m2
        self.i_t = i_t_kg_m2
        self.rifling_twist = rifling_twist_calibers

        # Área de referência
        if diameter_m is not None:
            self.s = pi * (diameter_m / 2) ** 2
        else:
            self.s = None

    @classmethod
    def from_imperial(cls, name, mass_lb, diameter_in, i_p_lbin2, i_t_lbin2,
                      rifling_twist_calibers=25.0):
        """
        Cria um projétil a partir de unidades imperiais.

        Parâmetros:
        -----------
        mass_lb : float
            Massa em libras
        diameter_in : float
            Diâmetro em polegadas
        i_p_lbin2 : float
            Momento de inércia polar em lb·in²
        i_t_lbin2 : float
            Momento de inércia transversal em lb·in²
        """
        lb_to_kg = 0.453592
        in_to_m = 0.0254
        lbin2_to_kgm2 = lb_to_kg * (in_to_m ** 2)

        mass_kg = mass_lb * lb_to_kg
        diameter_m = diameter_in * in_to_m
        i_p_kg_m2 = i_p_lbin2 * lbin2_to_kgm2
        i_t_kg_m2 = i_t_lbin2 * lbin2_to_kgm2

        return cls(name, mass_kg, diameter_m, i_p_kg_m2, i_t_kg_m2,
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
        info += f"  i_p: {self.i_p:.6f} kg·m²\n"
        info += f"  i_t: {self.i_t:.6f} kg·m²\n"
        info += f"  i_p/i_t: {self.i_p/self.i_t:.6f}\n"
        info += f"  Área de referência: {self.s:.6f} m²\n"
        info += f"  Rifling twist: {self.rifling_twist:.1f} calibres/volta\n"
        return info
