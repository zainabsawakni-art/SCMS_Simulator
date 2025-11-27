"""
Bank model representing the lending institution.
"""


class Bank:
    """Represents the bank that provides loans to customers."""
    
    def __init__(self):
        self.cash = 0.0
        self.receivables = 0.0
        self.assets = 0.0
    
    def setup(self, total_debt: float):
        """Initialize bank with total debt."""
        self.receivables = total_debt
        self.cash = 0.0
        self.assets = self.cash + self.receivables
    
    def update(self, total_paid_installment: float, total_compensation: float, 
               total_new_debt: float, performing_debt: float, non_performing_debt: float):
        """Update bank state after a simulation step."""
        self.cash += total_paid_installment + total_compensation - total_new_debt
        if self.cash < 0:
            print(f"Warning: bank-cash < 0: {self.cash}")
        
        self.receivables = performing_debt + non_performing_debt
        self.assets = self.cash + self.receivables
    
    def to_dict(self) -> dict:
        """Convert bank to dictionary for JSON serialization."""
        return {
            'cash': self.cash,
            'receivables': self.receivables,
            'assets': self.assets
        }

