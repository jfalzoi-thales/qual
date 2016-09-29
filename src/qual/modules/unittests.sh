#!/bin/sh

qatest sanity $@ 2>&1 | tee /tmp/unittests.txt
