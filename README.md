# ML & Crypto? - et 'recurrent neural network'-projekt

**binance_data_gatherer.py** er et godt eksempel på hvordan man bruger en API fra en 'børs' når den virker.

**bitmex_data_gatherer.py** er et ~~godt~~ eksempel på hvilke bjerge man må bestige hvis man enormt gerne vil have data imen ens API adgang er blokeret.

**cryptornn.py** er mit seneste passion-project hvor jeg har forsøgt at lave en model til at forudsige fremtidige prisændringer på crypto-markedet, primært i 1M, 3M og 5M interval.

En af de bedre resultater er en model der forudsiger 3 minutter frem i tiden på 60 minutters data på BNB (Binance Coin) og USDT (Tether - Cryptoverdenens svar på en fiat-analog) med en val_acc på ~**61%**. Det viste sig at ekstra data fra flere valuta end den man faktisk forsøger at forudsige blot gav støj. Det er en RNN model primært med LSTM (CuDNNLSTM) layers med opsætningen som fremgår i **cryptornn.py**.

Her er et eksempel på de modeller jeg trænede til den pågældende ticker på Binance:

![alt text](https://i.imgur.com/kHO7pEg.png)
