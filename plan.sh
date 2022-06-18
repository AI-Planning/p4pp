#!/bin/bash

# Set the limits so not too much time is spent on finding solutions

lama-first --overall-memory-limit 8G --overall-time-limit 30s --plan-file $1 $2 $3
