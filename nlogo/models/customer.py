"""
Customer (Patch) model representing a borrower in the credit system.
"""
import random
import math


class Customer:
    """Represents a customer/borrower in the credit insurance system."""
    
    def __init__(self, customer_id: int, x: int, y: int):
        self.i = customer_id
        self.x = x
        self.y = y
        
        # Financing variables
        self.installment = 0.0
        self.duration = 0
        self.debt = 0.0
        self.cum_debt = 0.0
        self.gross_debt = 0.0
        self.performing_debt = 0.0
        self.non_performing_debt = 0.0
        self.patch_month = 1
        self.financing_round = 1
        self.count_new_debt = 0
        self.patch_new_debt = 0.0
        self.status = 0
        
        # Insolvency variables
        self.shock = 0
        self.insolvency_fraction = 0.0
        
        # Contribution variables
        self.paid_contribution = 0.0
        self.cum_paid_contribution = 0.0
        self.cumulative_installment = 0.0
        self.unpaid_contribution = 0.0
        
        # Payment variables
        self.paid_installment = 0.0
        self.cum_paid_installment = 0.0
        self.deficit = 0.0
        self.cumulative_deficit = 0.0
        self.balance = 0.0
        
        # Compensation variables
        self.compensation_share = 0.0
        self.compensation_received = 0.0
        self.cum_compensation = 0.0
        self.additional_compensation = 0.0
        self.share = 0.0
        
        # Incentive system variables
        self.d = 0  # Non-adjusted preferred pay-day
        self.p_day = 0  # Preferred day (d ± 1)
        self.day = 0  # Actual pay-day
        self.b_risk = 0.0  # Behavioral risk
        self.lamda = 0.0  # Peer pressure weighting
        self.alpha_1 = 0.0  # Preferred day response
        self.alpha_2 = 0.0  # Premium response
        self.d_contribution = 0.0
        self.std_contribution = 0.0
        self.std_premium = 0.0
        self.points = 0
        
        # Membership variables
        self.membership = 1  # 1 if active, 0 if expelled
        self.on_time_payment = 0
        self.late_payment = 0
        
        # Neighbors for peer effect calculation
        self.neighbors = []
    
    def setup_financing(self, min_installment: float, max_installment: float, 
                       min_periods: int, max_periods: int):
        """Initialize financing for the customer."""
        self.installment = min_installment + random.randint(0, int(max_installment - min_installment))
        self.duration = min_periods + random.randint(0, max_periods - min_periods)
        self.debt = self.installment * self.duration
        self.cum_debt += self.debt
        self.gross_debt = self.installment * self.duration
        self.performing_debt = self.debt
    
    def setup_payment_day(self, max_day: int):
        """Set initial payment day preferences."""
        self.d = random.randint(1, max_day)
        self.p_day = self.d
        self.day = self.p_day
        self.b_risk = self.day / 30.0
    
    def setup_contribution(self, base_rate: float, premium_increment: float):
        """Set initial contribution rate."""
        self.d_contribution = (base_rate / 100.0) + ((premium_increment / 100.0) * max(self.d - 1, 1))
        if base_rate > 0:
            self.std_contribution = (self.d_contribution / (base_rate / 100.0)) / 30.0
        else:
            self.std_contribution = 0.0
    
    def setup_peer_effect(self, peer_effect: float, randomness: float):
        """Set peer effect weighting factor."""
        var = randomness / 100.0
        min_lamda = (1 - var) * (peer_effect / 100.0)
        max_lamda = (1 + var) * (peer_effect / 100.0)
        self.lamda = min_lamda + random.uniform(0, 1) * (max_lamda - min_lamda)
        self.lamda = max(0.0, min(1.0, self.lamda))
    
    def setup_response(self, p_day_response: float, premium_response: float, randomness: float):
        """Set response weighting factors."""
        var = randomness / 100.0
        min_alpha_1 = (1 - var) * p_day_response
        max_alpha_1 = (1 + var) * p_day_response
        min_alpha_2 = (1 - var) * premium_response
        max_alpha_2 = (1 + var) * premium_response
        self.alpha_1 = min_alpha_1 + random.uniform(0, 1) * (max_alpha_1 - min_alpha_1)
        self.alpha_2 = min_alpha_2 + random.uniform(0, 1) * (max_alpha_2 - min_alpha_2)
    
    def setup_membership(self):
        """Initialize membership status."""
        self.points = 100 - (self.d - 1)
        self.on_time_payment = 0
        self.late_payment = 0
        self.membership = 1
    
    def calculate_payment_day(self, max_day: int):
        """Calculate preferred payment day with variation."""
        min_p_day = max(self.d - 1, 1)
        max_p_day = self.d + 1
        self.p_day = min_p_day + random.randint(0, max_p_day - min_p_day)
        if self.p_day > max_day + 1:
            self.p_day = max_day + 1
    
    def calculate_rating(self, max_day: int):
        """Calculate behavioral risk and payment day based on incentives and peer pressure."""
        if self.patch_month > self.duration or self.membership == 0:
            return
        
        self.calculate_payment_day(max_day)
        
        # Calculate d1: weighted combination of p-day and std-premium
        d1 = (self.alpha_1 * (self.p_day / 30.0)) - (self.alpha_2 * self.std_premium)
        
        # Calculate d2: mean b-risk of neighbors
        if self.neighbors:
            d2 = sum(n.b_risk for n in self.neighbors if n.membership == 1) / len(self.neighbors)
        else:
            d2 = self.b_risk
        
        # Calculate behavioral risk
        self.b_risk = ((1 - self.lamda) * d1) + (self.lamda * d2)
        
        if self.b_risk < (1 / 30.0):
            self.b_risk = 1 / 30.0
        
        # Calculate actual payment day
        self.day = round(self.b_risk * 30)
        self.calculate_membership(max_day)
    
    def calculate_premium(self, base_rate: float, premium_increment: float):
        """Calculate contribution based on payment day."""
        if self.patch_month > self.duration or self.membership == 0:
            return
        
        self.d_contribution = (base_rate / 100.0) + ((premium_increment / 100.0) * (self.day - 1))
        if base_rate > 0:
            self.std_contribution = (self.d_contribution / (base_rate / 100.0)) / 30.0
            self.std_premium = self.std_contribution - (1 / 30.0)
        else:
            self.d_contribution = 0.0
            self.std_contribution = 0.0
            self.std_premium = 0.0
    
    def calculate_membership(self, max_day: int):
        """Update membership status based on payment timing."""
        self.points = 100 - (self.day - 1)
        if self.points >= 100 - (max_day - 2):
            self.on_time_payment += 1
        else:
            self.late_payment += 1
        
        if self.late_payment > 3:
            self.membership = 0
    
    def calculate_shock(self, insolvency_risk: float, unpaid_fraction: float, randomness: float):
        """Determine if customer experiences insolvency shock."""
        if self.patch_month > self.duration or self.membership == 0:
            return
        
        s = random.randint(1, 100)
        if s <= insolvency_risk:
            self.shock = 1
            var = randomness / 100.0
            min_fraction = (1 - var) * (unpaid_fraction / 100.0)
            max_fraction = (1 + var) * (unpaid_fraction / 100.0)
            self.insolvency_fraction = min_fraction + random.uniform(0, 1) * (max_fraction - min_fraction)
            if self.insolvency_fraction > 1:
                self.insolvency_fraction = 1.0
        else:
            self.shock = 0
            self.insolvency_fraction = 0.0
    
    def calculate_contribution(self, base_rate: float, incentive_system: bool):
        """Calculate membership contribution."""
        if self.patch_month <= self.duration and self.membership == 1:
            # Previous month's installment (before current shock)
            prev_installment = (1 - (self.shock * self.insolvency_fraction)) * self.installment
            
            if not incentive_system:
                self.d_contribution = base_rate / 100.0
            
            self.paid_contribution = self.d_contribution * prev_installment
            self.cumulative_installment += self.installment
            self.cum_paid_contribution += self.paid_contribution
        else:
            self.paid_contribution = 0.0
    
    def calculate_insolvency(self):
        """Calculate installment payment and deficit."""
        if self.patch_month <= self.duration and self.membership == 1:
            self.deficit = self.shock * self.insolvency_fraction * self.installment
            self.cumulative_deficit += self.deficit
            self.paid_installment = self.installment - self.deficit
            self.cum_paid_installment += self.paid_installment
        
        if self.patch_month > self.duration or self.membership == 0:
            self.deficit = 0.0
            self.paid_installment = 0.0
    
    def calculate_compensation(self):
        """Calculate compensation received from fund."""
        if self.patch_month <= self.duration and self.membership == 1:
            self.compensation_received = self.compensation_share * self.deficit
            self.cumulative_deficit -= self.compensation_received
            self.cum_compensation += self.compensation_received
            self.non_performing_debt = self.cumulative_deficit
        
        if self.patch_month > self.duration or self.membership == 0:
            self.compensation_received = 0.0
    
    def calculate_debt(self):
        """Update remaining debt."""
        if self.patch_month <= self.duration and self.membership == 1:
            self.debt = max(self.debt - self.installment, 0.0)
            self.performing_debt = self.debt
    
    def check_consistency(self):
        """Verify consistency: installment == paid-installment + deficit."""
        if self.patch_month <= self.duration and self.membership == 1:
            self.balance = self.installment - self.paid_installment - self.deficit
    
    def clear_vars(self):
        """Clear temporary variables."""
        self.status = 0
        self.installment = 0.0
        self.paid_contribution = 0.0
        self.deficit = 0.0
        self.paid_installment = 0.0
        self.compensation_received = 0.0
        self.additional_compensation = 0.0
        self.patch_new_debt = 0.0
        self.debt = 0.0
        self.d_contribution = 0.0
        self.std_contribution = 0.0
        self.std_premium = 0.0
        self.day = 0
        self.b_risk = 0.0
        self.on_time_payment = 0
        self.late_payment = 0
    
    def get_rating(self) -> str:
        """Get customer rating based on payment day."""
        if 1 <= self.day < 11:
            return "A"
        elif 11 <= self.day < 20:
            return "B"
        else:
            return "C"
    
    def to_dict(self) -> dict:
        """Convert customer to dictionary for JSON serialization."""
        return {
            'id': self.i,
            'x': self.x,
            'y': self.y,
            'installment': self.installment,
            'debt': self.debt,
            'membership': self.membership,
            'day': self.day,
            'rating': self.get_rating(),
            'shock': self.shock,
            'deficit': self.deficit,
            'paid_installment': self.paid_installment,
            'compensation_received': self.compensation_received,
            'patch_month': self.patch_month,
            'duration': self.duration,
            'points': self.points,
            'on_time_payment': self.on_time_payment,
            'late_payment': self.late_payment
        }

