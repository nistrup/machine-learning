import pandas as pd
from collections import deque
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, CuDNNLSTM, BatchNormalization
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.callbacks import ModelCheckpoint, ModelCheckpoint
import time
from sklearn import preprocessing

SEQ_LEN = 35
FUTURE_PERIOD_PREDICT = 3
RATIOS_TO_PREDICT = ["BNBUSDT"]
EPOCHS = 10
BATCH_SIZE = 32
# DATA_LENGTH = 100000
KLINE_SIZE = "5M"

dense_layers = [16, 32, 64]
lstm_layers = [32, 64, 128]
dropout_rates = [0.1, 0.2, 0.3]

def classify(current, future):
	change_percent = ((float(future) - float(current)) / float(current)) * 100
	if change_percent > float(0.55):
		return 1
	else:
		return 0

def preprocess_df(df):
    df = df.drop("future", 1)  # irrelevant i preprocessing, kun brugt til at danne "targets"

    for col in df.columns:
        if col != "target":  # normaliserer alle kolonner i data ... med undtagelse af vores "targets" da de allerede antager 0 og 1 som værdier
            df[col] = df[col].pct_change() # Vi er ikke interesseret i de nomielle værdier af priserne, blot den procentvise ændring.
            
            df[df==np.inf]=np.nan
            df.dropna(inplace=True)

            df[col] = preprocessing.scale(df[col].values)  # skalerer alle værdier til tal mellem 0 og 1 med sklearns preprocessing funktion.

    df.dropna(inplace=True)  # bare for at være på den sikre side!


    sequential_data = []
    prev_days = deque(maxlen=SEQ_LEN)  # deque funktionen fra collections holder styr på at len(prev_days) == 60 når nye værdier kommer ind i sekvensen.

    for i in df.values:
        prev_days.append([n for n in i[:-1]])  # danner sekvens med alle kolonner ud over "target"
        if len(prev_days) == SEQ_LEN:
            sequential_data.append([np.array(prev_days), i[-1]])  # omdanner vores SEQ_LEN - sekvens som en np.array til vores sekvens array

    random.shuffle(sequential_data)  # blander data

    buys = []
    sells = []

    # nedenstående deler vores sekventielle data op i sekvenser der er buys eller sells ud fra vores "target"
    for seq, target in sequential_data:
        if target == 0:
            sells.append([seq, target])
        elif target == 1: 
            buys.append([seq, target])

    random.shuffle(buys)  # shuffle igen
    random.shuffle(sells)  #  shuffle igen igen

    lower = min(len(buys), len(sells))

    buys = buys[:lower]  # sikre at data er 50/50 fordelt for at undgå bias
    sells = sells[:lower]  # se ovenstående

    sequential_data = buys+sells  # danner nu sekventiel data array
    random.shuffle(sequential_data)  # blander en sidste gang så modellen ikke ser alle buys og sells i forlængelse af hinanden

    X = []
    y = []

    for seq, target in sequential_data:
        X.append(seq)  # danner features
        y.append(target)  # danner labels / targets

    return np.array(X), y

for RATIO_TO_PREDICT in RATIOS_TO_PREDICT:
	for dense_layer in dense_layers:
		for lstm_layer in lstm_layers:
			for dropout_rate in dropout_rates:

				# dynamisk navngivning så der kan holdes styr på de forskellige modeller
				NAME = f"{RATIO_TO_PREDICT}-{dense_layer}-Dense-{lstm_layer}-LSTM-{dropout_rate}-Dropout-{int(time.time())}"

				ratios = ["BTCUSDT", "BNBUSDT"]

				# danner vores dataframe ud fra data i .csv format
				main_df = pd.DataFrame()
				for ratio in ratios:
					datapath = f"crypto_data/{KLINE_SIZE}/{ratio}-Binance-2018.csv"
					df = pd.read_csv(datapath)
					df = df.rename(columns={"close": f"{ratio}_close", "volume": f"{ratio}_volume"})
					df.set_index('time', inplace=True)
					# df = df[[f"{ratio}_close",f"{ratio}_volume"]]

					if len(main_df) == 0:
						main_df = df
					else:
						main_df = main_df.join(df)

				# danner vores target kolonne
				main_df['future'] = main_df[f"{RATIO_TO_PREDICT}_close"].shift(-FUTURE_PERIOD_PREDICT)
				main_df['target'] = list(map(classify, main_df[f"{RATIO_TO_PREDICT}_close"], main_df['future']))

				# splitter data op i training og validation data, i dette tilfælde 90/10
				times = sorted(main_df.index.values)
				last_pct = times[-int(0.10*len(times))]
				validation_main_df = main_df[(main_df.index >= last_pct)]
				main_df = main_df[(main_df.index < last_pct)]
				
				# smider dem igennem vores preprocessing funktion		
				train_x, train_y = preprocess_df(main_df)
				validation_x, validation_y = preprocess_df(validation_main_df)

				# print(f"train data: {len(train_x)} validation: {len(validation_x)}")
				# print(f"Dont buys: {train_y.count(0)}, buys: {train_y.count(1)}")
				# print(f"VALIDATION Dont buys: {validation_y.count(0)}, buys: {validation_y.count(1)}")

				# laver skelettet til vores model
				model = Sequential()

				model.add(CuDNNLSTM(lstm_layer, input_shape=(train_x.shape[1:]), return_sequences=True))
				model.add(Dropout(dropout_rate))
				model.add(BatchNormalization())

				model.add(CuDNNLSTM(lstm_layer, input_shape=(train_x.shape[1:]), return_sequences=True))
				model.add(Dropout(dropout_rate))
				model.add(BatchNormalization())

				model.add(CuDNNLSTM(lstm_layer, input_shape=(train_x.shape[1:])))
				model.add(Dropout(dropout_rate))
				model.add(BatchNormalization())

				model.add(Dense(dense_layer, activation='relu'))
				model.add(Dropout(dropout_rate))

				model.add(Dense(2, activation='softmax'))

				opt = tf.keras.optimizers.Adam(lr=0.001, decay=1e-6)

				model.compile(loss='sparse_categorical_crossentropy',
							  optimizer=opt,
							  metrics=['accuracy'])

				tensorboard = TensorBoard(log_dir=f'logs/{NAME}')

				# laver model checkpoint for at gemme modelen med højest val_acc over epoch'erne
				filepath = "models/" + f"{RATIO_TO_PREDICT}---{dense_layer}-Dense-{lstm_layer}-LSTM-{dropout_rate}-Dropout---" + "epoch-{epoch:02d}-val_acc-{val_acc:.2f}.hdf5"  # unique file name that will include the epoch and the validation acc for that epoch
				checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max') # saves only the best ones

				# der trænes.
				history = model.fit(
					train_x, train_y,
					batch_size=BATCH_SIZE,
					epochs=EPOCHS,
					validation_data=(validation_x, validation_y),
					callbacks=[tensorboard, checkpoint])