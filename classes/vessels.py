"""
_summary_

Returns:
    _type_: _description_
"""
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CLASSE EMBARCAÇÃO
# =============================================================================


class Vessels:
    """
    Classe que representa uma embarcação como um paralelepípedo.
    Preparada para simulações futuras envolvendo alvos móveis.
    """

    def __init__(self, name="Embarcação", center_position=(0.0, 0.0),
                 length=100.0, width=20.0, height=30.0,
                 velocity=(0.0, 0.0)):
        """
        Inicializa uma embarcação.

        Parâmetros:
        -----------
        name : str
            Nome da embarcação
        center_position : tuple (x, z)
            Posição do centro da embarcação (x=frente, z=direita)
        length : float
            Comprimento da embarcação em metros (eixo x)
        width : float
            Largura da embarcação em metros (eixo z)
        height : float
            Altura do casco em metros (eixo y)
        velocity : tuple (vx, vz)
            Velocidade da embarcação em m/s
        """
        self.name = name
        self.center = np.array(center_position, dtype=float)  # [x, z]
        self.length = length  # Comprimento (eixo x)
        self.width = width    # Largura (eixo z)
        self.height = height  # Altura (eixo y)
        self.velocity = np.array(velocity, dtype=float)  # [vx, vz]

    def get_bounds(self, time=0.0):
        """
        Retorna os limites da embarcação no espaço 3D no instante dado.

        Parâmetros:
        -----------
        time : float
            Tempo em segundos (para calcular posição com movimento)

        Retorna:
        --------
        dict : limites em x, y, z
        """
        # Posição atual considerando movimento
        current_center = self.center + self.velocity * time

        bounds = {
            'x_min': current_center[0] - self.length / 2,
            'x_max': current_center[0] + self.length / 2,
            'y_min': 0.0,  # Nível do mar
            'y_max': self.height,
            'z_min': current_center[1] - self.width / 2,
            'z_max': current_center[1] + self.width / 2
        }
        return bounds

    def check_impact(self, projectile_position, time=0.0, check_height=True):
        """
        Verifica se um projétil impactou a embarcação.

        Parâmetros:
        -----------
        projectile_position : array-like [x, y, z]
            Posição do projétil
        time : float
            Tempo atual
        check_height : bool
            Se True, verifica altura Y. Se False, ignora Y (útil para alvos no solo)

        Retorna:
        --------
        bool : True se houve impacto
        """
        bounds = self.get_bounds(time)
        x, y, z = projectile_position

        if check_height:
            impact = (bounds['x_min'] <= x <= bounds['x_max'] and
                      bounds['y_min'] <= y <= bounds['y_max'] and
                      bounds['z_min'] <= z <= bounds['z_max'])
        else:
            # Ignorar altura Y (para alvos no solo)
            impact = (bounds['x_min'] <= x <= bounds['x_max'] and
                      bounds['z_min'] <= z <= bounds['z_max'])

        return impact

    def get_info(self):
        """Retorna informações formatadas sobre a embarcação."""
        info = f"\n{'='*60}\n"
        info += f"EMBARCAÇÃO: {self.name}\n"
        info += f"{'='*60}\n"
        info += f"  Posição do centro (x, z): ({self.center[0]:.1f}, {self.center[1]:.1f}) m\n"
        info += f"  Dimensões (L×W×H): {self.length:.1f} × {self.width:.1f} × {self.height:.1f} m\n"
        info += f"  Velocidade (vx, vz): ({self.velocity[0]:.1f}, {self.velocity[1]:.1f}) m/s\n"
        return info
