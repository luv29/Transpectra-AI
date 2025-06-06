from fastapi import APIRouter, HTTPException
from app.schemas import ProductInput
from app.models.model_loader import encoder, model
import pandas as pd
import numpy as np
import tensorflow as tf

router = APIRouter()

features = [
    'Stock Level Thresholds',
    'Seasonality',
    'Market Changes',
    'Product Type',
    'Lead time (in days)',
    'Supplier Reliabilty',
    'Stock Handing Efficiency',
    'Product Costs(In Rs.)',
    'Maximum discount offered (in percentage)',
    'Products Expiry (in months)',
    'Backorders',
    'Bulk orders (By customers)'
]

dates = [
    '2023-12-01', '2024-01-01', '2024-02-01', '2024-03-01',
    '2024-04-01', '2024-05-01', '2024-06-01', '2024-07-01',
    '2024-08-01', '2024-09-01', '2024-10-01', '2024-11-01', '2024-12-01'
]

months = [
    'Dec-2023', 'Jan-2024,', 'Feb-2024', 'Mar-2024',
    'Apr-2024', 'May-2024', 'Jun-2024', 'Jul-2024',
    'Aug-2024', 'Sep-2024', 'Oct-2024', 'Nov-2024', 'Dec-2024'
]

dataset = pd.read_csv('app/models/dataset.csv')

def stock_forecast(products: list[str]) -> dict:
    """
    Predicts the future stock requirement for a list of products.

    Args:
        products: A list of product names for which stock forecasts are needed.

    Returns:
        dict: A dictionary mapping each product name to its predicted stock requirement.
              Example: {"Widget A": 120, "Gadget B": 85}

    This function uses a hybrid deep learning model (LSTM + CNN + Prophet) to forecast
    monthly stock needs. It processes the numerical and categorical data for each product
    and returns a rounded integer prediction of required stock levels.
    """
    print(products)
    data = dataset[dataset[dataset.columns[0]].isin(products)]

    # data = pd.DataFrame(products)
    data_cat = data.select_dtypes(include=['object'])
    data_num = data.select_dtypes(exclude=['object'])
    data_cat_encoded = encoder.transform(data_cat)
    data_cat_encoded = pd.DataFrame(data_cat_encoded, columns=data_cat.columns)
    data_X = pd.concat([data_num, data_cat_encoded], axis=1).astype('float32')

    data_by_month = []
    for i in range(len(data_X)):
        exp = []
        for j in range(13):
            cols = ['Product Name', 'Product Category']
            cols.append(f"Stocks Required-{dates[j]}")
            for feat in features:
                cols.append(feat + f'-{months[j]}')
            inst = list(data_X.loc[i, cols])
            exp.append(inst)
        data_by_month.append(exp)
    lstm_cnn_hybrid_data = np.array(data_by_month)

    prophet_model_data = data_X[[f'Stocks Required-{date}' for date in dates]].to_numpy()

    predictions = model.predict([prophet_model_data, lstm_cnn_hybrid_data])
    pred = tf.round(predictions)
    pred = tf.cast(pred, tf.int32)

    return {product: int(stock) for product, stock in zip(data['Product Name'], pred)}

@router.post("/predict_stock")
def predict_stock(input_data: ProductInput):
    try:
        return stock_forecast(input_data.products)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
