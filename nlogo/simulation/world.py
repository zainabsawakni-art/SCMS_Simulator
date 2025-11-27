"""
World simulation model representing the overall system state.
"""
import random
import math
from typing import List, Optional
from models.customer import Customer
from models.bank import Bank
from models.fund import Fund


class World:
    """Main simulation world containing all entities and state."""
    
    def __init__(self):
        self.customers: List[Customer] = []
        self.bank = Bank()
        self.fund = Fund()
        
        # Global state variables
        self.seed_number: Optional[int] = None
        self.month = 0
        self.total_contribution = 0.0
        self.total_deficit = 0.0
        self.total_compensation = 0.0
        self.total_paid_installment = 0.0
        self.total_debt = 0.0
        self.total_new_debt = 0.0
        self.zero_risk_period = 0
        self.expelled_agents = 0
        self.cum_total_deficit = 0.0
        self.cum_total_paid_installment = 0.0
        
        # Simulation parameters (defaults matching NetLogo model)
        self.world_size = 1225
        self.base_rate = 0.2
        self.premium_increment = 0.1
        self.min_installment = 4200.0
        self.max_installment = 5400.0
        self.min_periods = 20
        self.max_periods = 60
        self.no_of_periods = 90
        self.insolvency_risk = 3.0
        self.unpaid_fraction = 70.0
        self.max_day = 25
        self.p_day_response = 1.0
        self.premium_response = 1.0
        self.peer_effect = 40.0
        self.reserve_ratio = 0.0
        self.compensation_ratio = 70.0
        self.randomness = 25.0
        self.renew_financing = True
        self.incentive_system = True
        self.adjust_compensation = True
        self.fix_random_seed = False
        
        # Grid dimensions
        self.grid_size = 0
        self.grid_width = 0
        self.grid_height = 0
    
    def set_random_seed(self, seed: Optional[int] = None):
        """Set random seed for reproducibility."""
        if seed is not None:
            self.seed_number = seed
            random.seed(seed)
        else:
            self.seed_number = random.randint(1, 1000000)
            random.seed(self.seed_number)
        print(f"Seed number = {self.seed_number}")
    
    def calculate_no_of_customers(self):
        """Calculate grid dimensions based on world size."""
        self.grid_size = int(math.sqrt(self.world_size))
        self.grid_width = self.grid_size
        self.grid_height = self.grid_size
    
    def setup(self):
        """Initialize the simulation."""
        print("-------------------------------------------------------------------")
        self.month = 0
        self.customers.clear()
        self.expelled_agents = 0
        self.cum_total_deficit = 0.0
        self.cum_total_paid_installment = 0.0
        
        if not self.fix_random_seed:
            self.set_random_seed()
        
        self.calculate_no_of_customers()
        self.setup_customers()
        
        if self.incentive_system:
            self.setup_incentive_system()
        
        self.setup_bank()
        self.setup_fund()
    
    def setup_customers(self):
        """Create and initialize all customers."""
        customer_id = 0
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                customer = Customer(customer_id, x, y)
                customer.setup_financing(
                    self.min_installment,
                    self.max_installment,
                    self.min_periods,
                    self.max_periods
                )
                customer.financing_round = 1
                customer.membership = 1
                customer.status = 1
                self.customers.append(customer)
                customer_id += 1
        
        # Set up neighbor relationships for peer effect
        self._setup_neighbors()
    
    def _setup_neighbors(self):
        """Set up neighbor relationships for each customer."""
        for customer in self.customers:
            neighbors = []
            x, y = customer.x, customer.y
            # Check 8 neighbors (Moore neighborhood)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                        neighbor_id = ny * self.grid_width + nx
                        if neighbor_id < len(self.customers):
                            neighbors.append(self.customers[neighbor_id])
            customer.neighbors = neighbors
    
    def setup_incentive_system(self):
        """Initialize incentive system for all customers."""
        for customer in self.customers:
            customer.setup_payment_day(self.max_day)
            customer.setup_contribution(self.base_rate, self.premium_increment)
            customer.setup_peer_effect(self.peer_effect, self.randomness)
            customer.setup_response(self.p_day_response, self.premium_response, self.randomness)
            customer.setup_membership()
    
    def setup_bank(self):
        """Initialize bank."""
        self.total_debt = sum(c.debt for c in self.customers)
        self.bank.setup(self.total_debt)
    
    def setup_fund(self):
        """Initialize fund."""
        self.fund.setup()
    
    def calculate_renew_financing(self):
        """Handle loan renewals for customers who have completed their loans."""
        self.total_new_debt = 0.0
        for customer in self.customers:
            if customer.patch_month > customer.duration or customer.membership == 0:
                if self.renew_financing:
                    customer.clear_vars()
                    customer.setup_membership()
                    customer.setup_financing(
                        self.min_installment,
                        self.max_installment,
                        self.min_periods,
                        self.max_periods
                    )
                    customer.status = 1
                    customer.financing_round += 1
                    customer.patch_new_debt = customer.debt
                    customer.count_new_debt += 1
                    customer.patch_month = 1
                    self.total_new_debt += customer.patch_new_debt
                    customer.patch_new_debt = 0.0
                else:
                    # cal-exit equivalent
                    customer.clear_vars()
    
    def calculate_incentives(self):
        """Calculate payment day ratings and premiums."""
        if not self.incentive_system:
            return
        
        # First pass: calculate ratings
        expelled_count = 0
        for customer in self.customers:
            if customer.patch_month <= customer.duration and customer.membership == 1:
                customer.calculate_rating(self.max_day)
                if customer.late_payment > 3 and customer.membership == 1:
                    customer.membership = 0
                    expelled_count += 1
        
        self.expelled_agents += expelled_count
        
        # Second pass: calculate premiums
        for customer in self.customers:
            customer.calculate_premium(self.base_rate, self.premium_increment)
    
    def calculate_contribution(self):
        """Calculate membership contributions."""
        self.total_contribution = 0.0
        for customer in self.customers:
            customer.calculate_contribution(self.base_rate, self.incentive_system)
            self.total_contribution += customer.paid_contribution
    
    def calculate_insolvency(self):
        """Calculate insolvency shocks and payment deficits."""
        # First pass: calculate shocks
        for customer in self.customers:
            customer.calculate_shock(self.insolvency_risk, self.unpaid_fraction, self.randomness)
        
        # Second pass: calculate insolvency
        self.total_deficit = 0.0
        self.total_paid_installment = 0.0
        for customer in self.customers:
            customer.calculate_insolvency()
            self.total_deficit += customer.deficit
            self.total_paid_installment += customer.paid_installment
        
        self.cum_total_paid_installment += self.total_paid_installment
        self.cum_total_deficit += self.total_deficit
        self.calculate_shares()
    
    def calculate_shares(self):
        """Calculate compensation shares for each customer."""
        if self.fund.net_assets > self.total_deficit:
            if (self.total_deficit / self.fund.net_assets) < (self.compensation_ratio / 100.0):
                compensation_share = 1.0
            else:
                compensation_share = self.compensation_ratio / 100.0
        else:
            compensation_share = 0.0
        
        for customer in self.customers:
            customer.compensation_share = compensation_share
    
    def calculate_compensation(self):
        """Calculate compensation payments."""
        for customer in self.customers:
            customer.calculate_compensation()
        
        self.adjust_compensations()
        
        sum_period = sum(c.compensation_received for c in self.customers)
        sum_additional = sum(c.additional_compensation for c in self.customers)
        self.total_compensation = sum_period + sum_additional
    
    def adjust_compensations(self):
        """Adjust compensation for accumulated deficits."""
        if not self.adjust_compensation:
            for customer in self.customers:
                customer.additional_compensation = 0.0
            return
        
        sum_cum_deficit = sum(c.cumulative_deficit for c in self.customers)
        if self.fund.net_assets > sum_cum_deficit:
            fund_surplus = self.fund.net_assets - sum_cum_deficit
            for customer in self.customers:
                if sum_cum_deficit > 0:
                    customer.share = customer.cumulative_deficit / (sum_cum_deficit + 1)
                else:
                    customer.share = 0.0
                
                if customer.patch_month <= customer.duration and customer.membership == 1:
                    uncapped_add_comp = customer.share * fund_surplus
                    customer.additional_compensation = min(uncapped_add_comp, customer.cumulative_deficit)
                    customer.cumulative_deficit -= customer.additional_compensation
                    if customer.cumulative_deficit < 0:
                        customer.cumulative_deficit = 0.0
                    customer.cum_compensation += customer.additional_compensation
                    customer.non_performing_debt = customer.cumulative_deficit
                else:
                    customer.additional_compensation = 0.0
        else:
            for customer in self.customers:
                customer.additional_compensation = 0.0
    
    def calculate_debt(self):
        """Update customer debt."""
        for customer in self.customers:
            customer.calculate_debt()
    
    def check_consistency(self):
        """Check consistency of calculations."""
        for customer in self.customers:
            customer.check_consistency()
    
    def calculate_bank(self):
        """Update bank state."""
        performing_debt = sum(c.performing_debt for c in self.customers)
        non_performing_debt = sum(c.non_performing_debt for c in self.customers)
        self.bank.update(
            self.total_paid_installment,
            self.total_compensation,
            self.total_new_debt,
            performing_debt,
            non_performing_debt
        )
    
    def calculate_fund(self):
        """Update fund state."""
        self.fund.update(self.total_contribution, self.total_compensation, self.reserve_ratio)
    
    def calculate_zero_period(self):
        """Calculate months until non-performing debt is zero."""
        avg_npl = sum(c.non_performing_debt for c in self.customers) / len(self.customers) if self.customers else 0
        if avg_npl > 0:
            self.zero_risk_period = self.month
    
    def step(self):
        """Execute one simulation step."""
        self.month += 1
        for customer in self.customers:
            customer.patch_month += 1
        
        self.calculate_renew_financing()
        if self.incentive_system:
            self.calculate_incentives()
        self.calculate_contribution()
        self.calculate_insolvency()
        self.calculate_compensation()
        self.calculate_debt()
        self.calculate_fund()
        self.calculate_bank()
        self.check_consistency()
        self.calculate_zero_period()
        
        # Check stopping conditions
        if not self.renew_financing:
            if self.month >= self.max_periods:
                return False
        else:
            if self.month >= self.no_of_periods:
                return False
        
        return True
    
    def get_state(self) -> dict:
        """Get current simulation state as dictionary."""
        active_customers = [c for c in self.customers if c.membership == 1]
        a_rated = sum(1 for c in active_customers if 1 <= c.day < 11)
        b_rated = sum(1 for c in active_customers if 11 <= c.day < 20)
        c_rated = sum(1 for c in active_customers if c.day >= 20)
        insolvent = sum(1 for c in self.customers if c.shock == 1)
        mean_deficit = sum(c.deficit for c in self.customers) / len(self.customers) if self.customers else 0.0
        mean_compensation_received = sum(c.compensation_received for c in self.customers) / len(self.customers) if self.customers else 0.0
        mean_additional_compensation = sum(c.additional_compensation for c in self.customers) / len(self.customers) if self.customers else 0.0
        mean_day = sum(c.day for c in self.customers) / len(self.customers) if self.customers else 0.0
        max_day = max((c.day for c in self.customers), default=0)
        avg_points = sum(c.points for c in self.customers) / len(self.customers) if self.customers else 0.0
        rounds = max((c.financing_round for c in self.customers), default=1)
        
        return {
            'month': self.month,
            'seed_number': self.seed_number,
            'bank': self.bank.to_dict(),
            'fund': self.fund.to_dict(),
            'customers': {
                'total': len(self.customers),
                'active': len(active_customers),
                'expelled': self.expelled_agents,
                'a_rated': a_rated,
                'b_rated': b_rated,
                'c_rated': c_rated,
                'insolvent': insolvent
            },
            'totals': {
                'contribution': self.total_contribution,
                'deficit': self.total_deficit,
                'compensation': self.total_compensation,
                'paid_installment': self.total_paid_installment,
                'new_debt': self.total_new_debt,
                'cum_deficit': self.cum_total_deficit,
                'cum_paid_installment': self.cum_total_paid_installment
            },
            'metrics': {
                'avg_payment_day': sum(c.day for c in active_customers) / len(active_customers) if active_customers else 0.0,
                'avg_contribution_pct': (sum(c.d_contribution for c in active_customers) * 100 / len(active_customers)) if active_customers else 0.0,
                'performing_debt': sum(c.performing_debt for c in self.customers),
                'non_performing_debt': sum(c.non_performing_debt for c in self.customers),
                'zero_risk_period': self.zero_risk_period,
                'mean_deficit': mean_deficit,
                'mean_compensation_received': mean_compensation_received,
                'mean_additional_compensation': mean_additional_compensation,
                'mean_day': mean_day,
                'max_day': max_day,
                'avg_points': avg_points,
                'rounds': rounds
            },
            'customer_data': [c.to_dict() for c in self.customers[:100]]  # Limit for performance
        }

