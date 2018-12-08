#!/bin/bash
set -e
if [ ! -s "$1".sig ]; then
	gpg2 -b "$1"
	chmod a-w "$1".sig
fi
