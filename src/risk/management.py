class RiskManagementSystem:
    def __init__(self):
        self.risk_level = 'medium'
        self.exposure_limits = {}
        
    def calculate_var(self, portfolio, confidence=0.95):
        # Value at Risk calculation
        returns = portfolio['returns']
        var = np.percentile(returns, (1 - confidence) * 100)
        return {'var': var, 'confidence': confidence}
    
    def set_risk_level(self, level):
        valid_levels = ['low', 'medium', 'high', 'aggressive']
        if level in valid_levels:
            self.risk_level = level
            return {'status': 'risk_level_updated', 'new_level': level}
        return {'error': 'Invalid risk level'}
