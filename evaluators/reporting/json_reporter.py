"""
JSON report generation for evaluation results.

This module provides the JSONReporter class for generating JSON format reports
from evaluation results.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union


class JSONReporter:
    """
    Generates JSON format reports from evaluation results.
    
    This class handles the serialization of evaluation results to JSON format,
    with proper formatting and error handling.
    """
    
    def __init__(self, indent: int = 2) -> None:
        """
        Initialize the JSON reporter.
        
        Args:
            indent: Number of spaces for JSON indentation (default: 2)
        """
        self.indent = indent
    
    def generate_report(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        output_path: Union[str, Path]
    ) -> None:
        """
        Generate a JSON report and save it to a file.
        
        Args:
            data: The evaluation data to serialize (single result or list of results)
            output_path: Path where the JSON report should be saved
        
        Raises:
            IOError: If the file cannot be written
            TypeError: If the data cannot be serialized to JSON
        """
        output_path = Path(output_path)
        
        # Ensure the output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the JSON report
        with open(output_path, "w") as f:
            json.dump(data, f, indent=self.indent)
    
    def generate_report_string(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> str:
        """
        Generate a JSON report as a string without saving to file.
        
        Args:
            data: The evaluation data to serialize (single result or list of results)
        
        Returns:
            JSON formatted string
        
        Raises:
            TypeError: If the data cannot be serialized to JSON
        """
        return json.dumps(data, indent=self.indent)
    
    def load_report(self, input_path: Union[str, Path]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Load a JSON report from a file.
        
        Args:
            input_path: Path to the JSON report file
        
        Returns:
            The deserialized evaluation data
        
        Raises:
            IOError: If the file cannot be read
            json.JSONDecodeError: If the file contains invalid JSON
        """
        input_path = Path(input_path)
        
        with open(input_path, "r") as f:
            return json.load(f)
