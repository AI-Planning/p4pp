#!/bin/bash

# Set the limits so not too much time is spent on finding solutions
echo lama --alias seq-opt-merge-and-shrink --overall-memory-limit 8G --overall-time-limit $4 --plan-file $1 $2 $3
lama --alias seq-opt-merge-and-shrink --overall-memory-limit 8G --overall-time-limit $4 --plan-file $1 $2 $3
