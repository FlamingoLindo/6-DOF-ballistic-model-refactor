import numpy as np
import pandas as pd
from scipy.interpolate import interp1d, RectBivariateSpline
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CLASSE PARA INTERPOLAÇÃO DOS COEFICIENTES AERODINÂMICOS
# =============================================================================

class RealAerodynamicCoefficients:
    """
    Classe para carregar e interpolar coeficientes aerodinâmicos.
    Pré-Computa um grid 2D (Mach x alpha) para rodar mais rapidamente.
    """
    
    # TODO path
    def __init__(self, csv_path='C:\\Users\\DELL\\Downloads\\Coeficientes que vi 2 casas.csv'):
        """
        Carrega os coeficientes e pré-computa grid 2D.
        """
        print("\n" + "="*60)
        print("CARREGANDO COEFICIENTES AERODINÂMICOS (GRID 2D)")
        print("="*60)
        
        # Carregar arquivo Excel
        self.df = pd.read_excel(csv_path)
        print(f"✓ Arquivo carregado: {len(self.df)} pontos de Mach")
        print(f"  Faixa de Mach: {self.df['Match'].min():.2f} a {self.df['Match'].max():.2f}") # Observe que a tabela de coeficientes está esrcito "Match" errôneamente
        
        # Arrays de Mach da tabela
        mach_values = self.df['Match'].values
        self.mach_min = float(mach_values.min())
        self.mach_max = float(mach_values.max())
        
        # Lista de coeficientes (Detalhes encontrados no relatório)
        coeff_names = ['CX0', 'CX2', 'CNA', 'CMA', 'CPN', 'CYP', 
                      'CNPA', 'CNPA3', 'CNPA5', 'CPF1', 'CPF5', 
                      'CNPA-5', 'CMQ', 'CLP']
        
        # Pré-Computar grid 2D
        print("\nPré-computando grid 2D (Mach x Alpha)...")
        
        # Grid de Mach
        self.mach_grid = np.linspace(self.mach_min, self.mach_max, 100)
        
        # Grid de alpha: -10 a +10 graus (Escolha para otimizar, funciona adequadamente na faixa que estudaremos, possível problema para disparos semi-vertiais)
        self.alpha_grid = np.linspace(-np.radians(10), np.radians(10), 100)
        
        # Criar interpoladores 1D para cada coeficiente
        self.splines_1d = {}
        for col in coeff_names:
            if col in self.df.columns:
                self.splines_1d[col] = interp1d(
                    mach_values, 
                    self.df[col].values,
                    kind='cubic',
                    bounds_error=False,
                    fill_value=(self.df[col].values[0], self.df[col].values[-1])
                )
        
        # Pré-Computar todos os coeficientes base na grid de Mach
        self.grid_2d = {}
        for name, spline in self.splines_1d.items():
            self.grid_2d[name] = spline(self.mach_grid)
        
        # Pré-Computar coeficientes que dependem de alpha
        mach_mesh, alpha_mesh = np.meshgrid(self.mach_grid, self.alpha_grid, indexing='ij')
        
        print(f"  Grid: {len(self.mach_grid)} Machs x {len(self.alpha_grid)} alphas")
        print(f"  Range de alpha: [{np.degrees(self.alpha_grid[0]):.1f}°, {np.degrees(self.alpha_grid[-1]):.1f}°]")
        
        # Interpolar coeficientes base para a grid
        CX0_grid = np.zeros_like(mach_mesh)
        CX2_grid = np.zeros_like(mach_mesh)
        CNA_grid = np.zeros_like(mach_mesh)
        CNPA_grid = np.zeros_like(mach_mesh)
        CNPA3_grid = np.zeros_like(mach_mesh)
        CNPA5_grid = np.zeros_like(mach_mesh)
        
        for i, m in enumerate(self.mach_grid):
            if 'CX0' in self.grid_2d:
                CX0_grid[i, :] = self.grid_2d['CX0'][i]
            if 'CX2' in self.grid_2d:
                CX2_grid[i, :] = self.grid_2d['CX2'][i]
            if 'CNA' in self.grid_2d:
                CNA_grid[i, :] = self.grid_2d['CNA'][i]
            if 'CNPA' in self.grid_2d:
                CNPA_grid[i, :] = self.grid_2d['CNPA'][i]
            if 'CNPA3' in self.grid_2d:
                CNPA3_grid[i, :] = self.grid_2d['CNPA3'][i]
            if 'CNPA5' in self.grid_2d:
                CNPA5_grid[i, :] = self.grid_2d['CNPA5'][i]
        
        # Pré-Computar CD_total e CNP_total
        sin_alpha_mesh = np.sin(alpha_mesh)
        cos_alpha_mesh = np.cos(alpha_mesh)
        sin_alpha_2_mesh = np.sin(alpha_mesh)**2
        sin_alpha_3_mesh = sin_alpha_mesh**3
        sin_alpha_5th_mesh = sin_alpha_mesh**5
        
        # CX total (para uso no CLA)
        CX_total = CX0_grid + CX2_grid * sin_alpha_2_mesh
        
        # CD_total com o termo de CNA
        self.grid_2d['CD_total'] = CX_total*cos_alpha_mesh - (CNA_grid*sin_alpha_2_mesh)
        
        # CLA = CNA*cos(alpha) - CX
        self.grid_2d['CLA_total'] = CNA_grid * cos_alpha_mesh - CX_total
        
        self.grid_2d['CNP_total'] = (CNPA_grid * np.sign(alpha_mesh) +
                                      CNPA3_grid * sin_alpha_3_mesh+ 
                                      CNPA5_grid * sin_alpha_5th_mesh)
        
        
        # Criar interpoladores 2D
        self.interp_2d = {}
        self.interp_2d['CD_total'] = RectBivariateSpline(
            self.mach_grid, self.alpha_grid, self.grid_2d['CD_total'], kx=3, ky=3)
        self.interp_2d['CLA_total'] = RectBivariateSpline(
            self.mach_grid, self.alpha_grid, self.grid_2d['CLA_total'], kx=3, ky=3)
        self.interp_2d['CNP_total'] = RectBivariateSpline(
            self.mach_grid, self.alpha_grid, self.grid_2d['CNP_total'], kx=3, ky=3)
        
        # Coeficientes que não dependem 
        for name in ['CNA', 'CMA', 'CMQ', 'CLP', 'CYP']:
            if name in self.grid_2d:
                self.interp_2d[name] = interp1d(
                    self.mach_grid,
                    self.grid_2d[name],
                    kind='cubic',
                    bounds_error=False,
                    fill_value=(self.grid_2d[name][0], self.grid_2d[name][-1])
                )
        
        print("✓ Grid pré-computada com interpoladores prontos!")
        
    def get_coefficients(self, mach, alpha_rad=0.0):
        """
        Utilização dos coeficientes pré-computados
        """
        mach = np.clip(mach, self.mach_min, self.mach_max)
        alpha_rad = np.clip(alpha_rad, self.alpha_grid[0], self.alpha_grid[-1])
        
        coeffs = {}
        
        # Coeficientes que necessitam de alpha
        coeffs['CD_total'] = float(self.interp_2d['CD_total'](mach, alpha_rad))
        coeffs['CNP_total'] = float(self.interp_2d['CNP_total'](mach, alpha_rad))
        coeffs['CLA_total'] = float(self.interp_2d['CLA_total'](mach, alpha_rad))
        
        # Coeficientes fixos
        for name in ['CNA', 'CMA', 'CMQ', 'CLP', 'CYP']:
            if name in self.interp_2d:
                coeffs[name] = float(self.interp_2d[name](mach))
        
        return coeffs
