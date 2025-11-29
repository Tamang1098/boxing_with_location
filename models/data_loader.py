# models/data_loader.py
import pandas as pd
import os
from config import Config

class EnhancedDataLoader:
    def __init__(self):
        self.df = None
        self.locations = []
        self.load_data()
    
    def load_data(self):
        """Load and preprocess the enhanced boxing data with locations"""
        try:
            if not os.path.exists(Config.DATA_PATH):
                print(f"Data file not found at: {Config.DATA_PATH}")
                print(f"Current working directory: {os.getcwd()}")
                self.df = pd.DataFrame()
                return
            
            self.df = pd.read_csv(Config.DATA_PATH)
            self._preprocess_data()
            print(f"Enhanced data loaded successfully. Shape: {self.df.shape}")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def _preprocess_data(self):
        """Preprocess the enhanced data"""
        if self.df.empty:
            return
            
        # Calculate win ratio
        self.df['Win_Ratio'] = self.df['Wins'] / (self.df['Wins'] + self.df['Losses'] + 1e-8)
        
        # Calculate total fights
        self.df['Total_Fights'] = self.df['Wins'] + self.df['Losses']
        
        # Calculate performance score
        self.df['Performance_Score'] = (
            self.df['Win_Ratio'] * 0.6 + 
            (self.df['Wins'] / (self.df['Wins'].max() + 1)) * 0.2 +
            (self.df['Total_Fights'] / (self.df['Total_Fights'].max() + 1)) * 0.2
        )
        
        # Extract unique locations and gyms
        self.locations = sorted(self.df['Location'].unique())
    
    def get_data(self):
        return self.df
    
    def get_available_filters(self):
        """Get all available filter options"""
        if self.df.empty:
            return {}
        
        return {
            'locations': ["All Locations"] + self.locations,
            'gyms': ["All Gyms"] + sorted(self.df['Gym'].unique()),
            'years': ["All Years"] + sorted(self.df['Year'].unique()),
            'weights': ["All"] + sorted(self.df['Weight_Class'].unique()),
            'diagram_types': ["Bar Chart", "Pie Chart", "Line Chart", "Scatter Plot"],
            'genders': ["Both", "Male", "Female"]
        }








