"""
Feature 16: Advanced DEX Liquidity Forecasting
Source: prophet, arch, statsmodels
"""
from prophet import Prophet
from arch import arch_model
import statsmodels.api as sm
import pandas as pd
import numpy as np
from typing import Dict, List
import asyncio

class DEXLiquidityForecasting:
    def __init__(self):
        self.forecast_models = {}
        self.liquidity_pools = {}
        
    async def forecast_dex_liquidity(self, pool_address: str, historical_data: pd.DataFrame) -> Dict:
        """Forecast liquidity for DEX pools using multiple models"""
        forecasts = {}
        
        # Prophet for trend and seasonality
        prophet_forecast = await self._prophet_forecast(historical_data)
        forecasts['prophet'] = prophet_forecast
        
        # GARCH for volatility
        garch_forecast = await self._garch_volatility_forecast(historical_data)
        forecasts['garch'] = garch_forecast
        
        # ARIMA for stationary patterns
        arima_forecast = await self._arima_forecast(historical_data)
        forecasts['arima'] = arima_forecast
        
        # Ensemble the forecasts
        ensemble_forecast = self._ensemble_forecasts(forecasts)
        
        return {
            'pool_address': pool_address,
            'forecasts': forecasts,
            'ensemble_forecast': ensemble_forecast,
            'liquidity_outlook': self._assess_liquidity_outlook(ensemble_forecast),
            'confidence_interval': self._calculate_confidence(forecasts),
            'forecast_timestamp': self._get_timestamp()
        }
    
    async def _prophet_forecast(self, data: pd.DataFrame) -> Dict:
        """Forecast using Facebook Prophet"""
        try:
            # Prepare data for Prophet
            prophet_data = data.reset_index()[['timestamp', 'liquidity']]
            prophet_data.columns = ['ds', 'y']
            
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
            model.fit(prophet_data)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=24, freq='H')
            forecast = model.predict(future)
            
            return {
                'model': 'prophet',
                'forecast_values': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(24).to_dict('records'),
                'trend': forecast['trend'].iloc[-1],
                'seasonality_strength': self._calculate_seasonality_strength(forecast)
            }
        except Exception as e:
            return {'model': 'prophet', 'error': str(e)}
    
    async def _garch_volatility_forecast(self, data: pd.DataFrame) -> Dict:
        """Forecast volatility using GARCH model"""
        try:
            returns = data['liquidity'].pct_change().dropna()
            
            if len(returns) > 50:
                model = arch_model(returns, vol='Garch', p=1, q=1)
                fitted_model = model.fit(disp='off')
                
                # Forecast volatility
                forecast = fitted_model.forecast(horizon=5)
                predicted_volatility = forecast.variance.values[-1, -1] ** 0.5
                
                return {
                    'model': 'garch',
                    'predicted_volatility': predicted_volatility,
                    'volatility_regime': 'high' if predicted_volatility > 0.02 else 'low',
                    'confidence': 0.85
                }
            else:
                return {'model': 'garch', 'error': 'Insufficient data'}
        except Exception as e:
            return {'model': 'garch', 'error': str(e)}
    
    async def _arima_forecast(self, data: pd.DataFrame) -> Dict:
        """Forecast using ARIMA model"""
        try:
            if len(data) > 30:
                model = sm.tsa.ARIMA(data['liquidity'], order=(2,1,2))
                fitted_model = model.fit()
                
                forecast = fitted_model.forecast(steps=24)
                
                return {
                    'model': 'arima',
                    'forecast_values': forecast.tolist(),
                    'aic': fitted_model.aic,
                    'confidence_intervals': fitted_model.get_forecast(steps=24).conf_int().tolist()
                }
            else:
                return {'model': 'arima', 'error': 'Insufficient data'}
        except Exception as e:
            return {'model': 'arima', 'error': str(e)}
    
    def _ensemble_forecasts(self, forecasts: Dict) -> Dict:
        """Combine multiple forecasts using weighted averaging"""
        valid_forecasts = []
        weights = []
        
        for model_name, forecast in forecasts.items():
            if 'error' not in forecast:
                if model_name == 'prophet' and 'forecast_values' in forecast:
                    latest_value = forecast['forecast_values'][-1]['yhat'] if forecast['forecast_values'] else 0
                    valid_forecasts.append(latest_value)
                    weights.append(0.4)  # Prophet gets highest weight
                elif model_name == 'arima' and 'forecast_values' in forecast:
                    valid_forecasts.append(forecast['forecast_values'][0])
                    weights.append(0.35)
                elif model_name == 'garch' and 'predicted_volatility' in forecast:
                    # Use volatility to adjust confidence
                    valid_forecasts.append(valid_forecasts[-1] if valid_forecasts else 0)
                    weights.append(0.25)
        
        if valid_forecasts and weights:
            ensemble_value = np.average(valid_forecasts, weights=weights)
            return {
                'ensemble_value': ensemble_value,
                'component_forecasts': valid_forecasts,
                'weights': weights,
                'standard_deviation': np.std(valid_forecasts)
            }
        else:
            return {'ensemble_value': 0, 'error': 'No valid forecasts'}
    
    def _calculate_seasonality_strength(self, forecast: pd.DataFrame) -> float:
        """Calculate strength of seasonal patterns"""
        try:
            seasonal_component = forecast['yearly'].std() if 'yearly' in forecast.columns else 0
            trend_component = forecast['trend'].std()
            return seasonal_component / (trend_component + seasonal_component) if (trend_component + seasonal_component) > 0 else 0
        except:
            return 0.0
    
    def _assess_liquidity_outlook(self, ensemble_forecast: Dict) -> str:
        """Assess overall liquidity outlook"""
        if 'ensemble_value' not in ensemble_forecast:
            return 'uncertain'
        
        value = ensemble_forecast['ensemble_value']
        std = ensemble_forecast.get('standard_deviation', 0)
        
        if value > std * 2:
            return 'very_bullish'
        elif value > std:
            return 'bullish'
        elif value > -std:
            return 'neutral'
        elif value > -std * 2:
            return 'bearish'
        else:
            return 'very_bearish'
    
    def _calculate_confidence(self, forecasts: Dict) -> float:
        """Calculate overall forecast confidence"""
        valid_models = sum(1 for f in forecasts.values() if 'error' not in f)
        total_models = len(forecasts)
        
        base_confidence = valid_models / total_models if total_models > 0 else 0
        
        # Adjust based on model agreement
        if 'ensemble_forecast' in forecasts:
            std = forecasts['ensemble_forecast'].get('standard_deviation', 1)
            volatility_adjustment = max(0, 1 - std)
            return base_confidence * volatility_adjustment
        
        return base_confidence
    
    def _get_timestamp(self) -> int:
        import time
        return int(time.time())
