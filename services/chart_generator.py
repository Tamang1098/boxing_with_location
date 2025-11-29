



# services/chart_generator.py
import plotly.express as px
import plotly.io as pio
import pandas as pd
import random

class ChartGenerator:
    @staticmethod
    def generate_chart(filtered_data, mode, diagram_type, selected_boxers, selected_gyms, year, location, gender="Both"):
        """Generate the appropriate chart based on parameters"""
        if filtered_data.empty:
            return None
        
        # Apply filtering for "All Locations" to show only top performers
        if location == "All Locations":
            filtered_data = ChartGenerator._filter_top_performers(filtered_data, mode)
        
        if diagram_type == "Bar Chart":
            return ChartGenerator._generate_bar_chart(filtered_data, mode, selected_boxers, selected_gyms, year, location, gender)
        elif diagram_type == "Pie Chart":
            return ChartGenerator._generate_pie_chart(filtered_data, mode, selected_boxers, selected_gyms, year, location, gender)
        elif diagram_type == "Line Chart":
            return ChartGenerator._generate_line_chart(filtered_data, mode, selected_boxers, selected_gyms, location, gender)
        elif diagram_type == "Scatter Plot":
            return ChartGenerator._generate_scatter_plot(filtered_data, mode, selected_boxers, selected_gyms, location, gender)
        
        return None
    
    @staticmethod
    def _filter_top_performers(filtered_data, mode):
        """Filter to show only top performers when All Locations is selected"""
        if mode == "Gym":
            # Get top gym from each location (based on win ratio)
            top_gyms = []
            for location_name in filtered_data['Location'].unique():
                location_data = filtered_data[filtered_data['Location'] == location_name]
                gym_stats = []
                for gym in location_data['Gym'].unique():
                    gym_data = location_data[location_data['Gym'] == gym]
                    total_wins = gym_data['Wins'].sum()
                    total_losses = gym_data['Losses'].sum()
                    total_fights = total_wins + total_losses
                    win_ratio = total_wins / total_fights if total_fights > 0 else 0
                    gym_stats.append({
                        'gym': gym, 
                        'win_ratio': win_ratio, 
                        'wins': total_wins,
                        'location': location_name
                    })
                
                if gym_stats:
                    # Find gym with highest win ratio
                    top_gym = max(gym_stats, key=lambda x: x['win_ratio'])
                    top_gyms.append(top_gym['gym'])
            
            return filtered_data[filtered_data['Gym'].isin(top_gyms)]
        
        elif mode == "Boxer":
            # Get top boxer from each gym in each location (separate for male and female)
            top_boxers = []
            for location_name in filtered_data['Location'].unique():
                location_data = filtered_data[filtered_data['Location'] == location_name]
                for gym in location_data['Gym'].unique():
                    gym_data = location_data[location_data['Gym'] == gym]
                    
                    # Get top male boxer
                    male_boxers = gym_data[gym_data['Gender'] == 'Male']
                    if not male_boxers.empty:
                        male_stats = []
                        for boxer in male_boxers['Boxer_Name'].unique():
                            boxer_data = male_boxers[male_boxers['Boxer_Name'] == boxer]
                            total_wins = boxer_data['Wins'].sum()
                            total_losses = boxer_data['Losses'].sum()
                            total_fights = total_wins + total_losses
                            win_ratio = total_wins / total_fights if total_fights > 0 else 0
                            male_stats.append({
                                'boxer': boxer, 
                                'win_ratio': win_ratio, 
                                'wins': total_wins,
                                'gender': 'Male',
                                'gym': gym,
                                'location': location_name
                            })
                        
                        if male_stats:
                            top_male = max(male_stats, key=lambda x: x['win_ratio'])
                            top_boxers.append(top_male['boxer'])
                    
                    # Get top female boxer
                    female_boxers = gym_data[gym_data['Gender'] == 'Female']
                    if not female_boxers.empty:
                        female_stats = []
                        for boxer in female_boxers['Boxer_Name'].unique():
                            boxer_data = female_boxers[female_boxers['Boxer_Name'] == boxer]
                            total_wins = boxer_data['Wins'].sum()
                            total_losses = boxer_data['Losses'].sum()
                            total_fights = total_wins + total_losses
                            win_ratio = total_wins / total_fights if total_fights > 0 else 0
                            female_stats.append({
                                'boxer': boxer, 
                                'win_ratio': win_ratio, 
                                'wins': total_wins,
                                'gender': 'Female',
                                'gym': gym,
                                'location': location_name
                            })
                        
                        if female_stats:
                            top_female = max(female_stats, key=lambda x: x['win_ratio'])
                            top_boxers.append(top_female['boxer'])
            
            return filtered_data[filtered_data['Boxer_Name'].isin(top_boxers)]
        
        return filtered_data
    
    @staticmethod
    def _get_color_sequence(chart_type, mode, location):
        """Get different color sequences for different chart types and modes"""
        # Generate distinct colors for same location
        if location != "All Locations":
            if mode == "Boxer":
                # Different colors for each boxer in same location
                return px.colors.qualitative.Vivid
            else:
                # Different colors for each gym in same location  
                return px.colors.qualitative.Bold
        else:
            # For "All Locations", use location-based colors
            if chart_type == "bar":
                if mode == "Boxer":
                    return px.colors.qualitative.Vivid
                else:
                    return px.colors.qualitative.Bold
            
            elif chart_type == "pie":
                if mode == "Boxer":
                    return px.colors.qualitative.Pastel
                else:
                    return px.colors.qualitative.Set3
            
            elif chart_type == "line":
                return px.colors.qualitative.Dark24
            
            elif chart_type == "scatter":
                return px.colors.qualitative.Light24
        
        return px.colors.qualitative.Set1
    
    @staticmethod
    def _generate_bar_chart(filtered_data, mode, selected_boxers, selected_gyms, year, location, gender):
        if mode == "Boxer":
            return ChartGenerator._generate_boxer_bar_chart(filtered_data, selected_boxers, year, location, gender)
        else:
            return ChartGenerator._generate_gym_bar_chart(filtered_data, year, location)
    
    @staticmethod
    def _generate_boxer_bar_chart(filtered_data, selected_boxers, year, location, gender):
        # Filter by gender if specified
        if gender != "Both":
            filtered_data = filtered_data[filtered_data['Gender'] == gender]
        
        boxers_to_show = selected_boxers if selected_boxers else filtered_data['Boxer_Name'].unique()[:12]
        
        boxer_data_list = []
        for boxer in boxers_to_show:
            boxer_data = filtered_data[filtered_data['Boxer_Name'] == boxer]
            if not boxer_data.empty:
                if year == "All Years":
                    total_wins = boxer_data['Wins'].sum()
                    total_losses = boxer_data['Losses'].sum()
                    total_fights = total_wins + total_losses
                    win_ratio = total_wins / total_fights if total_fights > 0 else 0
                else:
                    year_data = boxer_data[boxer_data['Year'] == year]
                    total_wins = year_data['Wins'].sum()
                    total_losses = year_data['Losses'].sum()
                    total_fights = total_wins + total_losses
                    win_ratio = total_wins / total_fights if total_fights > 0 else 0
                
                gym_name = boxer_data['Gym'].iloc[0] if not boxer_data.empty else 'Unknown Gym'
                location_name = boxer_data['Location'].iloc[0] if not boxer_data.empty else 'Unknown'
                boxer_gender = boxer_data['Gender'].iloc[0] if not boxer_data.empty else 'Unknown'
                
                if location == "All Locations":
                    display_name = f"{boxer} ({gym_name}, {location_name})"
                    color_by = 'Location'
                else:
                    display_name = f"{boxer} ({gym_name})"
                    color_by = 'Boxer'  # Use boxer for color differentiation in same location
                
                boxer_data_list.append({
                    'Boxer': display_name,
                    'Original_Name': boxer,
                    'Win_Ratio': win_ratio,
                    'Wins': total_wins,
                    'Losses': total_losses,
                    'Gym': gym_name,
                    'Location': location_name,
                    'Gender': boxer_gender
                })
        
        if boxer_data_list:
            plot_df = pd.DataFrame(boxer_data_list)
            plot_df = plot_df.sort_values('Win_Ratio', ascending=True)
            
            if location == "All Locations":
                title = "🥊 Top Boxers from Each Location"
                color_column = 'Location'
            else:
                title = f"🥊 Boxer Performance - {location}"
                color_column = 'Original_Name'  # Different color for each boxer
            
            fig = px.bar(
                plot_df, 
                x='Win_Ratio', 
                y='Boxer',
                orientation='h',
                labels={"Boxer": "Boxer (Gym)", "Win_Ratio": "Win Ratio"},
                title=title,
                hover_data=['Wins', 'Losses', 'Gym', 'Location', 'Gender'],
                color=color_column,
                color_discrete_sequence=ChartGenerator._get_color_sequence("bar", "Boxer", location)
            )
            fig.update_layout(
                xaxis_tickangle=0,
                yaxis={'categoryorder': 'total ascending'},
                height=max(400, len(boxer_data_list) * 40)
            )
            return fig
        return None

    @staticmethod
    def _generate_gym_bar_chart(filtered_data, year, location):
        gym_data = []
        
        # Process each gym
        for gym in filtered_data['Gym'].unique():
            gym_filtered = filtered_data[filtered_data['Gym'] == gym]
            total_wins = gym_filtered['Wins'].sum()
            total_losses = gym_filtered['Losses'].sum()
            total_fights = total_wins + total_losses
            win_ratio = total_wins / total_fights if total_fights > 0 else 0
            
            location_name = gym_filtered['Location'].iloc[0] if not gym_filtered.empty else 'Unknown'
            
            # For "All Locations", show gym with location in name (format like second image)
            if location == "All Locations":
                display_name = f"{gym} ({location_name})"
                short_display = f"{gym} ({location_name})"
            else:
                display_name = gym
                short_display = gym
            
            gym_data.append({
                'Gym': display_name, 
                'Short_Gym': short_display,
                'Win_Ratio': win_ratio,
                'Wins': total_wins,
                'Losses': total_losses,
                'Location': location_name,
                'Total_Fights': total_fights
            })
        
        if gym_data:
            gym_df = pd.DataFrame(gym_data)
            gym_df = gym_df.sort_values('Win_Ratio', ascending=True)
            
            if location == "All Locations":
                title = "🏆 Best Gym from Each Location"
                color_column = 'Location'
                # Format like second image: "Gymname (Location) - WinRatio%"
                gym_df['Display'] = gym_df.apply(
                    lambda x: f"{x['Short_Gym']} - {x['Win_Ratio']:.1%}", axis=1
                )
            else:
                title = f"🏋️ Gym Performance - {location}"
                color_column = 'Gym'  # Different color for each gym in same location
                gym_df['Display'] = gym_df['Short_Gym']
            
            fig = px.bar(
                gym_df, 
                x='Win_Ratio', 
                y='Display',
                orientation='h',
                labels={"Display": "Gym", "Win_Ratio": "Win Ratio"},
                title=title,
                hover_data=['Wins', 'Losses', 'Location', 'Total_Fights'],
                color=color_column,
                color_discrete_sequence=ChartGenerator._get_color_sequence("bar", "Gym", location)
            )
            
            # Update layout for better appearance
            fig.update_layout(
                xaxis_tickangle=0,
                yaxis={'categoryorder': 'total ascending'},
                height=max(300, len(gym_data) * 40),
                showlegend=location == "All Locations"
            )
            
            # Format hover template
            fig.update_traces(
                hovertemplate="<b>%{y}</b><br>Win Ratio: %{x:.3f}<br>Wins: %{customdata[0]}<br>Losses: %{customdata[1]}<br>Location: %{customdata[2]}<br>Total Fights: %{customdata[3]}<extra></extra>"
            )
            
            return fig
        return None

    @staticmethod
    def _generate_pie_chart(filtered_data, mode, selected_boxers, selected_gyms, year, location, gender):
        if mode == "Boxer":
            return ChartGenerator._generate_boxer_pie_chart(filtered_data, selected_boxers, year, location, gender)
        else:
            return ChartGenerator._generate_gym_pie_chart(filtered_data, year, location)
    
    @staticmethod
    def _generate_boxer_pie_chart(filtered_data, selected_boxers, year, location, gender):
        # Filter by gender if specified
        if gender != "Both":
            filtered_data = filtered_data[filtered_data['Gender'] == gender]
            
        pie_data = []
        boxers_to_show = selected_boxers if selected_boxers else filtered_data['Boxer_Name'].unique()[:8]
        
        for boxer in boxers_to_show:
            boxer_data = filtered_data[filtered_data['Boxer_Name'] == boxer]
            if not boxer_data.empty:
                if year == "All Years":
                    total_wins = boxer_data['Wins'].sum()
                    total_losses = boxer_data['Losses'].sum()
                    total_fights = total_wins + total_losses
                    win_ratio = total_wins / total_fights if total_fights > 0 else 0
                else:
                    year_data = boxer_data[boxer_data['Year'] == year]
                    total_wins = year_data['Wins'].sum()
                    total_losses = year_data['Losses'].sum()
                    total_fights = total_wins + total_losses
                    win_ratio = total_wins / total_fights if total_fights > 0 else 0
                
                gym_name = boxer_data['Gym'].iloc[0] if not boxer_data.empty else 'Unknown Gym'
                location_name = boxer_data['Location'].iloc[0] if not boxer_data.empty else 'Unknown'
                boxer_gender = boxer_data['Gender'].iloc[0] if not boxer_data.empty else 'Unknown'
                
                if location == "All Locations":
                    label = f"{boxer} ({gym_name}, {location_name})"
                    color_by = 'Location'
                else:
                    label = f"{boxer} ({gym_name})"
                    color_by = 'Boxer'
                
                pie_data.append({
                    'Label': label, 
                    'Original_Name': boxer,
                    'Win_Ratio': win_ratio, 
                    'Gym': gym_name, 
                    'Location': location_name,
                    'Gender': boxer_gender,
                    'Total_Fights': total_fights
                })
        
        if pie_data:
            pie_df = pd.DataFrame(pie_data)
            
            if location == "All Locations":
                title = "🥊 Top Boxers Distribution (All Locations)"
                color_column = 'Location'
            else:
                title = f"🥊 Boxer Win Distribution - {location}"
                color_column = 'Original_Name'
            
            fig = px.pie(
                pie_df, 
                values='Win_Ratio', 
                names='Label', 
                title=title,
                hover_data=['Win_Ratio', 'Gym', 'Location', 'Total_Fights', 'Gender'],
                color=color_column,
                color_discrete_sequence=ChartGenerator._get_color_sequence("pie", "Boxer", location)
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                insidetextorientation='radial',
                hovertemplate="<b>%{label}</b><br>Win Ratio: %{value:.3f}<br>Gym: %{customdata[1]}<br>Location: %{customdata[2]}<br>Total Fights: %{customdata[3]}<br>Gender: %{customdata[4]}<extra></extra>"
            )
            
            fig.update_layout(
                uniformtext_minsize=10,
                uniformtext_mode='hide',
                showlegend=True,
                height=500
            )
            
            return fig
        return None

    @staticmethod
    def _generate_gym_pie_chart(filtered_data, year, location):
        pie_data = []
        for gym in filtered_data['Gym'].unique():
            gym_filtered = filtered_data[filtered_data['Gym'] == gym]
            total_wins = gym_filtered['Wins'].sum()
            total_losses = gym_filtered['Losses'].sum()
            total_fights = total_wins + total_losses
            win_ratio = total_wins / total_fights if total_fights > 0 else 0
            
            location_name = gym_filtered['Location'].iloc[0] if not gym_filtered.empty else 'Unknown'
            
            if location == "All Locations":
                display_name = f"{gym} ({location_name}) - {win_ratio:.1%}"
                color_by = 'Location'
            else:
                display_name = f"{gym} - {win_ratio:.1%}"
                color_by = 'Gym'
            
            pie_data.append({
                'Gym': display_name, 
                'Original_Gym': gym,
                'Win_Ratio': win_ratio, 
                'Wins': total_wins, 
                'Losses': total_losses,
                'Location': location_name
            })
        
        pie_df = pd.DataFrame(pie_data)
        
        if location == "All Locations":
            title = "🏆 Best Gyms Distribution (All Locations)"
            color_column = 'Location'
        else:
            title = f"🏋️ Gym Win Distribution - {location}"
            color_column = 'Original_Gym'
        
        fig = px.pie(
            pie_df, 
            values='Win_Ratio', 
            names='Gym', 
            title=title,
            hover_data=['Wins', 'Losses', 'Location', 'Original_Gym'],
            color=color_column,
            color_discrete_sequence=ChartGenerator._get_color_sequence("pie", "Gym", location)
        )
        fig.update_traces(
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>Win Ratio: %{value:.3f}<br>Wins: %{customdata[0]}<br>Losses: %{customdata[1]}<br>Location: %{customdata[2]}<extra></extra>"
        )
        return fig

    @staticmethod
    def _generate_line_chart(filtered_data, mode, selected_boxers, selected_gyms, location, gender):
        if filtered_data.empty:
            return None
            
        if mode == "Boxer":
            return ChartGenerator._generate_boxer_line_chart(filtered_data, selected_boxers, location, gender)
        else:
            return ChartGenerator._generate_gym_line_chart(filtered_data, selected_gyms, location)
    
    @staticmethod
    def _generate_boxer_line_chart(filtered_data, selected_boxers, location, gender):
        # Filter by gender if specified
        if gender != "Both":
            filtered_data = filtered_data[filtered_data['Gender'] == gender]
            
        boxers_to_show = selected_boxers if selected_boxers else filtered_data['Boxer_Name'].unique()[:6]
        
        boxer_progress = []
        for boxer in boxers_to_show:
            boxer_data = filtered_data[filtered_data['Boxer_Name'] == boxer]
            for year_val in sorted(boxer_data['Year'].unique()):
                year_data = boxer_data[boxer_data['Year'] == year_val]
                total_wins = year_data['Wins'].sum()
                total_losses = year_data['Losses'].sum()
                total_fights = total_wins + total_losses
                win_ratio = total_wins / total_fights if total_fights > 0 else 0
                
                gym_name = year_data['Gym'].iloc[0] if not year_data.empty else 'Unknown Gym'
                location_name = year_data['Location'].iloc[0] if not year_data.empty else 'Unknown'
                boxer_gender = year_data['Gender'].iloc[0] if not year_data.empty else 'Unknown'
                
                if location == "All Locations":
                    display_name = f"{boxer} ({gym_name}, {location_name})"
                    color_by = 'Location'
                else:
                    display_name = f"{boxer} ({gym_name})"
                    color_by = 'Boxer'
                
                boxer_progress.append({
                    'Boxer': display_name,
                    'Original_Name': boxer,
                    'Year': year_val,
                    'Win_Ratio': win_ratio,
                    'Wins': total_wins,
                    'Losses': total_losses,
                    'Gym': gym_name,
                    'Location': location_name,
                    'Gender': boxer_gender
                })
        
        if boxer_progress:
            progress_df = pd.DataFrame(boxer_progress)
            
            if location == "All Locations":
                title = "📈 Top Boxers Progress (All Locations)"
                color_column = 'Location'
            else:
                title = f"📈 Boxer Progress - {location}"
                color_column = 'Original_Name'
            
            fig = px.line(
                progress_df, 
                x="Year", 
                y="Win_Ratio", 
                color=color_column,
                title=title,
                hover_data=['Wins', 'Losses', 'Gym', 'Location', 'Gender'],
                markers=True,
                color_discrete_sequence=ChartGenerator._get_color_sequence("line", "Boxer", location)
            )
            fig.update_layout(hovermode='x unified')
            return fig
        return None

    @staticmethod
    def _generate_gym_line_chart(filtered_data, selected_gyms, location):
        gyms_to_show = selected_gyms if selected_gyms else filtered_data['Gym'].unique()[:6]
        
        gym_progress = []
        for gym in gyms_to_show:
            gym_data = filtered_data[filtered_data['Gym'] == gym]
            location_name = gym_data['Location'].iloc[0] if not gym_data.empty else 'Unknown'
            
            if location == "All Locations":
                display_name = f"{gym} ({location_name})"
                color_by = 'Location'
            else:
                display_name = gym
                color_by = 'Gym'
            
            for year_val in sorted(gym_data['Year'].unique()):
                year_data = gym_data[gym_data['Year'] == year_val]
                total_wins = year_data['Wins'].sum()
                total_losses = year_data['Losses'].sum()
                total_fights = total_wins + total_losses
                win_ratio = total_wins / total_fights if total_fights > 0 else 0
                
                gym_progress.append({
                    'Gym': display_name,
                    'Original_Gym': gym,
                    'Year': year_val,
                    'Win_Ratio': win_ratio,
                    'Wins': total_wins,
                    'Losses': total_losses,
                    'Location': location_name
                })
        
        if gym_progress:
            progress_df = pd.DataFrame(gym_progress)
            
            if location == "All Locations":
                title = "📈 Best Gyms Performance (All Locations)"
                color_column = 'Location'
            else:
                title = f"📈 Gym Performance - {location}"
                color_column = 'Original_Gym'
            
            fig = px.line(
                progress_df, 
                x="Year", 
                y="Win_Ratio", 
                color=color_column,
                title=title,
                hover_data=['Wins', 'Losses', 'Location'],
                markers=True,
                color_discrete_sequence=ChartGenerator._get_color_sequence("line", "Gym", location)
            )
            fig.update_layout(hovermode='x unified')
            return fig
        return None

    @staticmethod
    def _generate_scatter_plot(filtered_data, mode, selected_boxers, selected_gyms, location, gender):
        if mode == "Boxer":
            return ChartGenerator._generate_boxer_scatter_plot(filtered_data, selected_boxers, location, gender)
        else:
            return ChartGenerator._generate_gym_scatter_plot(filtered_data, location)
    
    @staticmethod
    def _generate_boxer_scatter_plot(filtered_data, selected_boxers, location, gender):
        # Filter by gender if specified
        if gender != "Both":
            filtered_data = filtered_data[filtered_data['Gender'] == gender]
            
        scatter_data = []
        boxers_to_show = selected_boxers if selected_boxers else filtered_data['Boxer_Name'].unique()[:15]
        
        for boxer in boxers_to_show:
            boxer_data = filtered_data[filtered_data['Boxer_Name'] == boxer]
            if not boxer_data.empty:
                total_wins = boxer_data['Wins'].sum()
                total_losses = boxer_data['Losses'].sum()
                total_fights = total_wins + total_losses
                win_ratio = total_wins / total_fights if total_fights > 0 else 0
                
                gym_name = boxer_data['Gym'].iloc[0] if not boxer_data.empty else 'Unknown'
                location_name = boxer_data['Location'].iloc[0] if not boxer_data.empty else 'Unknown'
                boxer_gender = boxer_data['Gender'].iloc[0] if not boxer_data.empty else 'Unknown'
                
                if location == "All Locations":
                    display_name = f"{boxer} ({gym_name}, {location_name})"
                    color_by = 'Location'
                else:
                    display_name = f"{boxer} ({gym_name})"
                    color_by = 'Boxer'
                
                scatter_data.append({
                    'Boxer': display_name,
                    'Original_Name': boxer,
                    'Total_Fights': total_fights,
                    'Win_Ratio': win_ratio,
                    'Wins': total_wins,
                    'Gym': gym_name,
                    'Location': location_name,
                    'Gender': boxer_gender
                })
        
        if scatter_data:
            scatter_df = pd.DataFrame(scatter_data)
            
            if location == "All Locations":
                title = "🎯 Top Boxers Performance (All Locations)"
                color_column = 'Location'
            else:
                title = f"🎯 Boxer Performance - {location}"
                color_column = 'Original_Name'
            
            fig = px.scatter(
                scatter_df, 
                x='Total_Fights', 
                y='Win_Ratio',
                size='Wins',
                color=color_column,
                hover_data=['Boxer', 'Wins', 'Gym', 'Gender'],
                title=title,
                labels={
                    'Total_Fights': 'Total Fights (Experience)',
                    'Win_Ratio': 'Win Ratio (Performance)'
                },
                color_discrete_sequence=ChartGenerator._get_color_sequence("scatter", "Boxer", location)
            )
            return fig
        return None

    @staticmethod
    def _generate_gym_scatter_plot(filtered_data, location):
        scatter_data = []
        for gym in filtered_data['Gym'].unique():
            gym_data = filtered_data[filtered_data['Gym'] == gym]
            total_wins = gym_data['Wins'].sum()
            total_losses = gym_data['Losses'].sum()
            total_fights = total_wins + total_losses
            win_ratio = total_wins / total_fights if total_fights > 0 else 0
            total_boxers = len(gym_data['Boxer_Name'].unique())
            location_name = gym_data['Location'].iloc[0] if not gym_data.empty else 'Unknown'
            
            if location == "All Locations":
                display_name = f"{gym} ({location_name})"
                color_by = 'Location'
            else:
                display_name = gym
                color_by = 'Gym'
            
            scatter_data.append({
                'Gym': display_name,
                'Original_Gym': gym,
                'Total_Fights': total_fights,
                'Win_Ratio': win_ratio,
                'Total_Boxers': total_boxers,
                'Avg_Fights_Per_Boxer': total_fights / total_boxers if total_boxers > 0 else 0,
                'Location': location_name
            })
        
        if scatter_data:
            scatter_df = pd.DataFrame(scatter_data)
            
            if location == "All Locations":
                title = "🎯 Best Gyms Performance (All Locations)"
                color_column = 'Location'
            else:
                title = f"🎯 Gym Performance - {location}"
                color_column = 'Original_Gym'
            
            fig = px.scatter(
                scatter_df, 
                x='Total_Fights', 
                y='Win_Ratio',
                size='Total_Boxers',
                color=color_column,
                hover_data=['Gym', 'Avg_Fights_Per_Boxer'],
                title=title,
                labels={
                    'Total_Fights': 'Total Gym Fights',
                    'Win_Ratio': 'Gym Win Ratio'
                },
                color_discrete_sequence=ChartGenerator._get_color_sequence("scatter", "Gym", location)
            )
            return fig
        return None

    @staticmethod
    def chart_to_html(fig):
        """Convert plotly figure to HTML"""
        return pio.to_html(fig, full_html=False) if fig else "<p>No data available for the selected filters.</p>"