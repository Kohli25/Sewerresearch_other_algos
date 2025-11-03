from typing import Dict
import numpy as np

class SewerHydraulics:
    
    """Calculate sewer hydraulic parameters"""
    
    def __init__(self, manning_n: float = 0.013):
        self.n = manning_n
        
    def calculate_flow_parameters(self, Q: float, D: float, S: float) -> Dict:
        """
        Calculate hydraulic parameters for partially full circular sewer
        Q: discharge (m3/s)
        D: diameter (m)
        S: slope (dimensionless)
        
        Returns None if parameters are invalid or calculation fails
        """
        try:
            # Input validation
            if Q is None or D is None or S is None:
                return None
            
            # Check for zero or negative values
            if Q <= 0:
                return None  # Zero or negative discharge
            
            if D <= 0:
                return None  # Invalid diameter
            
            if S <= 0:
                return None  # Invalid slope
            
            if self.n <= 0:
                return None  # Invalid Manning's n
            
            # Equation 3: K = Q*n*D^(-8/3)*S^(-1/2)
            try:
                K = Q * self.n * (D ** (-8/3)) * (S ** (-0.5))
            except (ZeroDivisionError, ValueError, OverflowError):
                return None
            
            # Check for invalid K values
            if not np.isfinite(K) or K <= 0:
                return None
            
            # Ensure K < 1/π (constraint from equation 4)
            if K >= 1/np.pi:
                return None
            
            # Equation 4: Calculate θ
            try:
                inner_sqrt = np.sqrt(np.pi * K)
                if inner_sqrt > 1:  # Check domain for next sqrt
                    return None
                
                middle_sqrt = np.sqrt(1 - inner_sqrt)
                if middle_sqrt > 1:  # Check domain for final sqrt
                    return None
                
                outer_sqrt = np.sqrt(1 - middle_sqrt)
                theta = (3 * np.pi / 2) * outer_sqrt
                
            except (ValueError, RuntimeWarning):
                return None
            
            # Validate theta
            if not np.isfinite(theta) or theta <= 0 or theta > 2 * np.pi:
                return None
            
            # Equation 5: d/D ratio
            try:
                d_D = 0.5 * (1 - np.cos(theta / 2))
            except (ValueError, OverflowError):
                return None
            
            # Validate d/D ratio
            if not np.isfinite(d_D) or d_D < 0 or d_D > 1:
                return None
            
            # Equation 6: hydraulic radius
            try:
                sin_theta = np.sin(theta)
                if not np.isfinite(sin_theta):
                    return None
                
                r = (D / 4) * ((theta - sin_theta) / theta)
            except (ZeroDivisionError, ValueError, OverflowError):
                return None
            
            # Validate hydraulic radius
            if not np.isfinite(r) or r <= 0 or r > D:
                return None
            
            # Calculate velocity: V = (1/n) * R^(2/3) * S^(1/2)
            try:
                V = (1 / self.n) * (r ** (2/3)) * (S ** 0.5)
            except (ZeroDivisionError, ValueError, OverflowError):
                return None
            
            # Validate velocity
            if not np.isfinite(V) or V <= 0:
                return None
            
            # Calculate flow depth
            d = d_D * D
            if not np.isfinite(d) or d < 0 or d > D:
                return None
            
            # All calculations successful, return results
            return {
                'K': K,
                'theta': theta,
                'd_D': d_D,
                'r': r,
                'V': V,
                'd': d
            }
            
        except Exception as e:
            # Catch any unexpected errors
            # print(f"Warning: Hydraulic calculation failed: {str(e)}")
            return None