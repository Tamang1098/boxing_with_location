# models/gym_recommender.py
import pandas as pd

class GymRecommender:
    def __init__(self, data):
        self.data = data
    
    def recommend_gyms_by_location(self, location, gender="Both", weight_class="All", limit=4):
        """Recommend best gyms in a specific location"""
        if self.data.empty:
            return []
        
        filtered_data = self.data[self.data['Location'] == location]
        
        if gender != "Both":
            filtered_data = filtered_data[filtered_data['Gender'] == gender]
        
        if weight_class != "All":
            filtered_data = filtered_data[filtered_data['Weight_Class'] == weight_class]
        
        gym_stats = []
        for gym in filtered_data['Gym'].unique():
            gym_data = filtered_data[filtered_data['Gym'] == gym]
            
            total_wins = gym_data['Wins'].sum()
            total_losses = gym_data['Losses'].sum()
            total_fights = total_wins + total_losses
            win_ratio = total_wins / total_fights if total_fights > 0 else 0
            
            total_boxers = len(gym_data['Boxer_Name'].unique())
            avg_performance = gym_data['Performance_Score'].mean()
            
            # Calculate gender-specific performance
            male_boxers = gym_data[gym_data['Gender'] == 'Male']
            female_boxers = gym_data[gym_data['Gender'] == 'Female']
            
            male_win_ratio = male_boxers['Wins'].sum() / (male_boxers['Wins'].sum() + male_boxers['Losses'].sum() + 1e-8)
            female_win_ratio = female_boxers['Wins'].sum() / (female_boxers['Wins'].sum() + female_boxers['Losses'].sum() + 1e-8)
            
            gym_stats.append({
                'gym': gym,
                'win_ratio': win_ratio,
                'total_wins': total_wins,
                'total_boxers': total_boxers,
                'avg_performance': avg_performance,
                'male_win_ratio': male_win_ratio,
                'female_win_ratio': female_win_ratio,
                'total_fights': total_fights
            })
        
        # Sort by win ratio and then by total wins
        gym_stats.sort(key=lambda x: (x['win_ratio'], x['total_wins']), reverse=True)
        
        if limit is None:
            return gym_stats
        return gym_stats[:limit]
    
    def get_gym_improvement_suggestions(self, gym_name, location):
        """Provide improvement suggestions for a specific gym"""
        if self.data.empty:
            return []
        
        gym_data = self.data[(self.data['Gym'] == gym_name) & (self.data['Location'] == location)]
        location_data = self.data[self.data['Location'] == location]
        
        suggestions = []
        
        # Analyze weaknesses
        total_boxers = len(gym_data['Boxer_Name'].unique())
        avg_win_ratio = gym_data['Wins'].sum() / (gym_data['Wins'].sum() + gym_data['Losses'].sum() + 1e-8)
        
        # Compare with other gyms in location
        other_gyms_stats = []
        for other_gym in location_data['Gym'].unique():
            if other_gym != gym_name:
                other_gym_data = location_data[location_data['Gym'] == other_gym]
                other_win_ratio = other_gym_data['Wins'].sum() / (other_gym_data['Wins'].sum() + other_gym_data['Losses'].sum() + 1e-8)
                other_gyms_stats.append(other_win_ratio)
        
        avg_other_win_ratio = sum(other_gyms_stats) / len(other_gyms_stats) if other_gyms_stats else 0
        
        # Generate suggestions based on analysis
        if avg_win_ratio < avg_other_win_ratio:
            suggestions.append(f"Focus on improving overall win ratio (current: {avg_win_ratio:.1%} vs location avg: {avg_other_win_ratio:.1%})")
        
        # Analyze gender performance
        male_performance = gym_data[gym_data['Gender'] == 'Male']['Win_Ratio'].mean()
        female_performance = gym_data[gym_data['Gender'] == 'Female']['Win_Ratio'].mean()
        
        if pd.notna(male_performance) and pd.notna(female_performance):
            if male_performance < female_performance:
                suggestions.append("Male boxers need more focused training sessions")
            elif female_performance < male_performance:
                suggestions.append("Female boxers would benefit from specialized coaching")
        
        # Analyze weight class distribution
        weight_class_counts = gym_data['Weight_Class'].value_counts()
        if len(weight_class_counts) < 3:
            suggestions.append("Consider recruiting boxers from underrepresented weight classes")
        
        # Check for consistency across years
        year_performance = gym_data.groupby('Year')['Win_Ratio'].mean()
        if len(year_performance) > 1 and year_performance.std() > 0.2:
            suggestions.append("Work on maintaining consistent performance across different years")
        
        # Check boxer retention
        if total_boxers < 8:
            suggestions.append("Focus on recruiting more boxers to build team depth")
        
        return suggestions