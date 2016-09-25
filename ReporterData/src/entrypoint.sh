#!/bin/bash

git clone https://github.com/WikiToLearn/ReportsMetadata.git /tmp/reports_settings

python data_aggregator.py

cron -f
