import numpy as np
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CLASSE ARMA
# =============================================================================

class Weapons:
    """
    Classe que representa uma arma (canhão) com suas características e posição.
    """
    
    def __init__(self, name="Canhão Naval", position=(0.0, 0.0, 0.0),
                 elevation_deg=45.0, azimuth_deg=0.0, rate_of_fire_rpm=15.0,
                 muzzle_velocity_mps=807.0, mounted_on_vessel=None):
        """
        Inicializa uma arma.
        
        Parâmetros:
        -----------
        name : str
            Nome/tipo da arma
        position : tuple (x, y, z)
            Posição da arma em metros RELATIVA à embarcação (x=frente, y=altura, z=direita)
        elevation_deg : float
            Elevação em graus
        azimuth_deg : float
            Azimute em graus
        rate_of_fire_rpm : float
            Taxa de tiro em tiros por minuto
        muzzle_velocity_mps : float
            Velocidade na boca em m/s
        mounted_on_vessel : Vessel, optional
            Embarcação na qual a arma está montada (None = arma em terra)
        """
        self.name = name
        self.position = np.array(position, dtype=float)  # [x, y, z] relativo à embarcação
        self.elevation = np.radians(elevation_deg)
        self.azimuth = np.radians(azimuth_deg)
        self.rate_of_fire = rate_of_fire_rpm
        self.muzzle_velocity = muzzle_velocity_mps
        self.mounted_on_vessel = mounted_on_vessel  # Referência à embarcação
    
    def set_firing_angles(self, elevation_deg, azimuth_deg):
        """Define os ângulos de tiro."""
        self.elevation = np.radians(elevation_deg)
        self.azimuth = np.radians(azimuth_deg)
    
    def get_absolute_position(self, time=0.0):
        """
        Retorna a posição absoluta da arma no espaço.
        Se montada em embarcação, considera movimento da embarcação.
        
        Parâmetros:
        -----------
        time : float
            Tempo em segundos (para calcular posição com movimento)
            
        Retorna:
        --------
        array : [x, y, z] posição absoluta em metros
        """
        if self.mounted_on_vessel is None:
            # Arma em terra - posição é absoluta
            return self.position.copy()
        else:
            # Arma montada em embarcação
            vessel_bounds = self.mounted_on_vessel.get_bounds(time)
            vessel_center_x = (vessel_bounds['x_min'] + vessel_bounds['x_max']) / 2
            vessel_center_z = (vessel_bounds['z_min'] + vessel_bounds['z_max']) / 2
            
            # Posição absoluta = posição do centro da embarcação + posição relativa da arma
            absolute_pos = np.array([
                vessel_center_x + self.position[0],
                self.position[1],  # Altura não muda
                vessel_center_z + self.position[2]
            ])
            return absolute_pos
    
    def get_velocity(self):
        """
        Retorna a velocidade da arma (velocidade da embarcação se montada).
        
        Retorna:
        --------
        array : [vx, vy, vz] velocidade em m/s
        """
        if self.mounted_on_vessel is None:
            # Arma em terra - velocidade zero
            return np.array([0.0, 0.0, 0.0])
        else:
            # Arma montada em embarcação - herda velocidade da embarcação
            return np.array([
                self.mounted_on_vessel.velocity[0],  # vx
                0.0,                                   # vy (embarcação não sobe/desce)
                self.mounted_on_vessel.velocity[1]   # vz
            ])
    
    def calculate_firing_angles(self):
        """
        Calcula os ângulos theta0 e phi0 conforme a convenção do simulador.
        
        Retorna:
        --------
        tuple : (theta0, phi0) em radianos
        """
        E = self.elevation # Elevação
        A = self.azimuth   # Azimutal
        
        theta0 = np.arcsin(np.cos(E) * np.sin(A))
        phi0 = np.arcsin(np.sin(E) / np.cos(theta0)) if np.cos(theta0) != 0 else np.pi/2
        
        return theta0, phi0
    
    def get_info(self):
        """Retorna informações formatadas sobre a arma."""
        info = f"\n{'='*60}\n"
        info += f"ARMA: {self.name}\n"
        info += f"{'='*60}\n"
        
        if self.mounted_on_vessel is None:
            info += f"  Posição (x, y, z): ({self.position[0]:.1f}, {self.position[1]:.1f}, {self.position[2]:.1f}) m\n"
            info += f"  Montada em: Terra (velocidade = 0)\n"
        else:
            abs_pos = self.get_absolute_position()
            vessel_vel = self.get_velocity()
            info += f"  Posição relativa (x, y, z): ({self.position[0]:.1f}, {self.position[1]:.1f}, {self.position[2]:.1f}) m\n"
            info += f"  Posição absoluta (x, y, z): ({abs_pos[0]:.1f}, {abs_pos[1]:.1f}, {abs_pos[2]:.1f}) m\n"
            info += f"  Montada em: {self.mounted_on_vessel.name}\n"
            info += f"  Velocidade da plataforma: ({vessel_vel[0]:.1f}, {vessel_vel[1]:.1f}, {vessel_vel[2]:.1f}) m/s\n"
        
        info += f"  Elevação: {np.degrees(self.elevation):.1f}°\n"
        info += f"  Azimute: {np.degrees(self.azimuth):.1f}°\n"
        info += f"  Taxa de tiro: {self.rate_of_fire:.1f} tiros/min\n"
        info += f"  Velocidade na boca: {self.muzzle_velocity:.1f} m/s\n"
        return info

