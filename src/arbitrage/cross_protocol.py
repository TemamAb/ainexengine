"""
Feature 18: Cross-Protocol Arbitrage
Source: web3.py, defi-sdk
"""
from web3 import Web3
import asyncio
import aiohttp
from typing import Dict, List
import time

class CrossProtocolArbitrage:
    def __init__(self, web3_providers: Dict):
        self.web3_instances = web3_providers
        self.protocols = {
            'lending': ['aave_v3', 'compound_v3', 'euler'],
            'dex': ['uniswap_v3', 'sushiswap', 'balancer_v2', 'curve'],
            'derivatives': ['dydx', 'perpetual_protocol', 'gmx']
        }
        
    async def find_cross_protocol_opportunities(self, base_asset: str = 'ETH') -> List[Dict]:
        """Find arbitrage opportunities across different DeFi protocols"""
        opportunities = []
        
        # Get prices from all protocol types
        lending_rates = await self._get_lending_rates(base_asset)
        dex_prices = await self._get_dex_prices(base_asset)
        derivative_prices = await self._get_derivative_prices(base_asset)
        
        # Find lending-DEX arbitrage
        lending_dex_opps = self._find_lending_dex_arbitrage(lending_rates, dex_prices, base_asset)
        opportunities.extend(lending_dex_opps)
        
        # Find DEX-derivatives arbitrage
        dex_deriv_opps = self._find_dex_derivatives_arbitrage(dex_prices, derivative_prices, base_asset)
        opportunities.extend(dex_deriv_opps)
        
        # Find multi-protocol triangular arbitrage
        triangular_opps = await self._find_triangular_arbitrage(base_asset)
        opportunities.extend(triangular_opps)
        
        return sorted(opportunities, key=lambda x: x['expected_profit_percentage'], reverse=True)
    
    async def _get_lending_rates(self, asset: str) -> Dict:
        """Get lending/borrowing rates from lending protocols"""
        rates = {}
        
        for protocol in self.protocols['lending']:
            try:
                if protocol == 'aave_v3':
                    rates[protocol] = await self._get_aave_v3_rates(asset)
                elif protocol == 'compound_v3':
                    rates[protocol] = await self._get_compound_v3_rates(asset)
                elif protocol == 'euler':
                    rates[protocol] = await self._get_euler_rates(asset)
            except Exception as e:
                print(f"Error getting {protocol} rates: {e}")
        
        return rates
    
    async def _get_dex_prices(self, asset: str) -> Dict:
        """Get prices from DEX protocols"""
        prices = {}
        
        for dex in self.protocols['dex']:
            try:
                if dex == 'uniswap_v3':
                    prices[dex] = await self._get_uniswap_v3_price(asset)
                elif dex == 'sushiswap':
                    prices[dex] = await self._get_sushiswap_price(asset)
                elif dex == 'balancer_v2':
                    prices[dex] = await self._get_balancer_price(asset)
                elif dex == 'curve':
                    prices[dex] = await self._get_curve_price(asset)
            except Exception as e:
                print(f"Error getting {dex} price: {e}")
        
        return prices
    
    async def _get_derivative_prices(self, asset: str) -> Dict:
        """Get prices from derivative protocols"""
        prices = {}
        
        for deriv in self.protocols['derivatives']:
            try:
                if deriv == 'dydx':
                    prices[deriv] = await self._get_dydx_price(asset)
                elif deriv == 'perpetual_protocol':
                    prices[deriv] = await self._get_perpetual_protocol_price(asset)
                elif deriv == 'gmx':
                    prices[deriv] = await self._get_gmx_price(asset)
            except Exception as e:
                print(f"Error getting {deriv} price: {e}")
        
        return prices
    
    def _find_lending_dex_arbitrage(self, lending_rates: Dict, dex_prices: Dict, asset: str) -> List[Dict]:
        """Find arbitrage between lending protocols and DEXes"""
        opportunities = []
        
        for lending_protocol, lending_data in lending_rates.items():
            for dex, dex_price in dex_prices.items():
                if lending_data and dex_price:
                    # Opportunity: Borrow cheap, sell high on DEX
                    borrow_rate = lending_data.get('borrow_rate', 0)
                    lending_price = lending_data.get('price', 0)
                    dex_price_value = dex_price.get('price', 0)
                    
                    if lending_price > 0 and dex_price_value > 0:
                        price_diff = dex_price_value - lending_price
                        spread_percentage = (price_diff / lending_price) * 100
                        
                        # Account for borrowing costs
                        net_profit_percentage = spread_percentage - borrow_rate
                        
                        if net_profit_percentage > 0.5:  # Minimum 0.5% net profit
                            opportunity = {
                                'type': 'lending_dex_arbitrage',
                                'asset': asset,
                                'strategy': f'borrow_{lending_protocol}_sell_{dex}',
                                'borrow_protocol': lending_protocol,
                                'sell_dex': dex,
                                'borrow_rate': borrow_rate,
                                'price_difference': price_diff,
                                'spread_percentage': spread_percentage,
                                'net_profit_percentage': net_profit_percentage,
                                'expected_profit_percentage': net_profit_percentage,
                                'complexity': 'medium',
                                'timestamp': time.time()
                            }
                            opportunities.append(opportunity)
        
        return opportunities
    
    def _find_dex_derivatives_arbitrage(self, dex_prices: Dict, deriv_prices: Dict, asset: str) -> List[Dict]:
        """Find arbitrage between DEXes and derivatives"""
        opportunities = []
        
        for dex, dex_data in dex_prices.items():
            for deriv, deriv_data in deriv_prices.items():
                if dex_data and deriv_data:
                    spot_price = dex_data.get('price', 0)
                    futures_price = deriv_data.get('price', 0)
                    
                    if spot_price > 0 and futures_price > 0:
                        basis = futures_price - spot_price
                        basis_percentage = (basis / spot_price) * 100
                        
                        # Basis trading opportunity
                        if abs(basis_percentage) > 0.3:  # Significant basis
                            if basis_percentage > 0:
                                strategy = f'buy_{dex}_sell_{deriv}'
                            else:
                                strategy = f'sell_{dex}_buy_{deriv}'
                            
                            opportunity = {
                                'type': 'basis_trading',
                                'asset': asset,
                                'strategy': strategy,
                                'spot_dex': dex,
                                'derivatives_protocol': deriv,
                                'spot_price': spot_price,
                                'futures_price': futures_price,
                                'basis': basis,
                                'basis_percentage': basis_percentage,
                                'expected_profit_percentage': abs(basis_percentage) * 0.8,  # 80% of basis
                                'complexity': 'high',
                                'timestamp': time.time()
                            }
                            opportunities.append(opportunity)
        
        return opportunities
    
    async def _find_triangular_arbitrage(self, base_asset: str) -> List[Dict]:
        """Find triangular arbitrage opportunities across protocols"""
        opportunities = []
        
        # Example: ETH -> USDC -> DAI -> ETH across different protocols
        try:
            # Get prices for multiple assets
            eth_prices = await self._get_dex_prices('ETH')
            usdc_prices = await self._get_dex_prices('USDC')
            dai_prices = await self._get_dex_prices('DAI')
            
            # Check triangular paths
            for dex1 in self.protocols['dex']:
                for dex2 in self.protocols['dex']:
                    for dex3 in self.protocols['dex']:
                        if dex1 != dex2 and dex2 != dex3:
                            path_profit = self._calculate_triangular_path(
                                eth_prices.get(dex1), 
                                usdc_prices.get(dex2), 
                                dai_prices.get(dex3)
                            )
                            
                            if path_profit and path_profit > 0.2:  # 0.2% minimum
                                opportunity = {
                                    'type': 'triangular_arbitrage',
                                    'path': f'ETH->USDC->DAI->ETH',
                                    'protocols': [dex1, dex2, dex3],
                                    'expected_profit_percentage': path_profit,
                                    'complexity': 'very_high',
                                    'execution_risk': 'high',
                                    'timestamp': time.time()
                                }
                                opportunities.append(opportunity)
        
        except Exception as e:
            print(f"Error in triangular arbitrage: {e}")
        
        return opportunities
    
    def _calculate_triangular_path(self, eth_data: Dict, usdc_data: Dict, dai_data: Dict) -> float:
        """Calculate profit for triangular arbitrage path"""
        if not all([eth_data, usdc_data, dai_data]):
            return 0.0
        
        try:
            # Simplified calculation
            eth_price = eth_data.get('price', 0)
            usdc_price = usdc_data.get('price', 0)
            dai_price = dai_data.get('price', 0)
            
            if eth_price > 0 and usdc_price > 0 and dai_price > 0:
                # Path: 1 ETH -> USDC -> DAI -> ETH
                initial_eth = 1.0
                usdc_amount = initial_eth * eth_price / usdc_price
                dai_amount = usdc_amount * usdc_price / dai_price
                final_eth = dai_amount * dai_price / eth_price
                
                profit_percentage = ((final_eth - initial_eth) / initial_eth) * 100
                return max(0.0, profit_percentage)
        
        except Exception as e:
            print(f"Error calculating triangular path: {e}")
        
        return 0.0
    
    # Mock protocol data methods (would be real implementations)
    async def _get_aave_v3_rates(self, asset: str) -> Dict:
        return {'borrow_rate': 0.034, 'supply_rate': 0.028, 'price': 1800.0}
    
    async def _get_compound_v3_rates(self, asset: str) -> Dict:
        return {'borrow_rate': 0.032, 'supply_rate': 0.026, 'price': 1795.0}
    
    async def _get_uniswap_v3_price(self, asset: str) -> Dict:
        return {'price': 1802.50, 'liquidity': 15000000}
    
    async def _get_sushiswap_price(self, asset: str) -> Dict:
        return {'price': 1801.75, 'liquidity': 8000000}
    
    async def _get_dydx_price(self, asset: str) -> Dict:
        return {'price': 1805.25, 'funding_rate': 0.0001}
