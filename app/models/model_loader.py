import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import CustomObjectScope
from app.models.prophet_model import ProphetModel
from app.models.lstm_cnn_hybrid_model import LSTMAndCNN4StockForecasting

with open('app/models/encoder.pkl', 'rb') as f:
    encoder = joblib.load(f)

with CustomObjectScope({
    'ProphetModel': ProphetModel,
    'LSTMAndCNN4StockForecasting': LSTMAndCNN4StockForecasting
}):
    model = load_model('app/models/ulip_model_stock_forecasting.h5')
