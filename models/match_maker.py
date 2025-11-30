# models/match_maker.py
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

class MatchMaker:
    """Find fair and balanced matches between boxers"""
    
    def __init__(self, data):
        self.data = data
        self._prepare_boxer_profiles()
        
    def _prepare_boxer_profiles(self):
        """Create boxer profiles for matching"""
        if self.data.empty:
            return
        
        profiles = []
        
        for boxer in self.data['Boxer_Name'].unique():
            boxer_data = self.data[self.data['Boxer_Name'] == boxer]
            
            total_wins = boxer_data['Wins'].sum()
            total_losses = boxer_data['Losses'].sum()
            total_fights = total_wins + total_losses
            win_ratio = total_wins / total_fights if total_fights > 0 else 0
            
            # Calculate skill level (0-100)
            skill_level = win_ratio * 100
            
            # Experience level
            years_active = len(boxer_data['Year'].unique())
            experience_level = min(100, years_active * 20)  # Max 5 years = 100
            
            # Recent performance weight
            recent_year = boxer_data['Year'].max()
            recent_data = boxer_data[boxer_data['Year'] == recent_year]
            recent_wins = recent_data['Wins'].sum()
            recent_losses = recent_data['Losses'].sum()
            recent_fights = recent_wins + recent_losses
            recent_ratio = recent_wins / recent_fights if recent_fights > 0 else 0
            recent_skill = recent_ratio * 100
            
            # Overall rating (weighted)
            overall_rating = (skill_level * 0.5) + (experience_level * 0.2) + (recent_skill * 0.3)
            
            boxer_info = boxer_data.iloc[0]
            
            profiles.append({
                'Boxer_Name': boxer,
                'Gender': boxer_info['Gender'],
                'Weight_Class': boxer_info['Weight_Class'],
                'Age': boxer_info['Age'],
                'Gym': boxer_info['Gym'],
                'Location': boxer_info['Location'],
                'Win_Ratio': win_ratio,
                'Total_Fights': total_fights,
                'Skill_Level': skill_level,
                'Experience_Level': experience_level,
                'Recent_Skill': recent_skill,
                'Overall_Rating': overall_rating
            })
        
        self.boxer_profiles = pd.DataFrame(profiles)
        
    def find_fair_matches(self, boxer_name, top_k=5):
        """Find fair matches for a boxer"""
        if self.boxer_profiles.empty:
            return []
        
        boxer_profile = self.boxer_profiles[self.boxer_profiles['Boxer_Name'] == boxer_name]
        if boxer_profile.empty:
            return []
        
        boxer = boxer_profile.iloc[0]
        
        # Filter potential opponents
        # Same gender, same weight class
        potential = self.boxer_profiles[
            (self.boxer_profiles['Gender'] == boxer['Gender']) &
            (self.boxer_profiles['Weight_Class'] == boxer['Weight_Class']) &
            (self.boxer_profiles['Boxer_Name'] != boxer_name)
        ].copy()
        
        if potential.empty:
            return []
        
        # Calculate match fairness score
        # Fair match: opponent rating within ±15 points
        boxer_rating = boxer['Overall_Rating']
        
        potential['Rating_Diff'] = abs(potential['Overall_Rating'] - boxer_rating)
        potential['Fairness_Score'] = 100 - (potential['Rating_Diff'] * 2)  # Max diff 50 = 0 score
        potential['Fairness_Score'] = potential['Fairness_Score'].clip(lower=0)
        
        # Prefer opponents with similar experience
        experience_diff = abs(potential['Experience_Level'] - boxer['Experience_Level'])
        potential['Experience_Bonus'] = 100 - experience_diff
        potential['Experience_Bonus'] = potential['Experience_Bonus'].clip(lower=0)
        
        # Combined match score
        potential['Match_Score'] = (potential['Fairness_Score'] * 0.7) + (potential['Experience_Bonus'] * 0.3)
        
        # Sort by match score
        potential = potential.sort_values('Match_Score', ascending=False)
        
        results = []
        for _, opp in potential.head(top_k).iterrows():
            rating_diff = opp['Overall_Rating'] - boxer_rating
            if abs(rating_diff) <= 10:
                match_type = "Fair Match"
            elif rating_diff > 10:
                match_type = "Challenging (Opponent Stronger)"
            else:
                match_type = "Advantage (You Stronger)"
            
            results.append({
                'opponent_name': opp['Boxer_Name'],
                'gym': opp['Gym'],
                'location': opp['Location'],
                'opponent_rating': opp['Overall_Rating'],
                'your_rating': boxer_rating,
                'rating_difference': rating_diff,
                'match_type': match_type,
                'match_score': opp['Match_Score'],
                'opponent_win_ratio': opp['Win_Ratio'],
                'opponent_total_fights': int(opp['Total_Fights'])
            })
        
        return results
    
    def find_training_partners(self, boxer_name, top_k=5):
        """Find suitable training partners"""
        if self.boxer_profiles.empty:
            return []
        
        boxer_profile = self.boxer_profiles[self.boxer_profiles['Boxer_Name'] == boxer_name]
        if boxer_profile.empty:
            return []
        
        boxer = boxer_profile.iloc[0]
        
        # Find similar boxers for training
        # Same location preferred, similar skill level
        potential = self.boxer_profiles[
            (self.boxer_profiles['Gender'] == boxer['Gender']) &
            (self.boxer_profiles['Weight_Class'] == boxer['Weight_Class']) &
            (self.boxer_profiles['Boxer_Name'] != boxer_name)
        ].copy()
        
        if potential.empty:
            return []
        
        # Location bonus (same location preferred)
        potential['Location_Bonus'] = potential['Location'] == boxer['Location']
        potential['Location_Bonus'] = potential['Location_Bonus'].astype(int) * 30
        
        # Skill similarity (close skill level good for training)
        skill_diff = abs(potential['Skill_Level'] - boxer['Skill_Level'])
        potential['Skill_Similarity'] = 100 - (skill_diff * 2)
        potential['Skill_Similarity'] = potential['Skill_Similarity'].clip(lower=0)
        
        # Experience similarity
        exp_diff = abs(potential['Experience_Level'] - boxer['Experience_Level'])
        potential['Exp_Similarity'] = 100 - exp_diff
        potential['Exp_Similarity'] = potential['Exp_Similarity'].clip(lower=0)
        
        # Training partner score
        potential['Training_Score'] = (
            potential['Location_Bonus'] +
            (potential['Skill_Similarity'] * 0.4) +
            (potential['Exp_Similarity'] * 0.3)
        )
        
        # Sort by training score
        potential = potential.sort_values('Training_Score', ascending=False)
        
        results = []
        for _, partner in potential.head(top_k).iterrows():
            results.append({
                'partner_name': partner['Boxer_Name'],
                'gym': partner['Gym'],
                'location': partner['Location'],
                'skill_level': partner['Skill_Level'],
                'win_ratio': partner['Win_Ratio'],
                'total_fights': int(partner['Total_Fights']),
                'training_score': partner['Training_Score'],
                'same_location': partner['Location'] == boxer['Location']
            })
        
        return results

