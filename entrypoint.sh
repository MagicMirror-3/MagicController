#!/bin/bash
cd /
mkdir logs
cd /MagicMirror || exit
npm run server &> /logs/mirror_log.txt &
python /MagicController/MagicController.py &> /logs/controller_log.txt &

