#!/bin/sh

grep "_id_: " $1 | sed -E "s/_id_: \`(\w+)\`$/\1/" | sed -E 's/(.+)/"\1"/' | sed 'H; 1h; $!d; x; s/\n/, /g'

