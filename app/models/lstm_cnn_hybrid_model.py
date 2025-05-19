import tensorflow as tf
from tensorflow.keras.layers import Layer,DepthwiseConv2D,LSTM,MaxPooling2D,Flatten,Dense,Reshape,Average

class LSTMAndCNN4StockForecasting(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # LSTM Layers:
        self.lstm1 = LSTM(units=16, activation='relu', kernel_initializer='he_uniform', return_sequences=True)
        self.lstm2 = LSTM(units=32, activation='relu', kernel_initializer='he_uniform', return_sequences=True)
        self.lstm3 = LSTM(units=64, activation='relu', kernel_initializer='he_uniform', return_sequences=False)

        # CNN Layers:
        self.cnn1 = DepthwiseConv2D(16, (1, 1), depth_multiplier=1, activation='relu',
                                    depthwise_initializer='he_uniform', padding='same')
        self.max1 = MaxPooling2D((2, 2), padding='same')

        self.cnn2 = DepthwiseConv2D(32, (1, 1), depth_multiplier=1, activation='relu',
                                    depthwise_initializer='he_uniform', padding='same')
        self.max2 = MaxPooling2D((2, 2), padding='same')

        self.flatten = Flatten()
        self.dense1 = Dense(256, activation='relu', kernel_initializer='he_uniform')
        self.dense2 = Dense(64, activation='relu', kernel_initializer='he_uniform')



    def call(self, x):
        # LSTM build:
        out1 = self.lstm1(x)
        out1 = self.lstm2(out1)
        out1 = self.lstm3(out1)

        # CNN build:
        out2 = Reshape((x.shape[1], x.shape[2], -1))(x)
        out2 = self.cnn1(out2)
        out2 = self.max1(out2)
        out2 = self.cnn2(out2)
        out2 = self.max2(out2)
        out2 = self.flatten(out2)
        out2 = self.dense1(out2)
        out2 = self.dense2(out2)

        # Combine Model
        final = Average()([out1, out2])
        return final

    def compute_output_shape(self, input_shape):
        return (input_shape[0], 64)



