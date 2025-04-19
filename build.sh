#!/bin/bash

if [ ! -d "data" ]
then
	mkdir data
fi

if [ ! -d "clean" ]
then
	mkdir clean
fi

if [ ! -d "build" ]
then
	mkdir build
fi

for i in $*
do
	case $i in
		"prep")
			echo preping!
			python3 preprocess.py train data/train.csv clean/train_clean.csv
			python3 preprocess.py test  data/test.csv  clean/test_clean.csv
			;;
		"train")
			echo training!
			SUBMIT="build/submit_$(date '+%d-%m_%H-%M-%S').csv"
			python3 model.py clean/train_clean.csv clean/test_clean.csv $SUBMIT
			;;
		"submit")
			echo submiting!
			python3 submit.py
			;;
		$0)
			;;
		*)
			echo nothing!
			;;
	esac
done
