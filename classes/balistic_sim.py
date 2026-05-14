"""
_summary_

Returns:
    _type_: _description_    
"""

import numpy as np
from math import sqrt, sin, cos, acos
from scipy.integrate import solve_ivp
from classes.sim_results import SimulationResults

import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CLASSE SIMULADOR BALÍSTICO
# =============================================================================


class BallisticSimulator:
    """
    Classe principal que gerencia a simulação balística 6-DOF.
    """

    def __init__(self, projectile, weapon, environment, aero_coeffs):
        """
        Inicializa o simulador.

        Parâmetros:
        -----------
        projectile : Projectile
            Objeto projétil
        weapon : Weapon
            Objeto arma
        environment : Environment
            Condições ambientais
        aero_coeffs : RealAerodynamicCoefficients
            Coeficientes aerodinâmicos
        """
        self.projectile = projectile
        self.weapon = weapon
        self.environment = environment
        self.aero_coeffs = aero_coeffs

        # Resultado da simulação
        self.result = None

    def build_initial_conditions(self, alpha0_deg=0.0, beta0_deg=0.0,
                                 w_j0=5.0, w_k0=5.0):
        """
        Constrói condições iniciais para a simulação.
        IMPORTANTE: Considera a velocidade da embarcação se a arma estiver montada em uma.

        Parâmetros:
        -----------
        alpha0_deg : float
            Ângulo de arfagem inicial em graus
        beta0_deg : float
            Ângulo de guinada inicial em graus
        w_j0 : float
            Velocidade angular em j' [rad/s]
        w_k0 : float
            Velocidade angular em k' [rad/s]

        Retorna:
        --------
        array : vetor de estado inicial [V1, V2, V3, h1, h2, h3, i1, i2, i3, x, y, z]
        """
        # Ângulos de tiro
        theta0, phi0 = self.weapon.calculate_firing_angles()
        alpha0 = np.radians(alpha0_deg)
        beta0 = np.radians(beta0_deg)

        # Velocidade inicial DO PROJÉTIL RELATIVA À ARMA (velocidade na boca)
        v0 = self.weapon.muzzle_velocity
        v1_rel = v0 * cos(theta0) * cos(phi0)
        v2_rel = v0 * cos(theta0) * sin(phi0)
        v3_rel = v0 * sin(theta0)

        # Velocidade da plataforma (embarcação)
        platform_velocity = self.weapon.get_velocity()

        # VELOCIDADE ABSOLUTA = Velocidade relativa + Velocidade da plataforma
        v1_0 = v1_rel + platform_velocity[0]
        v2_0 = v2_rel + platform_velocity[1]
        v3_0 = v3_rel + platform_velocity[2]

        # Spin inicial
        w_i0 = self.projectile.calculate_initial_spin(v0)

        # print(f"\n1. Velocidade inicial:")
        # if np.any(platform_velocity != 0):
        #     print(f"   Velocidade relativa (à arma): [{V1_rel:.2f},
        # \{V2_rel:.2f}, {V3_rel:.2f}] m/s")
        #     print(f"   Velocidade da plataforma: [{platform_velocity[0]:.2f},
        # \{platform_velocity[1]:.2f}, {platform_velocity[2]:.2f}] m/s")
        #     print(f"   Velocidade ABSOLUTA: [{V1_0:.2f}, {V2_0:.2f}, {V3_0:.2f}] m/s")
        # else:
        #     print(f"   V = [{V1_0:.2f}, {V2_0:.2f}, {V3_0:.2f}] m/s (plataforma estacionária)")
        # print(f"   |V| = {sqrt(V1_0**2 + V2_0**2 + V3_0**2):.2f} m/s")

        # Eixo polar i'
        phi_eff = phi0 + alpha0
        theta_eff = theta0 + beta0

        i1_0 = cos(phi_eff) * cos(theta_eff)
        i2_0 = cos(theta_eff) * sin(phi_eff)
        i3_0 = sin(theta_eff)

        # print(f"\n2. Eixo polar i':")
        # print(f"   φ_eff = {np.degrees(phi0):.2f}° +\
        # {np.degrees(alpha0):.2f}° = {np.degrees(phi_eff):.2f}°")
        # print(f"   θ_eff = {np.degrees(theta0):.2f}° +\
        # {np.degrees(beta0):.2f}° = {np.degrees(theta_eff):.2f}°")
        # print(f"   i' = [{i1_0:.6f}, {i2_0:.6f}, {i3_0:.6f}]")

        # Eixos j' e k'
        q = sin(theta_eff)**2 + cos(theta_eff)**2 * cos(phi_eff)**2
        sqrt_q = sqrt(q)

        # j1_0 = -(sin(phi_eff) * cos(phi_eff) * cos(theta_eff)**2) / sqrt_q
        # j2_0 = (cos(theta_eff)**2 * cos(phi_eff)
        #         ** 2 + sin(theta_eff)**2) / sqrt_q
        # j3_0 = -(sin(theta_eff) * cos(theta_eff) * sin(phi_eff)) / sqrt_q

        # k1_0 = -sin(theta_eff) / sqrt_q
        # k2_0 = 0.0
        # k3_0 = (cos(phi_eff) * cos(theta_eff)) / sqrt_q

        # di'/dt
        di1_dt = (w_j0 * sin(theta_eff) -
                  w_k0 * cos(theta_eff)**2 * sin(phi_eff) * cos(phi_eff)) / sqrt_q

        di2_dt = (w_k0 / sqrt_q) * (cos(theta_eff)**2 * cos(phi_eff)**2 +
                                    sin(theta_eff)**2)

        di3_dt = (-w_j0 * cos(theta_eff) * cos(phi_eff)
                  - w_k0 * sin(phi_eff) * cos(theta_eff) * sin(theta_eff)) / sqrt_q

        # Momento angular h
        omega1_inertial = w_i0

        i_p = self.projectile.i_p
        i_t = self.projectile.i_t

        term1_h1 = (i_p / i_t) * omega1_inertial * i1_0
        term1_h2 = (i_p / i_t) * omega1_inertial * i2_0
        term1_h3 = (i_p / i_t) * omega1_inertial * i3_0

        term2_h1 = i2_0 * di3_dt - i3_0 * di2_dt
        term2_h2 = i3_0 * di1_dt - i1_0 * di3_dt
        term2_h3 = i1_0 * di2_dt - i2_0 * di1_dt

        h1_0 = term1_h1 + term2_h1
        h2_0 = term1_h2 + term2_h2
        h3_0 = term1_h3 + term2_h3

        # print(f"\n3. Momento angular h:")
        # print(f"   h = [{h1_0:.6f}, {h2_0:.6f}, {h3_0:.6f}] rad/s")

        # # Verificação
        # h_dot_i = h1_0*i1_0 + h2_0*i2_0 + h3_0*i3_0
        # expected = (I_P / I_T) * omega1_inertial
        # print(f"   Verificação h·i' = {h_dot_i:.6f} vs esperado = {expected:.6f}")

        # Posição inicial (posição absoluta da arma)
        abs_position = self.weapon.get_absolute_position()
        x0, y0, z0 = abs_position

        # Monta vetor de estado
        y0_vec = np.array([v1_0, v2_0, v3_0,
                           h1_0, h2_0, h3_0,
                           i1_0, i2_0, i3_0,
                           x0, y0, z0], dtype=float)

        return y0_vec

    def rhs(self, _t, y):
        """
        Lado direito das equações diferenciais (RHS).

        Parâmetros:
        -----------
        t : float
            Tempo
        y : array
            Vetor de estado [V1, V2, V3, h1, h2, h3, i1, i2, i3, x, y, z]

        Retorna:
        --------
        array : derivadas do vetor de estado
        """
        v1, v2, v3, h1, h2, h3, i1, i2, i3, _x, _ypos, _z = y

        # Velocidade relativa (com vento)
        v1 = v1 - self.environment.W1
        v2 = v2 - self.environment.W2
        v3 = v3 - self.environment.W3
        v = sqrt(v1*v1 + v2*v2 + v3*v3)

        # Número de Mach
        mach = v / self.environment.sound_speed

        # Ângulo de ataque
        cos_alpha_t = (v1*i1 + v2*i2 + v3*i3) / v
        cos_alpha_t = np.clip(cos_alpha_t, -1.0, 1.0)
        alpha_rad = acos(cos_alpha_t)

        # Obter coeficientes aerodinâmicos
        coeffs = self.aero_coeffs.get_coefficients(mach, alpha_rad)

        c_d = coeffs['CD_total']  # Drag Force Coefficient
        c_lalpha = coeffs['CLA_total']  # Lift Force Coefficient
        c_npalpha = coeffs['CYP']  # Magnus Force Coefficient
        c_nq = 0  # Pitching Dumping Force Coefficient
        # Pitching Dumping Force Coefficient (segunda componente)
        c_nalpha_dot = 0
        c_lp = coeffs['CLP']  # Spin Dumping Moment Coefficient
        c_malpha = coeffs['CMA']  # Pitching Moment Coefficient
        c_mpalpha = coeffs['CNP_total']  # Magnus Moment Coefficient
        c_mq = coeffs['CMQ']  # Pitching Dumping Moment Coefficient
        c_malpha_dot = 0

        c_l_delta = 0.0
        delta_f = 0.0

        # Parâmetros do projétil e ambiente
        m = self.projectile.mass
        s = self.projectile.s
        d = self.projectile.diameter
        i_p = self.projectile.i_p
        i_t = self.projectile.i_t
        rho = self.environment.rho
        g = self.environment.g

        # ω₁ = (I_T/I_P) (h · i')
        h_dot_i = h1*i1 + h2*i2 + h3*i3
        omega1 = (i_t/i_p) * h_dot_i

        # Equações de força (dV/dt)
        dv1 = (
            - (rho*v*s*c_d)/(2*m) * v1
            + (rho*s*c_lalpha)/(2*m) * ((v*v)*i1 - v*v1*cos_alpha_t)
            - (rho*s*d*c_npalpha*omega1)/(2*m) * (v3*i2 - v2*i3)
            + (rho*v*s*d*(c_nq + c_nalpha_dot))/(2*m) * (h2*i3 - h3*i2)
        )
        dv2 = (
            - (rho*v*s*c_d)/(2*m) * v2
            + (rho*s*c_lalpha)/(2*m) * ((v*v)*i2 - v*v2*cos_alpha_t)
            - (rho*s*d*c_npalpha*omega1)/(2*m) * (v1*i3 - v3*i1)
            + (rho*v*s*d*(c_nq + c_nalpha_dot))/(2*m) * (h3*i1 - h1*i3)
            - g
        )
        dv3 = (
            - (rho*v*s*c_d)/(2*m) * v3
            + (rho*s*c_lalpha)/(2*m) * ((v*v)*i3 - v*v3*cos_alpha_t)
            - (rho*s*d*c_npalpha*omega1)/(2*m) * (v2*i1 - v1*i2)
            + (rho*v*s*d*(c_nq + c_nalpha_dot))/(2*m) * (h1*i2 - h2*i1)
        )

        # Equações de momento (dh/dt)
        dh1 = (
            (rho*v*s*d**2*c_lp*omega1)/(2*i_t) * i1
            + (rho*v**2*s*d*delta_f*c_l_delta)/(2*i_t) * i1
            + (rho*v*s*d*c_malpha)/(2*i_t) * (v2*i3 - v3*i2)
            + (rho*s*d**2*c_mpalpha*omega1)/(2*i_t) * (v1 - v*i1*cos_alpha_t)
            + (rho*v*s*d**2*(c_mq+c_malpha_dot)) /
            (2*i_t) * (h1 - ((i_t)*omega1)*i1)
        )
        dh2 = (
            (rho*v*s*d**2*c_lp*omega1)/(i_t) * i2
            + (rho*v**2*s*d*delta_f*c_l_delta)/(i_t) * i2
            + (rho*v*s*d*c_malpha)/(2*i_t) * (v3*i1 - v1*i3)
            + (rho*s*d**2*c_mpalpha*omega1)/(2*i_t) * (v2 - v*i2*cos_alpha_t)
            + (rho*v*s*d**2*(c_mq+c_malpha_dot)) /
            (2*i_t) * (h2 - ((i_p/i_t)*omega1)*i2)
        )
        dh3 = (
            (rho*v*s*d**2*c_lp*omega1)/(i_t) * i3
            + (rho*v**2*s*d*delta_f*c_l_delta)/(2*i_t) * i3
            + (rho*v*s*d*c_malpha)/(2*i_t) * (v1*i2 - v2*i1)
            + (rho*s*d**2*c_mpalpha*omega1)/(2*i_t) * (v3 - v*i3*cos_alpha_t)
            + (rho*v*s*d**2*(c_mq+c_malpha_dot)) /
            (2*i_t) * (h3 - ((i_p/i_t)*omega1)*i3)
        )

        # Equação de orientação (di'/dt)
        di1 = h2*i3 - h3*i2
        di2 = h3*i1 - h1*i3
        di3 = h1*i2 - h2*i1

        # Equação de posição
        dx, dy, dz = v1, v2, v3

        return np.array([dv1, dv2, dv3, dh1, dh2, dh3, di1, di2, di3, dx, dy, dz], dtype=float)

    def simulate(self, max_time=100.0, alpha0_deg=0.0, beta0_deg=0.0,
                 w_j0=5.0, w_k0=5.0, rtol=1e-7, atol=1e-8):
        """
        Executa a simulação balística.

        Parâmetros:
        -----------
        max_time : float
            Tempo máximo de simulação [s]
        alpha0_deg : float
            Ângulo de arfagem inicial [°]
        beta0_deg : float
            Ângulo de guinada inicial [°]
        w_j0 : float
            Velocidade angular em j' [rad/s]
        w_k0 : float
            Velocidade angular em k' [rad/s]
        rtol : float
            Tolerância relativa do integrador
        atol : float
            Tolerância absoluta do integrador

        Retorna:
        --------
        SimulationResult : objeto contendo os resultados
        """
        print("\n" + "="*80)
        print("INICIANDO SIMULAÇÃO")
        print("="*80)

        # Construir condições iniciais
        y0 = self.build_initial_conditions(alpha0_deg, beta0_deg, w_j0, w_k0)

        # Evento de impacto no solo
        def ground_event(_t, y):
            return y[10]  # y position
        ground_event.direction = -1
        ground_event.terminal = True

        print("\nIntegrando trajetória...")

        # Resolver EDO
        sol = solve_ivp(self.rhs, (0.0, max_time), y0,
                        method='DOP853',
                        rtol=rtol, atol=atol,
                        events=ground_event,
                        max_step=0.1)

        if sol.success:
            print("✓ Integração bem-sucedida!")
            print(f"  Tempo de voo: {sol.t[-1]:.2f} s")
        else:
            print(f"✗ Erro na integração: {sol.message}")

        # Criar objeto de resultado
        self.result = SimulationResults(sol, self)

        return self.result
