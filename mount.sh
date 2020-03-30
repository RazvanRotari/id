#!/usr/bin/bash
pgrep -f id_fs.py | xargs kill
if [ ! -d "id_fs" ]; then 
	mkdir id_fs
fi
./id_fs.py id_fs
cat id_fs/id
