#!/bin/bash

if [ -z "$*" ]; then
	echo "[INFO]: Usage: [prep] [train [nn]]"
fi

if [ ! -d "data" ]; then
	mkdir data
fi

if [ ! -d "clean" ]; then
	mkdir clean
fi

if [ ! -d "build" ]; then
	mkdir build
fi

echoval() {
	echo $*
	eval $*
}

for i in $*
do
	case $i in
		"prep")
			echo preping!
			echoval python3 preprocess.py train data/train.csv clean/train_clean.csv
			echoval python3 preprocess.py test  data/test.csv  clean/test_clean.csv
			;;
		"train")
			echo training!
			SUBMIT="build/submit_$(date '+%d-%m_%H-%M-%S').csv"
			SCRIPT="model.py"
			LAST=$(($#))
			if [[ "nn" == ${!LAST} ]]
			then
				SCRIPT="nn.py"
			fi
			echoval python3 $SCRIPT clean/train_clean.csv clean/test_clean.csv $SUBMIT
			if [[ $? ]]; then 
				echoval kaggle competitions submit -c cancer-detection-v1 -f $SUBMIT -m $(basename $SUBMIT)
			fi
			;;
		$0)
			;;
		*)
			;;
	esac
done
