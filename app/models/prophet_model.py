from prophet import Prophet
import tensorflow as tf
import pandas as pd
import numpy as np
from tensorflow.keras.layers import Layer

class ProphetModel(Layer):
    def __init__(self, dates, prediction_date, output_columns_selection, **kwargs):
        super().__init__(**kwargs)
        self.dates = dates
        self.prediction_date = prediction_date
        self.output_columns_selection = output_columns_selection
        self.ds = pd.DataFrame(self.dates, columns=['ds'])

    def get_prediction_from_prophet_model(self, inst):
        y = np.array(inst)
        y = pd.DataFrame(y, columns=['y'])
        inp = pd.concat([self.ds, y], axis=1)
        model = Prophet()
        model.fit(inp)
        pred_inp = pd.DataFrame([self.prediction_date], columns=['ds'])
        out = model.predict(pred_inp)
        out = out[self.output_columns_selection]
        out = np.array(out)
        return out

    def call(self, inputs):
        def get_prediction(inst):
            out = tf.py_function(
                func=self.get_prediction_from_prophet_model,
                inp=[inst],
                Tout=tf.float32
            )
            out = tf.reshape(out, (len(self.output_columns_selection),))
            return out

        outputs = tf.map_fn(
            get_prediction,
            inputs,
            fn_output_signature=tf.TensorSpec(
                shape=(len(self.output_columns_selection),), dtype=tf.float32
            ),
        )
        return outputs

    def compute_output_shape(self, input_shape):
        return (input_shape[0], len(self.output_columns_selection))

    def get_config(self):
        config = super().get_config()
        config.update(
            {
                'dates': self.dates,
                'prediction_date': self.prediction_date,
                'output_columns_selection': self.output_columns_selection
            }
        )
        return config
