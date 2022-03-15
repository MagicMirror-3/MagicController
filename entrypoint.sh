#!/bin/bash
cd /
mkdir logs
python /MagicController/Configuration/load_default_config.py
python /MagicController/MagicController.py > /logs/controller_log.txt &
cd /MagicMirror || exit
npm run server > /logs/mirror_log.txt &
