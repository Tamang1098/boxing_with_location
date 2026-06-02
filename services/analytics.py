# services/analytics.py
import pandas as pd

class Analytics:
    @staticmethod
    def calculate_kpis(filtered_data, mode):
        """Calculate Key Performance Indicators"""
        if filtered_data.empty:
            return {
                'total_boxers': 0,
                'total_gyms': 0,
                'total_locations': 0,
                'total_fights': 0,
                'avg_win_ratio': 0,
                'top_performer': "N/A"
            }
        
        total_boxers = len(filtered_data['Boxer_Name'].unique())
        total_gyms = len(filtered_data['Gym'].unique())
        total_locations = len(filtered_data['Location'].unique())
        total_fights = (filtered_data['Wins'].sum() + filtered_data['Losses'].sum())
        avg_win_ratio = (filtered_data['Win_Ratio'].mean() * 100).round(2)
        
        # Find top performer
        top_performer = Analytics._find_top_performer(filtered_data, mode)
        
        return {
            'total_boxers': total_boxers,
            'total_gyms': total_gyms,
            'total_locations': total_locations,
            'total_fights': total_fights,
            'avg_win_ratio': avg_win_ratio,
            'top_performer': top_performer
        }
    
    @staticmethod
    def _find_top_performer(filtered_data, mode):
        """Find the top performer based on win ratio"""
        if mode == "Boxer":
            boxer_stats = []
            for boxer in filtered_data['Boxer_Name'].unique():
                boxer_data = filtered_data[filtered_data['Boxer_Name'] == boxer]
                total_wins = boxer_data['Wins'].sum()
                total_losses = boxer_data['Losses'].sum()
                total_fights_boxer = total_wins + total_losses
                win_ratio = total_wins / total_fights_boxer if total_fights_boxer > 0 else 0
                
                gym_name = boxer_data['Gym'].iloc[0] if not boxer_data.empty else 'Unknown Gym'
                location = boxer_data['Location'].iloc[0] if not boxer_data.empty else 'Unknown'
                
                boxer_stats.append({
                    'name': boxer, 
                    'win_ratio': win_ratio, 
                    'wins': total_wins,
                    'gym': gym_name,
                    'location': location
                })
            
            if boxer_stats:
                top_boxer = max(boxer_stats, key=lambda x: x['win_ratio'])
                return f"{top_boxer['name']} ({top_boxer['gym']}, {top_boxer['location']}) - {top_boxer['win_ratio']:.1%}"
        
        elif mode == "Gym":
            gym_stats = []
            for gym in filtered_data['Gym'].unique():
                gym_data = filtered_data[filtered_data['Gym'] == gym]
                total_wins = gym_data['Wins'].sum()
                total_losses = gym_data['Losses'].sum()
                total_fights_gym = total_wins + total_losses
                win_ratio = total_wins / total_fights_gym if total_fights_gym > 0 else 0
                
                location = gym_data['Location'].iloc[0] if not gym_data.empty else 'Unknown'
                gym_stats.append({'name': gym, 'win_ratio': win_ratio, 'location': location})
            
            if gym_stats:
                top_gym = max(gym_stats, key=lambda x: x['win_ratio'])
                return f"{top_gym['name']} ({top_gym['location']}) - {top_gym['win_ratio']:.1%}"
        
        return "N/A"
    
    @staticmethod
    def calculate_win_ratios(filtered_data, mode, selected_boxers, year, diagram_type="Bar Chart"):
        """Calculate win ratios for display"""
        win_ratios = {}
        
        if filtered_data.empty:
            return win_ratios
        
        if mode == "Gym":
            for gym in filtered_data['Gym'].unique():
                gym_data = filtered_data[filtered_data['Gym'] == gym]
                total_wins = gym_data['Wins'].sum()
                total_losses = gym_data['Losses'].sum()
                total_fights = total_wins + total_losses
                win_ratio = total_wins / total_fights if total_fights > 0 else 0
                
                location = gym_data['Location'].iloc[0] if not gym_data.empty else 'Unknown'
                display_name = f"{gym} ({location})"
                win_ratios[display_name] = win_ratio
                    
        elif mode == "Boxer":
            boxers_to_calculate = selected_boxers if selected_boxers else filtered_data['Boxer_Name'].unique()
            for boxer in boxers_to_calculate:
                boxer_data = filtered_data[filtered_data['Boxer_Name'] == boxer]
                if not boxer_data.empty:
                    if year == "All Years" or diagram_type == "Line Chart":
                        total_wins = boxer_data['Wins'].sum()
                        total_losses = boxer_data['Losses'].sum()
                        total_fights = total_wins + total_losses
                        win_ratio = total_wins / total_fights if total_fights > 0 else 0
                    else:
                        total_wins = boxer_data['Wins'].sum()
                        total_losses = boxer_data['Losses'].sum()
                        total_fights = total_wins + total_losses
                        win_ratio = total_wins / total_fights if total_fights > 0 else 0
                    
                    gym_name = boxer_data['Gym'].iloc[0] if not boxer_data.empty else 'Unknown Gym'
                    location = boxer_data['Location'].iloc[0] if not boxer_data.empty else 'Unknown'
                    display_name = f"{boxer} ({gym_name}, {location})"
                    win_ratios[display_name] = win_ratio
        
        return win_ratios
    
    @staticmethod
    def calculate_advanced_stats(filtered_data, mode):
        """Calculate advanced statistics"""
        advanced_stats = {}
        
        if filtered_data.empty:
            return advanced_stats
        
        # Most consistent performer
        if mode == "Boxer":
            consistency_data = []
            for boxer in filtered_data['Boxer_Name'].unique():
                boxer_data = filtered_data[filtered_data['Boxer_Name'] == boxer]
                if len(boxer_data) > 1:
                    std_dev = boxer_data['Win_Ratio'].std()
                    avg_ratio = boxer_data['Win_Ratio'].mean()
                    consistency_data.append({'name': boxer, 'std_dev': std_dev, 'avg_ratio': avg_ratio})
            
            if consistency_data:
                most_consistent = min(consistency_data, key=lambda x: x['std_dev'])
                advanced_stats['most_consistent'] = f"{most_consistent['name']} (σ: {most_consistent['std_dev']:.3f})"
        
        # Best gym by volume
        gym_volume = filtered_data.groupby('Gym')['Wins'].sum()
        if not gym_volume.empty:
            best_gym_volume = gym_volume.idxmax()
            advanced_stats['best_gym_volume'] = f"{best_gym_volume} ({gym_volume.max()} wins)"
        
        # Highest win streak
        max_wins = filtered_data['Wins'].max()
        advanced_stats['highest_win_streak'] = max_wins
        
        # Location with most gyms
        location_stats = filtered_data.groupby('Location')['Gym'].nunique()
        if not location_stats.empty:
            best_location = location_stats.idxmax()
            advanced_stats['best_location'] = f"{best_location} ({location_stats.max()} gyms)"
        
        return advanced_stats