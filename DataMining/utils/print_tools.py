#!/usr/bin/env python3.5
import sys

#TODO documentation CHARGE BAR
def conditionalPrintCB(start, end, pos, text, guard):
	if guard == True:
		# printed size		
		p_size = 50
		size = end - start
		step = size / p_size
		#n points to print		
		np = pos / step
		
		done_message = ' 100 % Done '		


		p_bar = '['
		if pos < size-1:
			for i in range(0,p_size):
				if i <= np:
					p_bar += '='	
				else:
					p_bar += ' '
			p_bar += ']'
		else:
			head = 0
			tail = 0
			if (p_size - len(done_message)) % 2 == 0:
				head = tail = int((p_size - len(done_message))/2)
			else:
				head = int((p_size - len(done_message))/2)
				tail = head + 1

			for i in range(0,head):
				p_bar += '='	
			p_bar += done_message		
			for i in range(0,tail):
				p_bar += '='	
			p_bar += ']'					

		print(p_bar+' '+text, end='\r')
		


#TODO documentation
def conditionalPrint_inline(text, guard):
	if guard == True:
		print(text, end='')

#TODO documentation
def conditionalPrint(text, guard):
	if guard == True:
		print(text)


def main(args):
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))
