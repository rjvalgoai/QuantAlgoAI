import numpy as np
from scipy.stats import norm
from typing import Dict, Optional
from datetime import datetime
from core.logger import logger

class GreeksCalculator:
    """Option Greeks calculator"""
    
    def __init__(self):
        self.N = norm.cdf
        self.N_prime = norm.pdf
        
    def calculate_greeks(self, 
                        spot_price: float,
                        strike_price: float,
                        time_to_expiry: float,  # in years
                        volatility: float,
                        risk_free_rate: float,
                        option_type: str = "call") -> Dict[str, float]:
        """Calculate all Greeks for an option"""
        try:
            # Calculate d1 and d2
            d1 = (np.log(spot_price/strike_price) + 
                  (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / \
                 (volatility * np.sqrt(time_to_expiry))
            d2 = d1 - volatility * np.sqrt(time_to_expiry)
            
            # Calculate Greeks based on option type
            if option_type.lower() == "call":
                delta = self.N(d1)
                gamma = self.N_prime(d1) / (spot_price * volatility * np.sqrt(time_to_expiry))
                theta = (-spot_price * self.N_prime(d1) * volatility / 
                        (2 * np.sqrt(time_to_expiry)) - 
                        risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * 
                        self.N(d2))
                vega = spot_price * np.sqrt(time_to_expiry) * self.N_prime(d1)
                rho = strike_price * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * self.N(d2)
                
            else:  # Put option
                delta = self.N(d1) - 1
                gamma = self.N_prime(d1) / (spot_price * volatility * np.sqrt(time_to_expiry))
                theta = (-spot_price * self.N_prime(d1) * volatility / 
                        (2 * np.sqrt(time_to_expiry)) + 
                        risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * 
                        self.N(-d2))
                vega = spot_price * np.sqrt(time_to_expiry) * self.N_prime(d1)
                rho = -strike_price * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * self.N(-d2)
            
            return {
                "delta": round(delta, 4),
                "gamma": round(gamma, 4),
                "theta": round(theta, 4),
                "vega": round(vega, 4),
                "rho": round(rho, 4)
            }
            
        except Exception as e:
            logger.error(f"Greeks calculation failed: {e}")
            return {}
            
    def calculate_implied_volatility(self,
                                   option_price: float,
                                   spot_price: float,
                                   strike_price: float,
                                   time_to_expiry: float,
                                   risk_free_rate: float,
                                   option_type: str = "call") -> Optional[float]:
        """Calculate implied volatility using Newton-Raphson method"""
        try:
            MAX_ITERATIONS = 100
            PRECISION = 1.0e-5
            sigma = 0.5  # Initial guess
            
            for i in range(MAX_ITERATIONS):
                price = self.calculate_option_price(
                    spot_price, strike_price, time_to_expiry,
                    sigma, risk_free_rate, option_type
                )
                diff = option_price - price
                
                if abs(diff) < PRECISION:
                    return sigma
                    
                vega = self.calculate_greeks(
                    spot_price, strike_price, time_to_expiry,
                    sigma, risk_free_rate, option_type
                )["vega"]
                
                if vega == 0:
                    return None
                    
                sigma = sigma + diff/vega
                
            return None
            
        except Exception as e:
            logger.error(f"Implied volatility calculation failed: {e}")
            return None

    def calculate_iv(self, option_data):
        """Calculate Implied Volatility using Newton-Raphson method"""
        try:
            S = option_data['Underlying']  # Current stock price
            K = option_data['Strike Price']
            T = (option_data['Expiry'] - datetime.today()).days / 365
            r = 0.05  # Assuming a default risk-free rate
            C = option_data['Last Price']
            
            sigma = 0.3  # Initial volatility guess
            
            for i in range(100):
                d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
                d2 = d1 - sigma*np.sqrt(T)
                
                if option_data['Option Type'] == 'CE':
                    price = S*self.N(d1) - K*np.exp(-r*T)*self.N(d2)
                else:
                    price = K*np.exp(-r*T)*self.N(-d2) - S*self.N(-d1)
                
                diff = C - price
                if abs(diff) < 0.0001:
                    return sigma
                    
                vega = S*np.sqrt(T)*self.N_prime(d1)
                sigma = sigma + diff/vega
                
            return sigma
        except Exception as e:
            logger.error(f"Error calculating IV: {e}")
            return np.nan
            
    # Add other Greek calculations... 