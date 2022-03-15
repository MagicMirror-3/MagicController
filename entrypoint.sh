#!/bin/bash

cd /MagicMirror || exit
npm run server &> mirror_log.txt &
python /MagicController/MagicController.py &> controller_log.txt &

