#!/bin/bash

git clone https://github.com/WikiToLearn/ReportsMetadata.git /tmp/reports_settings

python -u data_aggregator.py
