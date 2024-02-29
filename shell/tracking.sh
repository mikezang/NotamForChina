#!/bin/bash

./webtracking.sh http://tn.adlantis.jp/iPhoneAppOwner/adlantis-iphone-sdk -o AdLantis.html
./webtracking.sh https://www.adcl.medibaad.com/sdk/iphone.zip -o MedibaAd.html
./webtracking.sh https://manage.amoad.com/sdk/iphone.zip -o AMoAd.html

./webtracking.sh http://www.traders.co.jp/domestic_stocks/domestic_market/market_s/market_s.asp -o MartketEvent.html
./webtracking.sh "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewContentsUserReviews?pageNumber=0&sortOrdering=4&type=Purple+Software&mt=8&id=408671117" -o MarketEventInAppStore.html
