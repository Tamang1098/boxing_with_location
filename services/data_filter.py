# services/data_filter.py
import pandas as pd

class DataFilter:
    def __init__(self, data):
        self.data = data
    
    def apply_filters(self, filters):
        """Apply all filters to the dataset"""
        filtered = self.data.copy()
        
        # Location filter
        if filters.get('location') != "All Locations":
            filtered = filtered[filtered['Location'] == filters['location']]
        
        # Year filter
        if filters.get('year') != "All Years":
            try:
                filtered = filtered[filtered['Year'] == int(filters['year'])]
            except ValueError:
                pass
        
        # Weight filter
        if filters.get('weight') != "All":
            filtered = filtered[filtered['Weight_Class'] == filters['weight']]
        
        # Gender filter
        if filters.get('gender') != "Both":
            filtered = filtered[filtered['Gender'] == filters['gender']]
        
        # Gym filter
        if filters.get('gym') != "All Gyms":
            filtered = filtered[filtered['Gym'] == filters['gym']]
        
        # Mode-specific filters
        if filters.get('mode') == "Gym" and filters.get('selected_gyms'):
            filtered = filtered[filtered['Gym'].isin(filters['selected_gyms'])]
        elif filters.get('mode') == "Boxer" and filters.get('selected_boxers'):
            filtered = filtered[filtered['Boxer_Name'].isin(filters['selected_boxers'])]
        
        return filtered
    
    def get_boxers_with_gyms(self, selected_gyms=None, gender="Both", location="All Locations", source_data=None):
        """Get boxers list with gym names for dropdown"""
        boxer_data = source_data.copy() if source_data is not None else self.data.copy()
        
        if location != "All Locations":
            boxer_data = boxer_data[boxer_data['Location'] == location]
        
        if selected_gyms:
            boxer_data = boxer_data[boxer_data['Gym'].isin(selected_gyms)]
        
        if gender != "Both":
            boxer_data = boxer_data[boxer_data['Gender'] == gender]
        
        available_boxers = []
        for boxer_name in sorted(boxer_data['Boxer_Name'].unique()):
            boxer_info = boxer_data[boxer_data['Boxer_Name'] == boxer_name].iloc[0]
            available_boxers.append({
                'value': boxer_name,
                'display': f"{boxer_name} ({boxer_info['Gym']}, {boxer_info['Location']})"
            })
        
        return available_boxers