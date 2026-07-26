class ValidationError(Exception):
    """Exception raised for errors in the user input validation."""
    pass

class InputValidator:
    """Validator class for parsing and checking input fields."""
    
    @staticmethod
    def parse_csv_input(input_str: str, expected_len: int = None) -> list:
        """
        Parses a comma-separated string into a list of floats.
        
        Args:
            input_str: The string to parse.
            expected_len: If provided, validates that the number of parsed items matches.
            
        Returns:
            List of floats.
            
        Raises:
            ValidationError: If parsing fails or length mismatch.
        """
        if not input_str.strip():
            raise ValidationError("Input cannot be empty.")
            
        try:
            values = [float(x.strip()) for x in input_str.split(',')]
        except ValueError:
            raise ValidationError("Please ensure all inputs are valid comma-separated numbers.")
            
        if expected_len is not None and len(values) != expected_len:
            raise ValidationError(f"Expected {expected_len} values, but got {len(values)}.")
            
        return values
