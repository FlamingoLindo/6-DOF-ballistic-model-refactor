from dataclasses import dataclass

# =============================================================================
# CLASSE AMBIENTE
# =============================================================================

@dataclass
class Environment:
    """
    Classe que define as condições ambientais da simulação.
    """
    rho: float = 1.225  # Densidade do ar [kg/m³]
    g: float = 9.81     # Aceleração da gravidade [m/s²]
    W1: float = 0.0     # Vento na direção x [m/s]
    W2: float = 0.0     # Vento na direção y [m/s]
    W3: float = 0.0     # Vento na direção z [m/s]
    sound_speed: float = 340.0  # Velocidade do som [m/s]

