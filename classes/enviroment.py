"""
Módulo responsável pela definição das condições ambientais da simulação.

Este módulo contém a classe `Environment`, utilizada para representar
parâmetros atmosféricos e condições externas que influenciam o comportamento
balístico do projétil, como densidade do ar, gravidade, vento e velocidade
do som.
"""

from dataclasses import dataclass

# =============================================================================
# CLASSE AMBIENTE
# =============================================================================


@dataclass
class Environment:
    """
    Representa as condições ambientais utilizadas na simulação balística.

    A classe armazena parâmetros físicos do ambiente, incluindo densidade
    do ar, gravidade, velocidade do vento nos três eixos e velocidade do som.

    Attributes
    ----------
    rho : float
        Densidade do ar em kg/m³.
    g : float
        Aceleração da gravidade em m/s².
    w1 : float
        Componente do vento no eixo x em m/s.
    w2 : float
        Componente do vento no eixo y em m/s.
    w3 : float
        Componente do vento no eixo z em m/s.
    sound_speed : float
        Velocidade do som no meio em m/s.
    """
    rho: float = 1.225  # Densidade do ar [kg/m³]
    g: float = 9.81     # Aceleração da gravidade [m/s²]
    w1: float = 0.0     # Vento na direção x [m/s]
    w2: float = 0.0     # Vento na direção y [m/s]
    w3: float = 0.0     # Vento na direção z [m/s]
    sound_speed: float = 340.0  # Velocidade do som [m/s]
