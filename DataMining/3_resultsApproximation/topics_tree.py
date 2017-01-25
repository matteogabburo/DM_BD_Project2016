#!/usr/bin/env python3.5
import sys

# WHAT TOPICS TREE HAS TO DO
# 1. Take the min s
# 2. Using the min s, divide the db (topics db) into sectors that are multiple of s (for now 4*s)
# 3. Merge the topics using a merge function
# 4. Save the computed topics into the db


def main(args):

	if len(args) == 1 or args[1] == '--h':
		print('Parameters : [ hostname, port, s ]')
		return 0



	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
