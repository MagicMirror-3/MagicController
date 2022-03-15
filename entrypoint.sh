#!/bin/bash
cd /
mkdir logs
cd /MagicMirror || exit
python /MagicController/MagicController.py > /logs/controller_log.txt &
npm run server > /logs/mirror_log.txt &
