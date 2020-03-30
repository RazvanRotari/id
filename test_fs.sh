#!/usr/bin/bash
set -x
set -e
if [ -z ${INTERNAL_RUN+x} ]; then
	PIDS=""
	if [ -d "test_data" ]; then
		rm -r "test_data"
	fi
	mkdir "test_data"

	for x in {0..10}; do
		export INTERNAL_RUN="${x}"
		./test_fs.sh &
		PIDS="${PIDS} $!"
	done
	echo $PIDS
	while kill -0 $PIDS 2> /dev/null; do sleep 1; done;
	cat test_data/* > test_data/merge.log
	sort_count=`cat merge.log | sort | uniq | wc -l | cut -d" " -f 1`
	merge_count=`wc -l merge.log | cut -d" " -f 1`
	if [ ${sort_count}=${merge_count} ]; then
		echo "Test succesfull"
	else
		echo "Test failed"
	fi
else
	for x in {0..10000}; do
		cat id_fs/id >> "test_data/id_${INTERNAL_RUN}.log"
	done
fi


