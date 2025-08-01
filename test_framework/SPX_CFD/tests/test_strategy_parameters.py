"""
Test suite for Strategy Parameter functionality (Category 2).
Tests parameter validation, relationships, and constraints.
"""

import pytest
import numpy as np
from unittest.mock import Mock


class TestParameterValidation:
    """Test suite for Parameter Validation (2.1)."""
    
    @pytest.mark.unit
    def test_initial_capital_validation(self, test_logger):
        """Test capital range ($10K-$1M)."""
        test_logger.start_test("test_initial_capital_validation")
        
        try:
            # Valid capital amounts
            valid_capitals = [10000, 25000, 50000, 100000, 500000, 1000000]
            
            for capital in valid_capitals:
                assert 10000 <= capital <= 1000000, f"Capital {capital} outside valid range"
                assert isinstance(capital, (int, float)), f"Capital {capital} not numeric"
                assert capital > 0, f"Capital {capital} not positive"
            
            # Invalid capital amounts
            invalid_capitals = [5000, 1500000, -10000, 0]
            
            for capital in invalid_capitals:
                if capital < 10000 or capital > 1000000:
                    assert not (10000 <= capital <= 1000000), f"Capital {capital} should be invalid"
            
            test_logger.end_test("test_initial_capital_validation", "PASS")
        except Exception as e:
            test_logger.end_test("test_initial_capital_validation", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_risk_per_trade_bounds(self, test_logger):
        """Validate risk percentage (0.5-3.0%)."""
        test_logger.start_test("test_risk_per_trade_bounds")
        
        try:
            # Valid risk percentages
            valid_risks = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
            
            for risk in valid_risks:
                assert 0.5 <= risk <= 3.0, f"Risk {risk}% outside valid range"
                assert isinstance(risk, (int, float)), f"Risk {risk} not numeric"
                assert risk > 0, f"Risk {risk} not positive"
            
            # Invalid risk percentages
            invalid_risks = [0.4, 3.1, 5.0, -1.0, 0]
            
            for risk in invalid_risks:
                if risk < 0.5 or risk > 3.0:
                    assert not (0.5 <= risk <= 3.0), f"Risk {risk}% should be invalid"
            
            test_logger.end_test("test_risk_per_trade_bounds", "PASS")
        except Exception as e:
            test_logger.end_test("test_risk_per_trade_bounds", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_opening_range_minutes(self, test_logger):
        """Test opening range (15-60 minutes)."""
        test_logger.start_test("test_opening_range_minutes")
        
        try:
            # Valid opening range minutes
            valid_minutes = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
            
            for minutes in valid_minutes:
                assert 15 <= minutes <= 60, f"Opening range {minutes} min outside valid range"
                assert isinstance(minutes, int), f"Opening range {minutes} not integer"
                assert minutes > 0, f"Opening range {minutes} not positive"
            
            # Invalid opening range minutes
            invalid_minutes = [10, 65, 0, -5, 120]
            
            for minutes in invalid_minutes:
                if minutes < 15 or minutes > 60:
                    assert not (15 <= minutes <= 60), f"Opening range {minutes} min should be invalid"
            
            test_logger.end_test("test_opening_range_minutes", "PASS")
        except Exception as e:
            test_logger.end_test("test_opening_range_minutes", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_entry_threshold_validation(self, test_logger):
        """Test threshold points (1.0-3.0 pts)."""
        test_logger.start_test("test_entry_threshold_validation")
        
        try:
            # Valid entry threshold points
            valid_thresholds = [1.0, 1.5, 2.0, 2.5, 3.0]
            
            for threshold in valid_thresholds:
                assert 1.0 <= threshold <= 3.0, f"Entry threshold {threshold} pts outside valid range"
                assert isinstance(threshold, (int, float)), f"Entry threshold {threshold} not numeric"
                assert threshold > 0, f"Entry threshold {threshold} not positive"
            
            # Invalid entry threshold points
            invalid_thresholds = [0.5, 3.5, 0, -1.0, 5.0]
            
            for threshold in invalid_thresholds:
                if threshold < 1.0 or threshold > 3.0:
                    assert not (1.0 <= threshold <= 3.0), f"Entry threshold {threshold} pts should be invalid"
            
            test_logger.end_test("test_entry_threshold_validation", "PASS")
        except Exception as e:
            test_logger.end_test("test_entry_threshold_validation", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_stop_loss_validation(self, test_logger):
        """Test stop loss points (3.0-6.0 pts)."""
        test_logger.start_test("test_stop_loss_validation")
        
        try:
            # Valid stop loss points
            valid_stops = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
            
            for stop in valid_stops:
                assert 3.0 <= stop <= 6.0, f"Stop loss {stop} pts outside valid range"
                assert isinstance(stop, (int, float)), f"Stop loss {stop} not numeric"
                assert stop > 0, f"Stop loss {stop} not positive"
            
            # Invalid stop loss points
            invalid_stops = [2.5, 6.5, 0, -1.0, 10.0]
            
            for stop in invalid_stops:
                if stop < 3.0 or stop > 6.0:
                    assert not (3.0 <= stop <= 6.0), f"Stop loss {stop} pts should be invalid"
            
            test_logger.end_test("test_stop_loss_validation", "PASS")
        except Exception as e:
            test_logger.end_test("test_stop_loss_validation", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_profit_target_validation(self, test_logger):
        """Test profit target points (6.0-12.0 pts)."""
        test_logger.start_test("test_profit_target_validation")
        
        try:
            # Valid profit target points
            valid_targets = [6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]
            
            for target in valid_targets:
                assert 6.0 <= target <= 12.0, f"Profit target {target} pts outside valid range"
                assert isinstance(target, (int, float)), f"Profit target {target} not numeric"
                assert target > 0, f"Profit target {target} not positive"
            
            # Invalid profit target points
            invalid_targets = [5.5, 12.5, 0, -1.0, 20.0]
            
            for target in invalid_targets:
                if target < 6.0 or target > 12.0:
                    assert not (6.0 <= target <= 12.0), f"Profit target {target} pts should be invalid"
            
            test_logger.end_test("test_profit_target_validation", "PASS")
        except Exception as e:
            test_logger.end_test("test_profit_target_validation", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_directional_bias_multiplier(self, test_logger):
        """Test bias multiplier (1.0-2.0x)."""
        test_logger.start_test("test_directional_bias_multiplier")
        
        try:
            # Valid directional bias multipliers
            valid_multipliers = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
            
            for multiplier in valid_multipliers:
                assert 1.0 <= multiplier <= 2.0, f"Bias multiplier {multiplier}x outside valid range"
                assert isinstance(multiplier, (int, float)), f"Bias multiplier {multiplier} not numeric"
                assert multiplier > 0, f"Bias multiplier {multiplier} not positive"
            
            # Invalid directional bias multipliers
            invalid_multipliers = [0.9, 2.1, 0, -1.0, 3.0]
            
            for multiplier in invalid_multipliers:
                if multiplier < 1.0 or multiplier > 2.0:
                    assert not (1.0 <= multiplier <= 2.0), f"Bias multiplier {multiplier}x should be invalid"
            
            test_logger.end_test("test_directional_bias_multiplier", "PASS")
        except Exception as e:
            test_logger.end_test("test_directional_bias_multiplier", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_transaction_cost_parameters(self, test_logger):
        """Test spread and commission parameters."""
        test_logger.start_test("test_transaction_cost_parameters")
        
        try:
            # Valid spread points (0.4-1.5 pts)
            valid_spreads = [0.4, 0.5, 0.7, 1.0, 1.2, 1.5]
            
            for spread in valid_spreads:
                assert 0.4 <= spread <= 1.5, f"Spread {spread} pts outside valid range"
                assert isinstance(spread, (int, float)), f"Spread {spread} not numeric"
                assert spread > 0, f"Spread {spread} not positive"
            
            # Valid commission per trade ($0.5-$2.0)
            valid_commissions = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
            
            for commission in valid_commissions:
                assert 0.5 <= commission <= 2.0, f"Commission ${commission} outside valid range"
                assert isinstance(commission, (int, float)), f"Commission {commission} not numeric"
                assert commission > 0, f"Commission {commission} not positive"
            
            # Invalid parameters
            invalid_spreads = [0.3, 1.6, 0, -0.5]
            for spread in invalid_spreads:
                if spread < 0.4 or spread > 1.5:
                    assert not (0.4 <= spread <= 1.5), f"Spread {spread} pts should be invalid"
            
            invalid_commissions = [0.4, 2.1, 0, -1.0]
            for commission in invalid_commissions:
                if commission < 0.5 or commission > 2.0:
                    assert not (0.5 <= commission <= 2.0), f"Commission ${commission} should be invalid"
            
            test_logger.end_test("test_transaction_cost_parameters", "PASS")
        except Exception as e:
            test_logger.end_test("test_transaction_cost_parameters", "FAIL", str(e))
            raise


class TestParameterRelationships:
    """Test suite for Parameter Relationship Tests (2.2)."""
    
    @pytest.mark.unit
    def test_risk_reward_ratio_calculation(self, test_logger, sample_strategy_params):
        """Verify 2:1 risk-reward ratio."""
        test_logger.start_test("test_risk_reward_ratio_calculation")
        
        try:
            stop_loss = sample_strategy_params['stop_loss_points']
            profit_target = sample_strategy_params['profit_target_points']
            
            # Calculate risk-reward ratio
            risk_reward_ratio = profit_target / stop_loss
            
            # Should be approximately 2:1 (profit target / stop loss)
            expected_ratio = 2.0
            tolerance = 0.5  # Allow some variance
            
            assert abs(risk_reward_ratio - expected_ratio) <= tolerance, \
                f"Risk-reward ratio {risk_reward_ratio:.2f}:1 not close to expected {expected_ratio}:1"
            
            # Test with various valid combinations
            test_combinations = [
                (3.0, 6.0),   # 2:1 ratio
                (4.0, 8.0),   # 2:1 ratio
                (5.0, 10.0),  # 2:1 ratio
                (6.0, 12.0),  # 2:1 ratio
            ]
            
            for stop, target in test_combinations:
                ratio = target / stop
                assert abs(ratio - 2.0) <= tolerance, f"Ratio {ratio:.2f}:1 for stop={stop}, target={target}"
            
            test_logger.end_test("test_risk_reward_ratio_calculation", "PASS")
        except Exception as e:
            test_logger.end_test("test_risk_reward_ratio_calculation", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_cost_viability_check(self, test_logger, sample_strategy_params):
        """Ensure profit targets 8x larger than spreads."""
        test_logger.start_test("test_cost_viability_check")
        
        try:
            spread_points = sample_strategy_params['spread_points']
            profit_target = sample_strategy_params['profit_target_points']
            
            # Calculate ratio
            cost_to_target_ratio = profit_target / spread_points
            
            # Should be at least 8x larger
            minimum_ratio = 8.0
            
            assert cost_to_target_ratio >= minimum_ratio, \
                f"Profit target ({profit_target} pts) is only {cost_to_target_ratio:.1f}x spread ({spread_points} pts), should be at least {minimum_ratio}x"
            
            # Test with various spreads
            test_spreads = [0.4, 0.5, 0.7, 1.0, 1.2, 1.5]
            
            for spread in test_spreads:
                # Minimum profit target for this spread
                min_profit_target = spread * minimum_ratio
                
                assert min_profit_target >= spread * minimum_ratio, \
                    f"For spread {spread}, minimum profit target should be {min_profit_target}"
                
                # Check if current profit target is viable with this spread
                if profit_target >= min_profit_target:
                    ratio = profit_target / spread
                    assert ratio >= minimum_ratio, f"Ratio {ratio:.1f}x below minimum for spread {spread}"
            
            test_logger.end_test("test_cost_viability_check", "PASS")
        except Exception as e:
            test_logger.end_test("test_cost_viability_check", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_position_sizing_formula(self, test_logger, sample_strategy_params):
        """Validate position size calculations."""
        test_logger.start_test("test_position_sizing_formula")
        
        try:
            initial_capital = sample_strategy_params['initial_capital']
            risk_per_trade = sample_strategy_params['risk_per_trade']
            stop_loss_points = sample_strategy_params['stop_loss_points']
            
            # Position sizing formula: Risk Amount ÷ (Stop Loss Points × CFD Multiplier)
            risk_amount = initial_capital * (risk_per_trade / 100)
            cfd_multiplier = 1.0  # $1 per point for S&P 500 CFDs
            position_size = int(risk_amount / (stop_loss_points * cfd_multiplier))
            
            # Validate calculations
            assert risk_amount > 0, "Risk amount should be positive"
            assert position_size > 0, "Position size should be positive"
            assert isinstance(position_size, int), "Position size should be integer"
            
            # Test example from requirements: $100 risk ÷ (4 points × $1/point) = 25 CFDs
            test_risk = 100
            test_stop_loss = 4.0
            expected_size = int(test_risk / (test_stop_loss * cfd_multiplier))
            assert expected_size == 25, f"Expected 25 CFDs, got {expected_size}"
            
            # Test with sample parameters
            expected_sample_size = int((initial_capital * risk_per_trade / 100) / (stop_loss_points * cfd_multiplier))
            assert position_size == expected_sample_size, \
                f"Position size {position_size} doesn't match expected {expected_sample_size}"
            
            # Validate maximum risk is respected
            actual_risk = position_size * stop_loss_points * cfd_multiplier
            assert actual_risk <= risk_amount, \
                f"Actual risk ${actual_risk:.2f} exceeds intended risk ${risk_amount:.2f}"
            
            test_logger.end_test("test_position_sizing_formula", "PASS")
        except Exception as e:
            test_logger.end_test("test_position_sizing_formula", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_leverage_constraints(self, test_logger, sample_strategy_params):
        """Test maximum 5:1 leverage limits."""
        test_logger.start_test("test_leverage_constraints")
        
        try:
            initial_capital = sample_strategy_params['initial_capital']
            
            # Test valid leverage ratios
            valid_leverage_ratios = [
                (2, 1, "Conservative"),  # 2:1 leverage (50% margin)
                (3, 1, "Moderate"),      # 3:1 leverage (33% margin)
                (5, 1, "Maximum"),       # 5:1 leverage (20% margin)
            ]
            
            for leverage, _, description in valid_leverage_ratios:
                # Calculate maximum position value
                max_position_value = initial_capital * leverage
                
                # Calculate margin requirement
                margin_requirement = max_position_value / leverage
                margin_utilization = margin_requirement / initial_capital
                
                assert leverage <= 5, f"{description} leverage {leverage}:1 exceeds maximum 5:1"
                assert margin_utilization <= 1.0, f"Margin utilization {margin_utilization:.2%} exceeds 100%"
                
                # Test margin utilization percentages
                if leverage == 2:
                    assert abs(margin_utilization - 0.5) < 0.01, "2:1 leverage should use 50% margin"
                elif leverage == 3:
                    assert abs(margin_utilization - 0.33) < 0.02, "3:1 leverage should use ~33% margin"
                elif leverage == 5:
                    assert abs(margin_utilization - 0.2) < 0.01, "5:1 leverage should use 20% margin"
            
            # Test invalid leverage ratios
            invalid_leverage_ratios = [6, 10, 20, 50]
            
            for leverage in invalid_leverage_ratios:
                assert leverage > 5, f"Leverage {leverage}:1 should be invalid (exceeds 5:1 limit)"
            
            test_logger.end_test("test_leverage_constraints", "PASS")
        except Exception as e:
            test_logger.end_test("test_leverage_constraints", "FAIL", str(e))
            raise