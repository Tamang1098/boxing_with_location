# config.py
import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "data", "enhanced_boxing_data.csv")
    SECRET_KEY = 'your-secret-key-here'
    DEBUG = True