# Blandet Machine Learning projekter

> "binance_data_gatherer.py" er et godt eksempel på hvordan man bruger en API når den virker.

> "bitmex_data_gatherer.py" er et "godt" eksempel på hvilke bjerge man må bestige hvis man enormt gerne vil have data imen ens API adgang er blokeret.

> "cryptornn.py" er mit seneste passion-project hvor jeg har forsøgt at lave en model til at forudsige fremtidige prisændringer på crypto-markedet, primært i 1M, 3M og 5M interval.

Mine bedste resultater er på nuværende tidspunkt en model der forudsiger 3 minutter frem i tiden på 60 minutters data mellem BNB (Binance Coin) og USDT (Tether - Cryptoverdenens svar på en fiat-analog) med en val_acc på ~64%. Det er en LSTM model (CuDNNLSTM) med opsætningen som fremgår i "cryptornn.py"
