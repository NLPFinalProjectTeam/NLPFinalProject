import os, sys

for i in range(1, 11):
	cmd = "python ask.py a%d.txt 1000" % i
	os.system(cmd)