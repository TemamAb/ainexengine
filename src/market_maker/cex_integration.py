"""
Feature 15: Real-Time DEX Integration
Source: web3.py, uniswap-v3-sdk, aave-protocol
"""
from web3 import Web3
from web3.middleware import geth_poa_middleware
import asyncio
import aiohttp
from typing import Dict, List
import time

class DEXIntegration:
    def __init__(self, web3_providers: Dict):
        self.web3_instances = {}
        self.setup_web3_connections(web3_providers)
        
        # DEX Router Addresses
        self.dex_routers = {
            'uniswap_v3': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
            'sushiswap': '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
            'pancakeswap_v3': '0x13f4EA83D0bd40E75C8222255bc855a974568Dd4',
            'aave_v3': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
            'balancer_v2': '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
        }
        
    def setup_web3_connections(self, providers: Dict):
        """Setup Web3 connections to multiple networks"""
        for network, provider_url in providers.items():
            try:
                w3 = Web3(Web3.HTTPProvider(provider_url))
                if network in ['polygon', 'bsc']:
                    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                if w3.is_connected():
                    self.web3_instances[network] = w3
                    print(f"✅ Connected to {network}")
                else:
                    print(f"❌ Failed to connect to {network}")
            except Exception as e:
                print(f"❌ Error connecting to {network}: {e}")
    
    async def get_dex_arbitrage_opportunities(self, token_pairs: List[str]) -> List[Dict]:
        """Find arbitrage opportunities across DEXes on multiple chains"""
        opportunities = []
        
        for token_pair in token_pairs:
            # Get prices from all DEXes across all chains
            dex_prices = await self._get_all_dex_prices(token_pair)
            
            # Find cross-DEX arbitrage opportunities
            cross_dex_opps = self._find_cross_dex_arbitrage(dex_prices, token_pair)
            opportunities.extend(cross_dex_opps)
            
            # Find cross-chain arbitrage opportunities
            cross_chain_opps = self._find_cross_chain_arbitrage(dex_prices, token_pair)
            opportunities.extend(cross_chain_opps)
        
        return sorted(opportunities, key=lambda x: x['profit_percentage'], reverse=True)
    
    async def _get_all_dex_prices(self, token_pair: str) -> Dict:
        """Get token prices from all DEXes across all chains"""
        dex_prices = {}
        
        for network, w3 in self.web3_instances.items():
            for dex_name, router_address in self.dex_routers.items():
                try:
                    price = await self._get_dex_price(w3, router_address, token_pair, dex_name)
                    if price:
                        key = f"{network}_{dex_name}"
                        dex_prices[key] = {
                            'price': price,
                            'network': network,
                            'dex': dex_name,
                            'router_address': router_address,
                            'timestamp': time.time()
                        }
                except Exception as e:
                    print(f"Error getting price from {dex_name} on {network}: {e}")
        
        return dex_prices
    
    async def _get_dex_price(self, w3, router_address: str, token_pair: str, dex: str) -> float:
        """Get token price from specific DEX"""
        try:
            # This would use the actual DEX router contracts
            # Simplified for example - in production would use actual contract calls
            
            if dex == 'uniswap_v3':
                # Uniswap V3 price calculation
                return await self._get_uniswap_v3_price(w3, router_address, token_pair)
            elif dex == 'aave_v3':
                # Aave V3 lending pool price
                return await self._get_aave_v3_price(w3, router_address, token_pair)
            elif dex == 'sushiswap':
                # Sushiswap price calculation
                return await self._get_sushiswap_price(w3, router_address, token_pair)
                
        except Exception as e:
            print(f"Error getting {dex} price: {e}")
            return None
    
    async def _get_uniswap_v3_price(self, w3, router_address: str, token_pair: str) -> float:
        """Get price from Uniswap V3 pool"""
        # Simplified - actual implementation would use Uniswap V3 Quoter
        try:
            # Mock price calculation - replace with actual contract calls
            base_price = 1.0  # This would be actual price from pool
            return base_price * (1 + (hash(token_pair) % 100) / 10000)  # Small variation
        except:
            return None
    
    async def execute_flash_loan_arbitrage(self, opportunity: Dict, loan_amount: float) -> Dict:
        """Execute flash loan arbitrage on DEXes"""
        try:
            # Step 1: Take flash loan from Aave
            flash_loan_result = await self._take_flash_loan(opportunity, loan_amount)
            
            if not flash_loan_result['success']:
                return {'success': False, 'error': 'Flash loan failed'}
            
            # Step 2: Execute arbitrage trade
            trade_result = await self._execute_arbitrage_trade(opportunity, loan_amount)
            
            # Step 3: Repay flash loan
            repay_result = await self._repay_flash_loan(flash_loan_result['loan_id'])
            
            # Calculate net profit
            net_profit = trade_result['gross_profit'] - flash_loan_result['fee']
            
            return {
                'success': trade_result['success'] and repay_result['success'],
                'flash_loan': flash_loan_result,
                'arbitrage_trade': trade_result,
                'loan_repayment': repay_result,
                'net_profit': net_profit,
                'net_profit_percentage': (net_profit / loan_amount) * 100,
                'executed_at': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'net_profit': 0
            }
    
    async def _take_flash_loan(self, opportunity: Dict, amount: float) -> Dict:
        """Take flash loan from Aave or other lending protocol"""
        try:
            # This would interact with Aave V3 Flash Loan contract
            # Simplified for example
            
            flash_loan_fee = amount * 0.0009  # 0.09% Aave flash loan fee
            
            return {
                'success': True,
                'loan_id': f"flash_loan_{int(time.time())}",
                'amount': amount,
                'fee': flash_loan_fee,
                'protocol': 'aave_v3',
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_arbitrage_trade(self, opportunity: Dict, amount: float) -> Dict:
        """Execute the arbitrage trade across DEXes"""
        try:
            # Buy on cheaper DEX
            buy_result = await self._swap_on_dex(
                opportunity['buy_dex'],
                opportunity['buy_network'], 
                opportunity['token_pair'],
                'buy',
                amount,
                opportunity['buy_price']
            )
            
            # Sell on expensive DEX
            sell_result = await self._swap_on_dex(
                opportunity['sell_dex'],
                opportunity['sell_network'],
                opportunity['token_pair'], 
                'sell',
                amount,
                opportunity['sell_price']
            )
            
            gross_profit = sell_result['output_amount'] - buy_result['input_amount']
            
            return {
                'success': buy_result['success'] and sell_result['success'],
                'gross_profit': gross_profit,
                'buy_transaction': buy_result,
                'sell_transaction': sell_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'gross_profit': 0
            }
    
    async def _swap_on_dex(self, dex: str, network: str, token_pair: str, side: str, amount: float, price: float) -> Dict:
        """Execute swap on specific DEX"""
        try:
            w3 = self.web3_instances.get(network)
            if not w3:
                return {'success': False, 'error': f'Network {network} not connected'}
            
            # This would use actual DEX router contracts to execute swap
            # Simplified for example
            
            return {
                'success': True,
                'dex': dex,
                'network': network,
                'input_amount': amount if side == 'buy' else amount * price,
                'output_amount': amount * price if side == 'buy' else amount,
                'transaction_hash': f"0x{hash(f'{dex}{network}{time.time()}')}",
                'gas_used': 150000,
                'slippage': 0.002
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_cross_dex_arbitrage(self, dex_prices: Dict, token_pair: str) -> List[Dict]:
        """Find arbitrage opportunities between DEXes on same chain"""
        opportunities = []
        networks = set(price_data['network'] for price_data in dex_prices.values())
        
        for network in networks:
            network_prices = {k: v for k, v in dex_prices.items() if v['network'] == network}
            dexes = list(network_prices.keys())
            
            for i, dex1 in enumerate(dexes):
                for j, dex2 in enumerate(dexes):
                    if i != j:
                        price1 = network_prices[dex1]['price']
                        price2 = network_prices[dex2]['price']
                        
                        if price1 and price2 and price1 > price2:
                            spread = price1 - price2
                            spread_percentage = (spread / price2) * 100
                            
                            if spread_percentage > 0.1:  # Minimum 0.1% spread
                                opportunity = {
                                    'type': 'cross_dex',
                                    'token_pair': token_pair,
                                    'network': network,
                                    'buy_dex': dex2,
                                    'sell_dex': dex1,
                                    'buy_price': price2,
                                    'sell_price': price1,
                                    'spread': spread,
                                    'profit_percentage': spread_percentage,
                                    'minimum_profit_threshold': 0.1,
                                    'timestamp': time.time()
                                }
                                opportunities.append(opportunity)
        
        return opportunities
    
    def _find_cross_chain_arbitrage(self, dex_prices: Dict, token_pair: str) -> List[Dict]:
        """Find arbitrage opportunities across different chains"""
        opportunities = []
        
        # Group prices by DEX type across networks
        dex_types = set(price_data['dex'] for price_data in dex_prices.values())
        
        for dex in dex_types:
            dex_prices_by_network = {
                price_data['network']: price_data['price']
                for price_data in dex_prices.values() 
                if price_data['dex'] == dex and price_data['price']
            }
            
            networks = list(dex_prices_by_network.keys())
            for i, net1 in enumerate(networks):
                for j, net2 in enumerate(networks):
                    if i != j:
                        price1 = dex_prices_by_network[net1]
                        price2 = dex_prices_by_network[net2]
                        
                        if price1 > price2:
                            spread = price1 - price2
                            spread_percentage = (spread / price2) * 100
                            
                            # Account for bridge fees (typically 0.1-0.3%)
                            if spread_percentage > 0.3:  # Must overcome bridge fees
                                opportunity = {
                                    'type': 'cross_chain',
                                    'token_pair': token_pair,
                                    'buy_network': net2,
                                    'sell_network': net1,
                                    'dex': dex,
                                    'buy_price': price2,
                                    'sell_price': price1,
                                    'spread': spread,
                                    'profit_percentage': spread_percentage - 0.2,  # Estimate bridge fee
                                    'bridge_required': True,
                                    'minimum_profit_threshold': 0.3,
                                    'timestamp': time.time()
                                }
                                opportunities.append(opportunity)
        
        return opportunities
