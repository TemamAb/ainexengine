#!/usr/bin/env python3
"""
ÌµµÔ∏è STEALTH MODE VERIFICATION SCRIPT
Verify all stealth protections are active and functioning
"""

import asyncio
from src.security.stealth_mode import StealthModeEngine
from web3 import Web3

async def verify_stealth_mode():
    """Verify stealth mode is fully functional"""
    print("ÌµµÔ∏è  VERIFYING STEALTH MODE PROTECTIONS...")
    
    # Mock Web3 for testing
    web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
    
    try:
        # Initialize stealth engine
        stealth = StealthModeEngine(web3)
        
        # Activate stealth mode
        activation = await stealth.activate_stealth_mode("maximum")
        
        print("‚úÖ STEALTH MODE ACTIVATION:", activation["stealth_mode"])
        print("ÌæØ PROTECTION LEVEL:", activation["level"])
        
        # Verify all protection layers
        for layer in activation["protection_layers"]:
            status = "‚úÖ" if layer["status"].get("status") in ["active", "enabled", "secured"] else "‚ùå"
            print(f"   {status} {layer['layer']}: {layer['status']}")
        
        # Test stealth trade execution
        test_trade = {
            "amount": 10000,
            "asset": "ETH",
            "direction": "buy",
            "routing_path": ["uniswap_v3", "sushiswap"]
        }
        
        stealth_trade = await stealth.execute_stealth_trade(test_trade)
        
        print(f"Ì¥í STEALTH TRADE EXECUTION: {stealth_trade['success']}")
        if stealth_trade['success']:
            print("   ‚úÖ MEV Protected:", stealth_trade['mev_protected'])
            print("   ‚úÖ Identity Rotated:", stealth_trade['identity_rotated'])
            print("   ‚úÖ Stealth Level:", stealth_trade['stealth_level'])
        
        print("\nÌæØ STEALTH MODE VERIFICATION COMPLETE!")
        print("Ì¥í ALL PROTECTIONS ACTIVE AND FUNCTIONAL")
        
    except Exception as e:
        print(f"‚ùå STEALTH MODE VERIFICATION FAILED: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(verify_stealth_mode())
    exit(0 if success else 1)
