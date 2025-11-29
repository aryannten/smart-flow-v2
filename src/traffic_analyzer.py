"""
Traffic Analyzer module for SMART FLOW traffic signal simulation system.

Handles traffic density calculation and congestion analysis.
"""

from typing import Dict


class TrafficAnalyzer:
    """
    Analyzes traffic density and identifies congestion patterns.
    
    This class provides methods for calculating traffic density from vehicle counts,
    identifying the most congested lane, and computing density ratios for signal allocation.
    """
    
    def calculate_density(self, lane_counts: Dict[str, int]) -> Dict[str, float]:
        """
        Calculate traffic density for each lane.
        
        For this MVP, density is directly proportional to vehicle count.
        In a more sophisticated system, this could account for lane length,
        historical patterns, or other factors.
        
        Args:
            lane_counts: Dictionary mapping lane names to vehicle counts
            
        Returns:
            Dict[str, float]: Dictionary mapping lane names to density values
        """
        # For MVP, density equals vehicle count (as float)
        densities = {lane: float(count) for lane, count in lane_counts.items()}
        return densities
    
    def identify_max_density_lane(self, densities: Dict[str, float]) -> str:
        """
        Identify the lane with maximum traffic density.
        
        When multiple lanes have equal maximum density, applies consistent
        tie-breaking by selecting the first lane in alphabetical order.
        
        Args:
            densities: Dictionary mapping lane names to density values
            
        Returns:
            str: Name of the lane with maximum density
            
        Raises:
            ValueError: If densities dictionary is empty
        """
        if not densities:
            raise ValueError("Cannot identify max density lane from empty densities")
        
        # Find maximum density value
        max_density = max(densities.values())
        
        # Find all lanes with maximum density
        max_lanes = [lane for lane, density in densities.items() if density == max_density]
        
        # Apply tie-breaking: select first lane alphabetically
        return sorted(max_lanes)[0]
    
    def get_density_ratios(self, densities: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate normalized density ratios for signal allocation.
        
        Converts absolute density values to ratios that sum to 1.0.
        These ratios can be used to proportionally allocate green time.
        
        Args:
            densities: Dictionary mapping lane names to density values
            
        Returns:
            Dict[str, float]: Dictionary mapping lane names to density ratios (0.0 to 1.0)
        """
        total_density = sum(densities.values())
        
        # If no vehicles detected, distribute equally
        if total_density == 0:
            num_lanes = len(densities)
            return {lane: 1.0 / num_lanes for lane in densities.keys()}
        
        # Calculate ratios
        ratios = {lane: density / total_density for lane, density in densities.items()}
        return ratios
