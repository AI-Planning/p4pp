#!/bin/bash

# Set the limits so not too much time is spent on finding solutions
echo lama-first --overall-memory-limit 8G --overall-time-limit $4 --plan-file $1 $2 $3
lama-first --overall-memory-limit 8G --overall-time-limit $4 --plan-file $1 $2 $3
