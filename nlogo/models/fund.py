"""
Mutual Insurance Fund model.
"""


class Fund:
    """Represents the mutual insurance fund that collects contributions and pays compensation."""
    
    def __init__(self):
        self.assets = 100.0  # Initial fund assets
        self.net_assets = 100.0
    
    def setup(self):
        """Initialize fund."""
        self.net_assets = 100.0
        self.assets = self.net_assets
    
    def update(self, total_contribution: float, total_compensation: float, reserve_ratio: float):
        """Update fund state after a simulation step."""
        self.assets += total_contribution
        self.net_assets = max(
            (1 - (reserve_ratio / 100.0)) * self.assets - total_compensation,
            0.0
        )
        if self.assets < total_compensation:
            print(f"Warning: fund net assets: {self.assets - total_compensation}")
    
    def to_dict(self) -> dict:
        """Convert fund to dictionary for JSON serialization."""
        return {
            'assets': self.assets,
            'net_assets': self.net_assets
        }

