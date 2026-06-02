# services/improvement_advisor.py
import pandas as pd

class ImprovementAdvisor:
    def __init__(self, data):
        self.data = data
    
    def get_gym_suggestions(self, gym_name, location):
        """Get 5 personalized improvement suggestions for a specific gym"""
        if self.data.empty:
            return []
        
        gym_data = self.data[(self.data['Gym'] == gym_name) & (self.data['Location'] == location)]
        if gym_data.empty:
            return []
        
        location_data = self.data[self.data['Location'] == location]
        
        suggestions = []
        
        # Calculate gym metrics
        total_wins = gym_data['Wins'].sum()
        total_losses = gym_data['Losses'].sum()
        total_fights = total_wins + total_losses
        win_ratio = total_wins / total_fights if total_fights > 0 else 0
        total_boxers = len(gym_data['Boxer_Name'].unique())
        
        # Compare with other gyms in location
        other_gyms_win_ratios = []
        other_gyms_boxer_counts = []
        for other_gym in location_data['Gym'].unique():
            if other_gym != gym_name:
                other_gym_data = location_data[location_data['Gym'] == other_gym]
                other_wins = other_gym_data['Wins'].sum()
                other_losses = other_gym_data['Losses'].sum()
                other_fights = other_wins + other_losses
                if other_fights > 0:
                    other_gyms_win_ratios.append(other_wins / other_fights)
                other_gyms_boxer_counts.append(len(other_gym_data['Boxer_Name'].unique()))
        
        avg_other_win_ratio = sum(other_gyms_win_ratios) / len(other_gyms_win_ratios) if other_gyms_win_ratios else 0
        avg_other_boxers = sum(other_gyms_boxer_counts) / len(other_gyms_boxer_counts) if other_gyms_boxer_counts else 0
        
        # Gender-specific analysis
        male_boxers = gym_data[gym_data['Gender'] == 'Male']
        female_boxers = gym_data[gym_data['Gender'] == 'Female']
        male_win_ratio = 0
        female_win_ratio = 0
        
        if not male_boxers.empty:
            male_wins = male_boxers['Wins'].sum()
            male_losses = male_boxers['Losses'].sum()
            male_fights = male_wins + male_losses
            male_win_ratio = male_wins / male_fights if male_fights > 0 else 0
        
        if not female_boxers.empty:
            female_wins = female_boxers['Wins'].sum()
            female_losses = female_boxers['Losses'].sum()
            female_fights = female_wins + female_losses
            female_win_ratio = female_wins / female_fights if female_fights > 0 else 0
        
        # Weight class diversity
        weight_classes = gym_data['Weight_Class'].unique()
        weight_class_count = len(weight_classes)
        
        # Year consistency
        year_performance = gym_data.groupby('Year').apply(
            lambda x: x['Wins'].sum() / (x['Wins'].sum() + x['Losses'].sum() + 1e-8)
        )
        performance_std = year_performance.std() if len(year_performance) > 1 else 0
        
        # Generate personalized suggestions (exactly 5)
        
        # Suggestion 1: Win ratio improvement
        if win_ratio < avg_other_win_ratio and avg_other_win_ratio > 0:
            gap = (avg_other_win_ratio - win_ratio) * 100
            suggestions.append(f"Improve overall win ratio by {gap:.1f}% to match location average. Focus on strategic fight preparation and technique refinement.")
        elif win_ratio < 0.5:
            suggestions.append(f"Current win ratio is {win_ratio*100:.1f}%. Implement advanced training programs focusing on defensive techniques and counter-attacking strategies.")
        elif win_ratio >= 0.7:
            suggestions.append(f"Excellent win ratio of {win_ratio*100:.1f}%! Maintain this performance by continuing current training methods and mentoring newer boxers.")
        else:
            suggestions.append(f"Win ratio is {win_ratio*100:.1f}%. Focus on consistency in training and match preparation to reach the next level.")
        
        # Suggestion 2: Team size
        if total_boxers < avg_other_boxers and avg_other_boxers > 0:
            suggestions.append(f"Recruit {int(avg_other_boxers - total_boxers)} more boxers to match location average. Larger teams provide better training partners and competitive environment.")
        elif total_boxers < 5:
            suggestions.append(f"Small team size ({total_boxers} boxers). Expand recruitment to build team depth and create more competitive training scenarios.")
        elif total_boxers > 15:
            suggestions.append(f"Large team ({total_boxers} boxers). Focus on personalized coaching for each boxer to maximize individual potential.")
        else:
            suggestions.append(f"Team size is good ({total_boxers} boxers). Focus on quality training sessions and individual skill development.")
        
        # Suggestion 3: Gender performance
        if not male_boxers.empty and not female_boxers.empty:
            if abs(male_win_ratio - female_win_ratio) > 0.15:
                if male_win_ratio < female_win_ratio:
                    suggestions.append(f"Male boxers' win ratio ({male_win_ratio*100:.1f}%) is lower than female ({female_win_ratio*100:.1f}%). Provide specialized coaching for male boxers focusing on technique and conditioning.")
                else:
                    suggestions.append(f"Female boxers' win ratio ({female_win_ratio*100:.1f}%) is lower than male ({male_win_ratio*100:.1f}%). Enhance training programs specifically designed for female boxers.")
            else:
                suggestions.append(f"Gender performance is balanced. Continue equal focus on both male and female training programs.")
        elif not male_boxers.empty:
            suggestions.append(f"Only male boxers present. Consider recruiting female boxers to diversify the team and expand gym's competitive reach.")
        elif not female_boxers.empty:
            suggestions.append(f"Only female boxers present. Consider recruiting male boxers to create a more diverse and competitive training environment.")
        
        # Suggestion 4: Weight class diversity
        if weight_class_count < 3:
            suggestions.append(f"Limited weight class representation ({weight_class_count} classes). Diversify by recruiting boxers across different weight classes to strengthen overall gym performance.")
        elif weight_class_count >= 5:
            suggestions.append(f"Good weight class diversity ({weight_class_count} classes). Focus on specialized training for each weight class to maximize performance.")
        else:
            suggestions.append(f"Moderate weight class coverage ({weight_class_count} classes). Consider adding 1-2 more weight classes to expand competitive opportunities.")
        
        # Suggestion 5: Performance consistency or fight volume
        if performance_std > 0.2 and len(year_performance) > 1:
            suggestions.append(f"Inconsistent performance across years (variance: {performance_std:.2f}). Develop long-term training plans to maintain consistent results year-over-year.")
        elif total_fights < 20:
            suggestions.append(f"Low fight volume ({total_fights} total fights). Increase competition participation to gain experience and improve win rates through more match practice.")
        elif total_fights > 50:
            suggestions.append(f"High activity level ({total_fights} fights). Focus on recovery and quality over quantity - ensure boxers have adequate rest between competitions.")
        else:
            suggestions.append(f"Good fight volume ({total_fights} fights). Balance competition frequency with training quality to optimize performance.")
        
        # Ensure exactly 5 suggestions
        return suggestions[:5]
    
    def get_boxer_suggestions(self, boxer_name, location=None):
        """Get 5 personalized improvement suggestions for a specific boxer"""
        if self.data.empty:
            return []
        
        boxer_data = self.data[self.data['Boxer_Name'] == boxer_name]
        if location and location != "All Locations":
            boxer_data = boxer_data[boxer_data['Location'] == location]
        
        if boxer_data.empty:
            return []
        
        suggestions = []
        
        # Calculate boxer metrics
        total_wins = boxer_data['Wins'].sum()
        total_losses = boxer_data['Losses'].sum()
        total_fights = total_wins + total_losses
        win_ratio = total_wins / total_fights if total_fights > 0 else 0
        
        # Get boxer details
        gym_name = boxer_data['Gym'].iloc[0] if not boxer_data.empty else 'Unknown'
        boxer_gender = boxer_data['Gender'].iloc[0] if not boxer_data.empty else 'Unknown'
        weight_class = boxer_data['Weight_Class'].iloc[0] if not boxer_data.empty else 'Unknown'
        
        # Compare with other boxers in same gym
        gym_data = self.data[self.data['Gym'] == gym_name]
        gym_boxers_win_ratios = []
        for other_boxer in gym_data['Boxer_Name'].unique():
            if other_boxer != boxer_name:
                other_boxer_data = gym_data[gym_data['Boxer_Name'] == other_boxer]
                other_wins = other_boxer_data['Wins'].sum()
                other_losses = other_boxer_data['Losses'].sum()
                other_fights = other_wins + other_losses
                if other_fights > 0:
                    gym_boxers_win_ratios.append(other_wins / other_fights)
        
        avg_gym_win_ratio = sum(gym_boxers_win_ratios) / len(gym_boxers_win_ratios) if gym_boxers_win_ratios else 0
        
        # Year progression
        year_progression = boxer_data.groupby('Year').apply(
            lambda x: x['Wins'].sum() / (x['Wins'].sum() + x['Losses'].sum() + 1e-8)
        )
        years = sorted(boxer_data['Year'].unique())
        improving = False
        if len(years) >= 2:
            recent_ratio = year_progression[years[-1]] if years[-1] in year_progression.index else 0
            earlier_ratio = year_progression[years[0]] if years[0] in year_progression.index else 0
            improving = recent_ratio > earlier_ratio
        
        # Generate personalized suggestions (exactly 5)
        
        # Suggestion 1: Win ratio
        if win_ratio < 0.4:
            suggestions.append(f"Win ratio is {win_ratio*100:.1f}%. Focus on fundamental techniques, defensive skills, and consistent training to improve performance.")
        elif win_ratio < 0.6:
            suggestions.append(f"Win ratio is {win_ratio*100:.1f}%. Work on advanced strategies, counter-punching, and mental preparation to reach elite level.")
        elif win_ratio >= 0.75:
            suggestions.append(f"Excellent win ratio of {win_ratio*100:.1f}%! Maintain this by focusing on consistency, recovery, and mentoring others.")
        else:
            suggestions.append(f"Good win ratio of {win_ratio*100:.1f}%. Push to next level by refining technique and increasing fight frequency.")
        
        # Suggestion 2: Comparison with gym average
        if avg_gym_win_ratio > 0 and win_ratio < avg_gym_win_ratio:
            gap = (avg_gym_win_ratio - win_ratio) * 100
            suggestions.append(f"Performance is {gap:.1f}% below gym average. Train with top performers in your gym and seek additional coaching sessions.")
        elif avg_gym_win_ratio > 0 and win_ratio > avg_gym_win_ratio:
            suggestions.append(f"Performing above gym average! Share techniques with teammates and consider competing at higher levels.")
        else:
            suggestions.append(f"Focus on consistent training schedule and sparring with diverse opponents to improve skills.")
        
        # Suggestion 3: Fight volume
        if total_fights < 5:
            suggestions.append(f"Limited fight experience ({total_fights} fights). Increase competition participation to gain experience and build confidence.")
        elif total_fights < 15:
            suggestions.append(f"Moderate experience ({total_fights} fights). Continue competing regularly while focusing on quality preparation for each match.")
        elif total_fights > 30:
            suggestions.append(f"Extensive experience ({total_fights} fights). Focus on recovery, technique refinement, and strategic fight selection.")
        else:
            suggestions.append(f"Good fight experience ({total_fights} fights). Balance competition with training to optimize performance.")
        
        # Suggestion 4: Year progression
        if len(years) >= 2:
            if improving:
                suggestions.append(f"Showing improvement over time! Continue current training approach and set higher goals for upcoming competitions.")
            else:
                suggestions.append(f"Performance needs improvement over time. Review training methods, consider new coaching approaches, and focus on weaknesses.")
        else:
            suggestions.append(f"Build long-term training plan focusing on skill development, conditioning, and strategic fight preparation.")
        
        # Suggestion 5: Weight class and specialization
        if total_fights > 0:
            weight_class_performance = boxer_data.groupby('Weight_Class').apply(
                lambda x: x['Wins'].sum() / (x['Wins'].sum() + x['Losses'].sum() + 1e-8)
            )
            if len(weight_class_performance) > 1:
                suggestions.append(f"Competing in multiple weight classes. Consider specializing in one weight class where performance is strongest.")
            else:
                suggestions.append(f"Specialized in {weight_class} weight class. Focus on mastering techniques specific to this weight class and maintaining optimal weight.")
        else:
            suggestions.append(f"Focus on building fundamental boxing skills, conditioning, and finding the optimal weight class for your physique.")
        
        # Ensure exactly 5 suggestions
        return suggestions[:5]
    
    def get_comprehensive_analysis(self, location, gender="Both"):
        """Get comprehensive analysis and recommendations for all gyms in a location"""
        if self.data.empty:
            return {}
        
        location_data = self.data[self.data['Location'] == location]
        
        analysis = {
            'location': location,
            'total_gyms': len(location_data['Gym'].unique()),
            'total_boxers': len(location_data['Boxer_Name'].unique()),
            'gym_analysis': [],
            'overall_recommendations': []
        }
        
        # Analyze each gym
        for gym in location_data['Gym'].unique():
            gym_data = location_data[location_data['Gym'] == gym]
            
            gym_analysis = {
                'gym_name': gym,
                'total_boxers': len(gym_data['Boxer_Name'].unique()),
                'total_wins': gym_data['Wins'].sum(),
                'total_losses': gym_data['Losses'].sum(),
                'win_ratio': gym_data['Wins'].sum() / (gym_data['Wins'].sum() + gym_data['Losses'].sum() + 1e-8),
                'strengths': [],
                'weaknesses': [],
                'recommendations': []
            }
            
            # Gender analysis
            male_boxers = gym_data[gym_data['Gender'] == 'Male']
            female_boxers = gym_data[gym_data['Gender'] == 'Female']
            
            if not male_boxers.empty:
                male_win_ratio = male_boxers['Wins'].sum() / (male_boxers['Wins'].sum() + male_boxers['Losses'].sum() + 1e-8)
                gym_analysis['male_win_ratio'] = male_win_ratio
            
            if not female_boxers.empty:
                female_win_ratio = female_boxers['Wins'].sum() / (female_boxers['Wins'].sum() + female_boxers['Losses'].sum() + 1e-8)
                gym_analysis['female_win_ratio'] = female_win_ratio
            
            # Identify strengths and weaknesses
            if gym_analysis['win_ratio'] > 0.6:
                gym_analysis['strengths'].append("High overall win ratio")
            elif gym_analysis['win_ratio'] < 0.4:
                gym_analysis['weaknesses'].append("Low overall win ratio")
            
            if gym_analysis['total_boxers'] > 10:
                gym_analysis['strengths'].append("Large team size")
            elif gym_analysis['total_boxers'] < 5:
                gym_analysis['weaknesses'].append("Small team size")
            
            # Generate recommendations
            if gym_analysis['win_ratio'] < 0.5:
                gym_analysis['recommendations'].append("Focus on improving training techniques and strategy")
            
            if len(gym_data['Weight_Class'].unique()) < 3:
                gym_analysis['recommendations'].append("Diversify weight class representation")
            
            if 'male_win_ratio' in gym_analysis and 'female_win_ratio' in gym_analysis:
                if gym_analysis['male_win_ratio'] < gym_analysis['female_win_ratio']:
                    gym_analysis['recommendations'].append("Provide specialized coaching for male boxers")
                else:
                    gym_analysis['recommendations'].append("Enhance training programs for female boxers")
            
            analysis['gym_analysis'].append(gym_analysis)
        
        # Generate overall recommendations for the location
        total_win_ratio = location_data['Wins'].sum() / (location_data['Wins'].sum() + location_data['Losses'].sum() + 1e-8)
        
        if total_win_ratio < 0.5:
            analysis['overall_recommendations'].append("Location-wide training improvement needed")
        
        if analysis['total_gyms'] < 3:
            analysis['overall_recommendations'].append("Consider establishing more gyms in this area")
        
        return analysis




