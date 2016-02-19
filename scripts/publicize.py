"""This script makes a public JSON at static/qfile.json from the main json"""

import json
import sys
import os
from collections import OrderedDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PUBLIC_ATTRS = ('title', 'score')

def publicize(data1):
	data2 = []
	for q1 in data1:
		q2 = OrderedDict()
		for attr in PUBLIC_ATTRS:
			if attr in q1:
				q2[attr] = q1[attr]
		data2.append(q2)
	return data2

def main(fname):
	ifile = open(fname)
	ofile = open(os.path.join(BASE_DIR, 'static', 'qfile.json'), 'w')
	json.dump(publicize(json.load(ifile)), ofile, indent=4)

if __name__=="__main__":
	main(sys.argv[1])
