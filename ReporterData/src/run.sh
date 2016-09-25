#!/bin/bash

rm -rf /tmp/reports_settings
git clone https://github.com/WikiToLearn/ReportsSettings.git

python data_aggregator.py
