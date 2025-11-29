# # app.py
# from flask import Flask
# import webbrowser
# import threading
# import time
# from config import Config
# from models.data_loader import EnhancedDataLoader
# from routes.main_routes import MainRoutes

# def open_browser():
#     """Wait a moment for the server to start, then open the browser"""
#     time.sleep(1.5)
#     webbrowser.open_new('http://127.0.0.1:5000/')

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
    
#     # Initialize data loader
#     data_loader = EnhancedDataLoader()
    
#     # Setup routes
#     main_routes = MainRoutes(app, data_loader)
    
#     return app

# if __name__ == "__main__":
#     app = create_app()
    
#     # Start browser opening in a separate thread
#     threading.Thread(target=open_browser).start()
    
#     # Run the Flask app
#     app.run(debug=app.config['DEBUG'], port=5000)


















# app.py (Recommended)
from flask import Flask
import webbrowser
import threading
import time
import os
from config import Config
from models.data_loader import EnhancedDataLoader
from routes.main_routes import MainRoutes

def open_browser():
    """Open browser after delay, only in main process"""
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        return
        
    def _open():
        time.sleep(3)  # Increased delay
        webbrowser.open_new_tab("http://127.0.0.1:5000/")
    
    threading.Thread(target=_open, daemon=True).start()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize data loader
    data_loader = EnhancedDataLoader()
    
    # Setup routes
    main_routes = MainRoutes(app, data_loader)
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    print("🚀 Starting Boxing Analytics Dashboard...")
    print("📊 Dashboard will open automatically in your browser")
    print("🛑 Press CTRL+C to stop the server")
    
    # Open browser only once
    open_browser()
    
    # Run the app
    app.run(debug=True, use_reloader=True, port=5000)









