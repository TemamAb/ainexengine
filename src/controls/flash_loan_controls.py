class FlashLoanControls:
    def __init__(self):
        self.max_capacity = 500000  # $500K
        self.current_utilization = 0
        self.active_loans = []
        
    def request_flash_loan(self, amount, strategy):
        if amount > self.max_capacity:
            return {'approved': False, 'reason': 'Exceeds maximum capacity'}
        
        if self.current_utilization + amount > self.max_capacity * 0.8:  # 80% safety margin
            return {'approved': False, 'reason': 'High utilization rate'}
            
        loan = {
            'amount': amount,
            'strategy': strategy,
            'timestamp': '2024-01-01 10:00:00',  # Should be dynamic
            'status': 'active'
        }
        self.active_loans.append(loan)
        self.current_utilization += amount
        
        return {'approved': True, 'loan_id': len(self.active_loans), 'terms': 'Must be repaid in same transaction'}
