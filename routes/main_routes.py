# routes/main_routes.py
from flask import render_template, request, send_file, jsonify
import io
from datetime import datetime
import numpy as np
from models.data_loader import EnhancedDataLoader
from models.gym_recommender import GymRecommender
from models.match_maker import MatchMaker
from services.data_filter import DataFilter
from services.analytics import Analytics
from services.chart_generator import ChartGenerator
from services.improvement_advisor import ImprovementAdvisor


def convert_to_native_types(obj):
    """Convert numpy/pandas types to native Python types for JSON serialization"""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_native_types(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return convert_to_native_types(obj.__dict__)
    else:
        return obj


class MainRoutes:
    def __init__(self, app, data_loader):
        self.app = app
        self.data_loader = data_loader
        self.setup_routes()
    
    def setup_routes(self):
        self.app.add_url_rule('/', 'index', self.index, methods=['GET', 'POST'])
        self.app.add_url_rule('/export_csv', 'export_csv', self.export_csv)
        self.app.add_url_rule('/get_recommendations', 'get_recommendations', self.get_recommendations, methods=['POST'])
        self.app.add_url_rule('/get_improvement_analysis', 'get_improvement_analysis', self.get_improvement_analysis, methods=['POST'])
        self.app.add_url_rule('/get_suggestions', 'get_suggestions', self.get_suggestions, methods=['POST'])
        # Real problem solving endpoints
        # self.app.add_url_rule('/predict_career', 'predict_career', self.predict_career, methods=['POST'])
        self.app.add_url_rule('/find_fair_matches', 'find_fair_matches', self.find_fair_matches, methods=['POST'])
       
    
    def index(self):
        # Get form data
        form_data = self._get_form_data()
        
        # Filter data
        data_filter = DataFilter(self.data_loader.get_data())
        filtered_data = data_filter.apply_filters(form_data)
        
        # Calculate metrics
        kpis = Analytics.calculate_kpis(filtered_data, form_data['mode'])
        win_ratios = Analytics.calculate_win_ratios(
            filtered_data, form_data['mode'], form_data['selected_boxers'], 
            form_data['year'], form_data['diagram_type']
        )
        advanced_stats = Analytics.calculate_advanced_stats(filtered_data, form_data['mode'])
        
        # Generate chart
        chart_generator = ChartGenerator()
        fig = chart_generator.generate_chart(
            filtered_data, form_data['mode'], form_data['diagram_type'],
            form_data['selected_boxers'], form_data['selected_gyms'], 
            form_data['year'], form_data['location']
        )
        graph_html = chart_generator.chart_to_html(fig)
        
        # Get available filters
        available_filters = self.data_loader.get_available_filters()

        # Get gym recommendations
        gym_recommender = GymRecommender(self.data_loader.get_data())
        recommended_gyms = []
        location_gym_details = []
        location_recommendations = {}
        if form_data['location'] != "All Locations":
            all_ranked_gyms = gym_recommender.recommend_gyms_by_location(
                form_data['location'], form_data['gender'], form_data['weight'], limit=None
            )
            recommended_gyms = all_ranked_gyms[:4]
            location_gym_details = all_ranked_gyms
        else:
            for loc in available_filters['locations']:
                if loc == "All Locations":
                    continue
                recs = gym_recommender.recommend_gyms_by_location(
                    loc, form_data['gender'], form_data['weight']
                )
                if recs:
                    location_recommendations[loc] = recs
        
        # Get available boxers
        boxer_filters = form_data.copy()
        boxer_filters['selected_boxers'] = []
        boxer_filters['selected_gyms'] = []
        boxer_filters['gym'] = "All Gyms"
        boxer_filtered_data = data_filter.apply_filters(boxer_filters)
        boxer_location_filter = "All Locations" if form_data['mode'] == "Boxer" else form_data['location']
        boxer_gyms_filter = None if form_data['mode'] == "Boxer" else form_data['selected_gyms']
        available_boxers = data_filter.get_boxers_with_gyms(
            boxer_gyms_filter, form_data['gender'], boxer_location_filter, boxer_filtered_data
        )
        
        return render_template("index.html",
                           locations=available_filters['locations'],
                           gyms=available_filters['gyms'],
                           boxers=available_boxers,
                           years=available_filters['years'],
                           weights=available_filters['weights'],
                           diagram_types=available_filters['diagram_types'],
                           genders=available_filters['genders'],
                           graph_html=graph_html,
                           win_ratios=win_ratios,
                           recommended_gyms=recommended_gyms,
                           location_recommendations=location_recommendations,
                           location_gym_details=location_gym_details,
                           selected_mode=form_data['mode'],
                           selected_gender=form_data['gender'],
                           selected_location=form_data['location'],
                           selected_gyms=form_data['selected_gyms'],
                           selected_boxers=form_data['selected_boxers'],
                           selected_year=form_data['year'],
                           selected_weight=form_data['weight'],
                           selected_diagram=form_data['diagram_type'],
                           boxer_primary=form_data['boxer_primary'],
                           boxer_secondary=form_data['boxer_secondary'],
                           total_boxers=kpis['total_boxers'],
                           total_gyms=kpis['total_gyms'],
                           total_locations=kpis['total_locations'],
                           total_fights=kpis['total_fights'],
                           avg_win_ratio=kpis['avg_win_ratio'],
                           top_performer=kpis['top_performer'],
                           advanced_stats=advanced_stats)
    
    def _get_form_data(self):
        """Extract and format form data"""
        boxer_primary = request.form.get("boxer_primary")
        boxer_secondary = request.form.get("boxer_secondary")
        selected_boxers = request.form.getlist("boxers")
        if boxer_primary or boxer_secondary:
            selected_boxers = [name for name in [boxer_primary, boxer_secondary] if name]
        
        return {
            'mode': request.form.get("mode", "Gym"),
            'gender': request.form.get("gender", "Both"),
            'location': request.form.get("location", "All Locations"),
            'selected_gyms': request.form.getlist("gyms"),
            'selected_boxers': selected_boxers,
            'boxer_primary': boxer_primary,
            'boxer_secondary': boxer_secondary,
            'year': self._parse_year(request.form.get("year", "All Years")),
            'weight': request.form.get("weight", "All"),
            'diagram_type': request.form.get("diagram", "Bar Chart"),
            'gym': request.form.get("gym", "All Gyms")
        }
    
    def _parse_year(self, year_input):
        """Parse year input with All Years handling"""
        if year_input == "All Years":
            return "All Years"
        try:
            return int(year_input)
        except ValueError:
            return "All Years"
    
    def get_recommendations(self):
        """Get gym recommendations for a specific location"""
        data = request.get_json()
        location = data.get('location', 'Boudha')
        gender = data.get('gender', 'Both')
        weight_class = data.get('weight_class', 'All')
        
        gym_recommender = GymRecommender(self.data_loader.get_data())
        recommendations = gym_recommender.recommend_gyms_by_location(location, gender, weight_class)
        
        return jsonify(recommendations)
    
    def get_improvement_analysis(self):
        """Get improvement analysis for a location"""
        data = request.get_json()
        location = data.get('location', 'Boudha')
        gender = data.get('gender', 'Both')
        
        improvement_advisor = ImprovementAdvisor(self.data_loader.get_data())
        analysis = improvement_advisor.get_comprehensive_analysis(location, gender)
        
        return jsonify(analysis)
    
    def get_suggestions(self):
        """Get improvement suggestions for a gym or boxer"""
        data = request.get_json()
        entity_type = data.get('type', 'gym')  # 'gym' or 'boxer'
        entity_name = data.get('name')
        location = data.get('location')
        
        improvement_advisor = ImprovementAdvisor(self.data_loader.get_data())
        
        if entity_type == 'gym':
            suggestions = improvement_advisor.get_gym_suggestions(entity_name, location)
            return jsonify({
                'type': 'gym',
                'name': entity_name,
                'location': location,
                'suggestions': suggestions
            })
        elif entity_type == 'boxer':
            suggestions = improvement_advisor.get_boxer_suggestions(entity_name, location)
            return jsonify({
                'type': 'boxer',
                'name': entity_name,
                'location': location,
                'suggestions': suggestions
            })
        else:
            return jsonify({'error': 'Invalid entity type'}), 400
    
    def export_csv(self):
        """Export filtered data as CSV"""
        form_data = {
            'mode': request.args.get('mode', 'Gym'),
            'gender': request.args.get('gender', 'Both'),
            'location': request.args.get('location', 'All Locations'),
            'selected_gyms': request.args.getlist('gyms'),
            'selected_boxers': request.args.getlist('boxers'),
            'year': request.args.get('year', 'All Years'),
            'weight': request.args.get('weight', 'All')
        }
        
        data_filter = DataFilter(self.data_loader.get_data())
        filtered_data = data_filter.apply_filters(form_data)
        
        # Create CSV in memory
        output = io.StringIO()
        filtered_data.to_csv(output, index=False)
        output.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'boxing_data_export_{timestamp}.csv'
        )
    
    # def predict_boxer_performance(self):
    #     """Predict future performance for a boxer using ML"""
    #     data = request.get_json()
    #     boxer_name = data.get('boxer_name')
    #     future_years = data.get('future_years', 1)
        
    #     if not boxer_name:
    #         return jsonify({'error': 'Boxer name is required'}), 400
        
    #     try:
    #         ml_predictor = MLPredictor(self.data_loader.get_data())
    #         prediction = ml_predictor.predict_boxer_performance(boxer_name, future_years)
            
    #         if prediction:
    #             return jsonify(convert_to_native_types(prediction))
    #         else:
    #             return jsonify({'error': 'Could not generate prediction. Not enough data.'}), 400
    #     except Exception as e:
    #         return jsonify({'error': str(e)}), 500
    
    # def ml_recommend_gyms(self):
    #     """Get ML-based gym recommendations for a boxer"""
    #     data = request.get_json()
    #     boxer_name = data.get('boxer_name')
    #     location = data.get('location', None)
    #     top_k = data.get('top_k', 5)
        
    #     if not boxer_name:
    #         return jsonify({'error': 'Boxer name is required'}), 400
        
    #     try:
    #         ml_recommender = MLGymRecommender(self.data_loader.get_data())
    #         recommendations = ml_recommender.recommend_gyms_for_boxer(boxer_name, location, top_k)
            
    #         return jsonify(convert_to_native_types({
    #             'boxer_name': boxer_name,
    #             'recommendations': recommendations
    #         }))
    #     except Exception as e:
    #         return jsonify({'error': str(e)}), 500
    
    # def detect_anomalies(self):
    #     """Detect underperforming boxers and gyms"""
    #     data = request.get_json()
    #     entity_type = data.get('type', 'all')  # 'boxers', 'gyms', or 'all'
        
    #     try:
    #         detector = AnomalyDetector(self.data_loader.get_data())
            
    #         result = {}
    #         if entity_type in ['boxers', 'all']:
    #             result['underperforming_boxers'] = detector.detect_underperforming_boxers()
            
    #         if entity_type in ['gyms', 'all']:
    #             result['underperforming_gyms'] = detector.detect_underperforming_gyms()
            
    #         return jsonify(convert_to_native_types(result))
    #     except Exception as e:
    #         return jsonify({'error': str(e)}), 500
    
    # def get_ml_insights(self):
    #     """Get comprehensive ML insights"""
    #     try:
    #         detector = AnomalyDetector(self.data_loader.get_data())
    #         insights = detector.get_insights()
            
    #         # Add prediction insights
    #         ml_predictor = MLPredictor(self.data_loader.get_data())
    #         top_predictions = ml_predictor.predict_all_boxers_next_year()
    #         insights['top_predicted_performers'] = top_predictions[:10]  # Top 10
            
    #         return jsonify(convert_to_native_types(insights))
    #     except Exception as e:
    #         return jsonify({'error': str(e)}), 500
    
    # def predict_career(self):
    #     """Predict boxer career trajectory"""
    #     data = request.get_json()
    #     boxer_name = data.get('boxer_name')
        
    #     if not boxer_name:
    #         return jsonify({'error': 'Boxer name is required'}), 400
        
    #     try:
    #         predictor = CareerPredictor(self.data_loader.get_data())
    #         prediction = predictor.predict_career_trajectory(boxer_name)
            
    #         if prediction:
    #             # Get similar successful boxers
    #             similar = predictor.find_similar_successful_boxers(boxer_name, top_k=3)
    #             prediction['similar_successful_boxers'] = similar
                
    #             return jsonify(convert_to_native_types(prediction))
    #         else:
    #             return jsonify({'error': 'Could not generate career prediction. Not enough data.'}), 400
    #     except Exception as e:
    #         return jsonify({'error': str(e)}), 500
    
    def find_fair_matches(self):
        """Find fair matches for a boxer"""
        data = request.get_json()
        boxer_name = data.get('boxer_name')
        top_k = data.get('top_k', 5)
        
        if not boxer_name:
            return jsonify({'error': 'Boxer name is required'}), 400
        
        try:
            match_maker = MatchMaker(self.data_loader.get_data())
            matches = match_maker.find_fair_matches(boxer_name, top_k)
            
            return jsonify(convert_to_native_types({
                'boxer_name': boxer_name,
                'matches': matches
            }))
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # def find_training_partners(self):
    #     """Find training partners for a boxer"""
    #     data = request.get_json()
    #     boxer_name = data.get('boxer_name')
    #     top_k = data.get('top_k', 5)
        
    #     if not boxer_name:
    #         return jsonify({'error': 'Boxer name is required'}), 400
        
    #     try:
    #         match_maker = MatchMaker(self.data_loader.get_data())
    #         partners = match_maker.find_training_partners(boxer_name, top_k)
            
    #         return jsonify(convert_to_native_types({
    #             'boxer_name': boxer_name,
    #             'training_partners': partners
    #         }))
    #     except Exception as e:
    #         return jsonify({'error': str(e)}), 500





