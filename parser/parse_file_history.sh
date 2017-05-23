#!/bin/sh

for file in $(git ls-files $1)
do
  echo {\"${file}\": [$(git log --pretty=format:"%h" ${file} | sed -e 's/^/\"/;s/$/\"/' | paste -sd ",")]}
done
