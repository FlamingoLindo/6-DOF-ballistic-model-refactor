
import numpy as np
from math import sqrt, atan2
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CLASSE RESULTADO DA SIMULAÇÃO
# ================================================================  =============

class SimulationResults:
    """
    Classe que armazena e analisa os resultados de uma simulação balística.
    Gráficos no estilo 3Blue1Brown com fundo branco.
    """
    
    # Paleta de cores estilo 3Blue1Brown - FUNDO BRANCO
    COLORS = {
        'bg': '#FFFFFF',           # Fundo branco
        'primary': '#1A7FA0',      # Azul cyan mais escuro
        'secondary': '#2E5F7D',    # Azul esverdeado escuro
        'accent1': '#3BA3C7',      # Azul claro vibrante
        'accent2': '#1A5F7A',      # Azul petróleo
        'grid': '#D0D0D0',         # Grid visível mas suave
        'text': '#1A1A1A',         # Texto escuro
        'green': '#2E7D32',        # Verde escuro
        'red': '#C62828',          # Vermelho escuro
        'yellow': '#F9A825',       # Amarelo dourado
        'purple': '#6A1B9A',       # Roxo escuro
        'orange': '#EF6C00'        # Laranja escuro
    }
    
    def __init__(self, solution, simulator):
        """
        Inicializa o resultado da simulação.
        
        Parâmetros:
        -----------
        solution : OdeResult
            Resultado do scipy.integrate.solve_ivp
        simulator : BallisticSimulator
            O simulador que gerou estes resultados
        """
        self.solution = solution
        self.simulator = simulator
        
        # Extrair dados
        self.t = solution.t
        self.V1, self.V2, self.V3 = solution.y[0:3]
        self.h1, self.h2, self.h3 = solution.y[3:6]
        self.i1, self.i2, self.i3 = solution.y[6:9]
        self.x, self.y, self.z = solution.y[9:12]
        
        # Calcular grandezas derivadas
        self._calculate_derived_quantities()
    
    def _calculate_derived_quantities(self):
        """Calcula grandezas derivadas da trajetória."""
        # Velocidade total
        self.V_mag = np.sqrt(self.V1**2 + self.V2**2 + self.V3**2)
        
        # Mach
        self.mach = self.V_mag / self.simulator.environment.sound_speed
        
        # Momento angular total
        self.h_mag = np.sqrt(self.h1**2 + self.h2**2 + self.h3**2)
        
        # Spin rate
        self.spin_rate = []
        I_P = self.simulator.projectile.I_P
        I_T = self.simulator.projectile.I_T
        for idx in range(len(self.t)):
            h_dot_i = self.h1[idx]*self.i1[idx] + self.h2[idx]*self.i2[idx] + self.h3[idx]*self.i3[idx]
            omega1 = (I_T/I_P) * h_dot_i
            self.spin_rate.append(omega1)
        self.spin_rate = np.array(self.spin_rate)
        
        # Ângulo de ataque
        self.alpha_traj = []
        for idx in range(len(self.t)):
            v1 = self.V1[idx] - self.simulator.environment.W1
            v2 = self.V2[idx] - self.simulator.environment.W2
            v3 = self.V3[idx] - self.simulator.environment.W3
            v = sqrt(v1*v1 + v2*v2 + v3*v3) + 1e-12
            
            v_along = v1*self.i1[idx] + v2*self.i2[idx] + v3*self.i3[idx]
            v_perp1 = v1 - v_along*self.i1[idx]
            v_perp2 = v2 - v_along*self.i2[idx]
            v_perp3 = v3 - v_along*self.i3[idx]
            v_perp = sqrt(v_perp1**2 + v_perp2**2 + v_perp3**2)
            
            alpha = np.degrees(atan2(v_perp, v_along))
            self.alpha_traj.append(alpha)
        self.alpha_traj = np.array(self.alpha_traj)
        
        # Estatísticas
        self.alcance_max = float(self.x[-1])
        self.altura_max = float(np.max(self.y))
        self.desvio_lateral_max = float(np.max(np.abs(self.z)))
        self.tempo_voo = float(self.t[-1])
    
    def _setup_3b1b_style(self, ax, title=''):
        """Configura o estilo 3Blue1Brown para um eixo (fundo branco)."""
        ax.set_facecolor(self.COLORS['bg'])
        ax.grid(True, alpha=0.4, color=self.COLORS['grid'], linestyle='-', linewidth=0.8)
        ax.tick_params(colors=self.COLORS['text'], labelsize=10)
        ax.spines['bottom'].set_color(self.COLORS['text'])
        ax.spines['top'].set_color(self.COLORS['text']) 
        ax.spines['right'].set_color(self.COLORS['text'])
        ax.spines['left'].set_color(self.COLORS['text'])
        ax.spines['bottom'].set_linewidth(1.5)
        ax.spines['top'].set_linewidth(1.5)
        ax.spines['right'].set_linewidth(1.5)
        ax.spines['left'].set_linewidth(1.5)
        ax.xaxis.label.set_color(self.COLORS['text'])
        ax.yaxis.label.set_color(self.COLORS['text'])
        ax.title.set_color(self.COLORS['text'])
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    
    def print_statistics(self):
        """Imprime estatísticas da trajetória."""
        print(f"\n{'='*80}")
        print("ESTATÍSTICAS DA TRAJETÓRIA")
        print(f"{'='*80}")
        print(f"  Alcance: {self.alcance_max/1000:.2f} km")
        print(f"  Altura máxima: {self.altura_max/1000:.2f} km")
        print(f"  Desvio lateral: {self.desvio_lateral_max:.2f} m")
        print(f"  Tempo de voo: {self.tempo_voo:.2f} s")
        print(f"\nÂNGULO DE ATAQUE:")
        print(f"  Mínimo: {np.min(self.alpha_traj):.2f}°")
        print(f"  Máximo: {np.max(self.alpha_traj):.2f}°")
        print(f"  Médio: {np.mean(self.alpha_traj):.2f}°")
    
    def plot_trajectory_3d(self, save_path='01_trajectory_3d_white.png'):
        """Gráfico 1: Trajetória 3D completa."""
        fig = plt.figure(figsize=(12, 10), facecolor=self.COLORS['bg'])
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor(self.COLORS['bg'])
        
        # Trajetória
        ax.plot(self.x/1000, self.z, self.y/1000, 
                color=self.COLORS['primary'], linewidth=3, alpha=0.9)
        
        # Pontos de início e fim
        ax.scatter([0], [0], [0], c=self.COLORS['green'], 
                  s=200, marker='o', edgecolors=self.COLORS['text'], linewidths=2.5, label='Início')
        ax.scatter([self.x[-1]/1000], [self.z[-1]], [self.y[-1]/1000], 
                  c=self.COLORS['red'], s=200, marker='X', 
                  edgecolors=self.COLORS['text'], linewidths=2.5, label='Impacto')
        
        # Labels e título
        ax.set_xlabel('Alcance [km]', fontsize=12, fontweight='bold', 
                     color=self.COLORS['text'], labelpad=10)
        ax.set_ylabel('Deriva Lateral [m]', fontsize=12, fontweight='bold',
                     color=self.COLORS['text'], labelpad=10)
        ax.set_zlabel('Altitude [km]', fontsize=12, fontweight='bold',
                     color=self.COLORS['text'], labelpad=10)
        ax.set_title('Trajetória 3D Completa', fontsize=16, fontweight='bold', 
                    color=self.COLORS['text'], pad=20)
        
        # Estilo dos eixos
        ax.tick_params(colors=self.COLORS['text'])
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor(self.COLORS['grid'])
        ax.yaxis.pane.set_edgecolor(self.COLORS['grid'])
        ax.zaxis.pane.set_edgecolor(self.COLORS['grid'])
        ax.grid(True, alpha=0.3, color=self.COLORS['grid'])
        
        # Legenda
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          loc='upper left', fontsize=10, framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_top_view(self, save_path='02_top_view_white.png'):
        """Gráfico 2: Vista de cima (deriva lateral)."""
        fig, ax = plt.subplots(figsize=(14, 6), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Vista de Cima - Deriva Lateral')
        
        # Trajetória
        ax.plot(self.x/1000, self.z, color=self.COLORS['primary'], 
               linewidth=3, alpha=0.9)
        
        # Pontos
        ax.scatter([self.x[0]/1000], [self.z[0]], c=self.COLORS['green'], 
                  s=200, marker='o', edgecolors=self.COLORS['text'], 
                  linewidths=2.5, label='Início', zorder=5)
        ax.scatter([self.x[-1]/1000], [self.z[-1]], c=self.COLORS['red'], 
                  s=200, marker='X', edgecolors=self.COLORS['text'], 
                  linewidths=2.5, label='Impacto', zorder=5)
        
        # Linha de referência (sem deriva)
        ax.axhline(y=0, color=self.COLORS['yellow'], linestyle='--', 
                  alpha=0.7, linewidth=2, label='Referência (Z=0)')
        
        ax.set_xlabel('Alcance [km]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Deriva Lateral [m]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_side_view(self, save_path='03_side_view_white.png'):
        """Gráfico 3: Vista lateral (perfil vertical)."""
        fig, ax = plt.subplots(figsize=(14, 6), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Vista Lateral - Perfil Vertical')
        
        # Área sob a curva
        ax.fill_between(self.x/1000, 0, self.y/1000, 
                       alpha=0.15, color=self.COLORS['primary'])
        
        # Trajetória
        ax.plot(self.x/1000, self.y/1000, color=self.COLORS['primary'], 
               linewidth=3, alpha=0.9)
        
        # Pontos
        ax.scatter([self.x[0]/1000], [self.y[0]/1000], c=self.COLORS['green'], 
                  s=200, marker='o', edgecolors=self.COLORS['text'], 
                  linewidths=2.5, label='Início', zorder=5)
        ax.scatter([self.x[-1]/1000], [self.y[-1]/1000], c=self.COLORS['red'], 
                  s=200, marker='X', edgecolors=self.COLORS['text'], 
                  linewidths=2.5, label='Impacto', zorder=5)
        
        # Linha do solo
        ax.axhline(y=0, color=self.COLORS['text'], linestyle='-', 
                  alpha=0.8, linewidth=2.5, label='Nível do Solo')
        
        ax.set_xlabel('Alcance [km]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Altitude [km]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_velocity_vs_time(self, save_path='04_velocity_vs_time_white.png'):
        """Gráfico 4a: Velocidade vs Tempo."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Velocidade vs Tempo')
        
        ax.plot(self.t, self.V_mag, color=self.COLORS['primary'], 
               linewidth=3.5, label='|V| (Magnitude)', alpha=0.9)
        ax.plot(self.t, self.V1, color=self.COLORS['accent1'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='V₁ (Forward)')
        ax.plot(self.t, self.V2, color=self.COLORS['green'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='V₂ (Up)')
        ax.plot(self.t, self.V3, color=self.COLORS['purple'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='V₃ (Right)')
        
        ax.set_xlabel('Tempo [s]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Velocidade [m/s]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_velocity_vs_distance(self, save_path='05_velocity_vs_distance_white.png'):
        """Gráfico 4b: Velocidade vs Distância."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Velocidade vs Distância')
        
        ax.plot(self.x/1000, self.V_mag, color=self.COLORS['primary'], 
               linewidth=3.5, label='|V| (Magnitude)', alpha=0.9)
        ax.plot(self.x/1000, self.V1, color=self.COLORS['accent1'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='V₁ (Forward)')
        ax.plot(self.x/1000, self.V2, color=self.COLORS['green'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='V₂ (Up)')
        ax.plot(self.x/1000, self.V3, color=self.COLORS['purple'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='V₃ (Right)')
        
        ax.set_xlabel('Alcance [km]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Velocidade [m/s]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_axis_orientation_vs_time(self, save_path='06_axis_orientation_vs_time_white.png'):
        """Gráfico 5a: Orientação do eixo i' vs Tempo."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, "Evolução do Eixo Polar i' vs Tempo")
        
        ax.plot(self.t, self.i1, color=self.COLORS['red'], 
               linewidth=3, label="i'₁", alpha=0.9)
        ax.plot(self.t, self.i2, color=self.COLORS['green'], 
               linewidth=3, label="i'₂", alpha=0.9)
        ax.plot(self.t, self.i3, color=self.COLORS['accent1'], 
               linewidth=3, label="i'₃", alpha=0.9)
        
        ax.axhline(y=0, color=self.COLORS['text'], linestyle=':', 
                  linewidth=1.5, alpha=0.5)
        
        ax.set_xlabel('Tempo [s]', fontsize=12, fontweight='bold')
        ax.set_ylabel("Componentes de i'", fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=11, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_axis_orientation_vs_distance(self, save_path='07_axis_orientation_vs_distance_white.png'):
        """Gráfico 5b: Orientação do eixo i' vs Distância."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, "Evolução do Eixo Polar i' vs Distância")
        
        ax.plot(self.x/1000, self.i1, color=self.COLORS['red'], 
               linewidth=3, label="i'₁", alpha=0.9)
        ax.plot(self.x/1000, self.i2, color=self.COLORS['green'], 
               linewidth=3, label="i'₂", alpha=0.9)
        ax.plot(self.x/1000, self.i3, color=self.COLORS['accent1'], 
               linewidth=3, label="i'₃", alpha=0.9)
        
        ax.axhline(y=0, color=self.COLORS['text'], linestyle=':', 
                  linewidth=1.5, alpha=0.5)
        
        ax.set_xlabel('Alcance [km]', fontsize=12, fontweight='bold')
        ax.set_ylabel("Componentes de i'", fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=11, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_angular_momentum_vs_time(self, save_path='08_angular_momentum_vs_time_white.png'):
        """Gráfico 6a: Momento Angular vs Tempo."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Momento Angular vs Tempo')
        
        ax.plot(self.t, self.h_mag, color=self.COLORS['primary'], 
               linewidth=3.5, label='|h| (Magnitude)', alpha=0.9)
        ax.plot(self.t, self.h1, color=self.COLORS['red'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='h₁')
        ax.plot(self.t, self.h2, color=self.COLORS['green'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='h₂')
        ax.plot(self.t, self.h3, color=self.COLORS['accent1'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='h₃')
        
        ax.set_xlabel('Tempo [s]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Momento Angular [rad/s]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_angular_momentum_vs_distance(self, save_path='09_angular_momentum_vs_distance_white.png'):
        """Gráfico 6b: Momento Angular vs Distância."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Momento Angular vs Distância')
        
        ax.plot(self.x/1000, self.h_mag, color=self.COLORS['primary'], 
               linewidth=3.5, label='|h| (Magnitude)', alpha=0.9)
        ax.plot(self.x/1000, self.h1, color=self.COLORS['red'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='h₁')
        ax.plot(self.x/1000, self.h2, color=self.COLORS['green'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='h₂')
        ax.plot(self.x/1000, self.h3, color=self.COLORS['accent1'], 
               linewidth=2.5, linestyle='--', alpha=0.8, label='h₃')
        
        ax.set_xlabel('Alcance [km]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Momento Angular [rad/s]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_angle_of_attack_vs_time(self, save_path='10_angle_of_attack_vs_time_white.png'):
        """Gráfico 7a: Ângulo de Ataque vs Tempo."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Ângulo de Ataque vs Tempo')
        
        ax.plot(self.t, self.alpha_traj, color=self.COLORS['primary'], 
               linewidth=3, alpha=0.9)
        
        # Preencher áreas positivas e negativas
        ax.fill_between(self.t, 0, self.alpha_traj, 
                       where=(self.alpha_traj >= 0),
                       color=self.COLORS['green'], alpha=0.25, label='α positivo')
        ax.fill_between(self.t, 0, self.alpha_traj, 
                       where=(self.alpha_traj < 0),
                       color=self.COLORS['red'], alpha=0.25, label='α negativo')
        
        ax.axhline(y=0, color=self.COLORS['text'], linestyle=':', 
                  linewidth=1.5, alpha=0.6)
        
        ax.set_xlabel('Tempo [s]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ângulo de Ataque [°]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_angle_of_attack_vs_distance(self, save_path='11_angle_of_attack_vs_distance_white.png'):
        """Gráfico 7b: Ângulo de Ataque vs Distância."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Ângulo de Ataque vs Distância')
        
        ax.plot(self.x/1000, self.alpha_traj, color=self.COLORS['primary'], 
               linewidth=3, alpha=0.9)
        
        # Preencher áreas positivas e negativas
        ax.fill_between(self.x/1000, 0, self.alpha_traj, 
                       where=(self.alpha_traj >= 0),
                       color=self.COLORS['green'], alpha=0.25, label='α positivo')
        ax.fill_between(self.x/1000, 0, self.alpha_traj, 
                       where=(self.alpha_traj < 0),
                       color=self.COLORS['red'], alpha=0.25, label='α negativo')
        
        ax.axhline(y=0, color=self.COLORS['text'], linestyle=':', 
                  linewidth=1.5, alpha=0.6)
        
        ax.set_xlabel('Alcance [km]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ângulo de Ataque [°]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_mach_vs_time(self, save_path='12_mach_vs_time_white.png'):
        """Gráfico 8a: Número de Mach vs Tempo."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Número de Mach vs Tempo')
        
        ax.plot(self.t, self.mach, color=self.COLORS['purple'], 
               linewidth=3, alpha=0.9, label='Mach')
        
        ax.axhline(y=1.0, color=self.COLORS['red'], linestyle='--', 
                  alpha=0.8, linewidth=2.5, label='Mach 1 (Barreira do Som)')
        
        # Preencher regiões
        ax.fill_between(self.t, 0, self.mach, 
                       where=(self.mach >= 1.0),
                       color=self.COLORS['red'], alpha=0.15, label='Supersônico')
        ax.fill_between(self.t, 0, self.mach, 
                       where=(self.mach < 1.0),
                       color=self.COLORS['green'], alpha=0.15, label='Subsônico')
        
        ax.set_xlabel('Tempo [s]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Número de Mach', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_mach_vs_distance(self, save_path='13_mach_vs_distance_white.png'):
        """Gráfico 8b: Número de Mach vs Distância."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Número de Mach vs Distância')
        
        ax.plot(self.x/1000, self.mach, color=self.COLORS['purple'], 
               linewidth=3, alpha=0.9, label='Mach')
        
        ax.axhline(y=1.0, color=self.COLORS['red'], linestyle='--', 
                  alpha=0.8, linewidth=2.5, label='Mach 1 (Barreira do Som)')
        
        # Preencher regiões
        ax.fill_between(self.x/1000, 0, self.mach, 
                       where=(self.mach >= 1.0),
                       color=self.COLORS['red'], alpha=0.15, label='Supersônico')
        ax.fill_between(self.x/1000, 0, self.mach, 
                       where=(self.mach < 1.0),
                       color=self.COLORS['green'], alpha=0.15, label='Subsônico')
        
        ax.set_xlabel('Alcance [km]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Número de Mach', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_spin_rate_vs_time(self, save_path='14_spin_rate_vs_time_white.png'):
        """Gráfico 9a: Taxa de Spin vs Tempo."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Taxa de Spin vs Tempo')
        
        omega_spin_inicial = self.simulator.projectile.calculate_initial_spin(
            self.simulator.weapon.muzzle_velocity)
        
        ax.plot(self.t, self.spin_rate, color=self.COLORS['orange'], 
               linewidth=3, alpha=0.9, label='Spin Atual')
        
        ax.axhline(y=omega_spin_inicial, color=self.COLORS['yellow'], 
                  linestyle=':', alpha=0.8, linewidth=2.5, label='Spin Inicial')
        
        ax.set_xlabel('Tempo [s]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Taxa de Spin [rad/s]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_spin_rate_vs_distance(self, save_path='15_spin_rate_vs_distance_white.png'):
        """Gráfico 9b: Taxa de Spin vs Distância."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Taxa de Spin vs Distância')
        
        omega_spin_inicial = self.simulator.projectile.calculate_initial_spin(
            self.simulator.weapon.muzzle_velocity)
        
        ax.plot(self.x/1000, self.spin_rate, color=self.COLORS['orange'], 
               linewidth=3, alpha=0.9, label='Spin Atual')
        
        ax.axhline(y=omega_spin_inicial, color=self.COLORS['yellow'], 
                  linestyle=':', alpha=0.8, linewidth=2.5, label='Spin Inicial')
        
        ax.set_xlabel('Alcance [km]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Taxa de Spin [rad/s]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    
    def plot_altitude_vs_time(self, save_path='16_altitude_vs_time_white.png'):
        """Gráfico 10: Altura (Altitude) vs Tempo."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Altitude vs Tempo')
        
        # Área sob a curva
        ax.fill_between(self.t, 0, self.y/1000, 
                       alpha=0.15, color=self.COLORS['primary'])
        
        # Linha da altitude
        ax.plot(self.t, self.y/1000, color=self.COLORS['primary'], 
               linewidth=3, alpha=0.9, label='Altitude')
        
        # Ponto de altura máxima
        idx_max_alt = np.argmax(self.y)
        ax.scatter([self.t[idx_max_alt]], [self.y[idx_max_alt]/1000], 
                  c=self.COLORS['red'], s=200, marker='*', 
                  edgecolors=self.COLORS['text'], linewidths=2.5, 
                  label=f'Altura Máxima: {self.altura_max/1000:.2f} km', zorder=5)
        
        # Linha do solo
        ax.axhline(y=0, color=self.COLORS['text'], linestyle='-', 
                  alpha=0.8, linewidth=2.5, label='Nível do Solo')
        
        ax.set_xlabel('Tempo [s]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Altitude [km]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_lateral_drift_vs_time(self, save_path='17_lateral_drift_vs_time_white.png'):
        """Gráfico 11: Desvio Lateral vs Tempo."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Desvio Lateral vs Tempo')
        
        # Linha do desvio lateral
        ax.plot(self.t, self.z, color=self.COLORS['accent1'], 
               linewidth=3, alpha=0.9, label='Desvio Lateral (Z)')
        
        # Preencher área acima/abaixo de zero
        ax.fill_between(self.t, 0, self.z, 
                       where=(self.z >= 0),
                       color=self.COLORS['green'], alpha=0.2, label='Desvio positivo')
        ax.fill_between(self.t, 0, self.z, 
                       where=(self.z < 0),
                       color=self.COLORS['red'], alpha=0.2, label='Desvio negativo')
        
        # Linha de referência (sem deriva)
        ax.axhline(y=0, color=self.COLORS['yellow'], linestyle='--', 
                  alpha=0.7, linewidth=2, label='Referência (Z=0)')
        
        # Desvio máximo
        idx_max_z = np.argmax(np.abs(self.z))
        ax.scatter([self.t[idx_max_z]], [self.z[idx_max_z]], 
                  c=self.COLORS['purple'], s=200, marker='D', 
                  edgecolors=self.COLORS['text'], linewidths=2.5, 
                  label=f'Desvio Máx: {np.abs(self.z[idx_max_z]):.2f} m', zorder=5)
        
        ax.set_xlabel('Tempo [s]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Desvio Lateral [m]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_range_vs_time(self, save_path='18_range_vs_time_white.png'):
        """Gráfico 12: Alcance vs Tempo."""
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=self.COLORS['bg'])
        self._setup_3b1b_style(ax, 'Alcance vs Tempo')
        
        # Área sob a curva
        ax.fill_between(self.t, 0, self.x/1000, 
                       alpha=0.15, color=self.COLORS['secondary'])
        
        # Linha do alcance
        ax.plot(self.t, self.x/1000, color=self.COLORS['secondary'], 
               linewidth=3, alpha=0.9, label='Alcance (X)')
        
        # Ponto final (alcance máximo)
        ax.scatter([self.t[-1]], [self.x[-1]/1000], 
                  c=self.COLORS['red'], s=200, marker='X', 
                  edgecolors=self.COLORS['text'], linewidths=2.5, 
                  label=f'Alcance Final: {self.alcance_max/1000:.2f} km', zorder=5)
        
        ax.set_xlabel('Tempo [s]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Alcance [km]', fontsize=12, fontweight='bold')
        
        legend = ax.legend(facecolor=self.COLORS['bg'], edgecolor=self.COLORS['text'], 
                          fontsize=10, loc='best', framealpha=1)
        for text in legend.get_texts():
            text.set_color(self.COLORS['text'])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=200, facecolor=self.COLORS['bg'], bbox_inches='tight')
        print(f"✓ Gráfico salvo: {save_path}")
        plt.show()
    
    def plot_all_graphs(self):
        """Gera todos os gráficos individuais."""
        print("\n" + "="*80)
        print("GERANDO TODOS OS GRÁFICOS (ESTILO 3BLUE1BROWN - FUNDO BRANCO)")
        print("="*80)
        
        self.plot_trajectory_3d()
        self.plot_top_view()
        self.plot_side_view()
        self.plot_velocity_vs_time()
        self.plot_velocity_vs_distance()
        self.plot_axis_orientation_vs_time()
        self.plot_axis_orientation_vs_distance()
        self.plot_angular_momentum_vs_time()
        self.plot_angular_momentum_vs_distance()
        self.plot_angle_of_attack_vs_time()
        self.plot_angle_of_attack_vs_distance()
        self.plot_mach_vs_time()
        self.plot_mach_vs_distance()
        self.plot_spin_rate_vs_time()
        self.plot_spin_rate_vs_distance()
        
        # NOVOS GRÁFICOS
        self.plot_altitude_vs_time()
        self.plot_lateral_drift_vs_time()
        self.plot_range_vs_time()
        
        print("\n✓ Todos os gráficos foram gerados!")

