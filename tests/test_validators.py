import pytest
from aqualabs.core.validator import InputValidator, ValidationError

class TestInputValidator:
    def test_valid_csv(self):
        res = InputValidator.parse_csv_input("1.5, 2.5, 3.0")
        assert res == [1.5, 2.5, 3.0]
        
    def test_valid_csv_with_length(self):
        res = InputValidator.parse_csv_input("1.5, 2.5, 3.0", expected_len=3)
        assert res == [1.5, 2.5, 3.0]
        
    def test_invalid_length(self):
        with pytest.raises(ValidationError, match="Expected 3 values, but got 2"):
            InputValidator.parse_csv_input("1.5, 2.5", expected_len=3)
            
    def test_invalid_chars(self):
        with pytest.raises(ValidationError, match="Please ensure all inputs are valid comma-separated numbers"):
            InputValidator.parse_csv_input("1.5, abc, 3.0")
            
    def test_empty_input(self):
        with pytest.raises(ValidationError, match="Input cannot be empty"):
            InputValidator.parse_csv_input("   ")
