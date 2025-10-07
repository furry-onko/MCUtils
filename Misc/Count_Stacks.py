#!/usr/bin/env python3
import sys

def main() -> None:
	argv: list = sys.argv[1:]
	items: int = 0

	while True:
		if len(argv) == 0:
			try:
				items = int(input("Amount of items: "))
			except ValueError:
				print("Invalid value")
				exit(1)
		elif len(argv) == 1:
			try:
				items = int(argv[0])
			except ValueError:
				print("Invalid value")
				exit(1)
		else:
			print("Too many arguments")
			exit(1)

		if not items:
			print("Please enter a number of items.")
			exit(1)

		if items < 0:
			print("Amount of items cannot be negative.")
			exit(1)

		else:
			break

	item, stack, chest = 0, 0, 0

	while items > 0:
		if items >= 64:
			items -= 64
			stack += 1
		else:
			item += 1
			items -= 1

		if stack >= 27:
			stack -= 27
			chest += 1

	max_result_length: int = len( str( max(item, stack, chest)) )

	print(f"+-------+{'-' * max_result_length}+")
	print(f"|Items  |{item}{' ' * (max_result_length - len(str(item)))}|")
	print(f"|Stacks |{stack}{' ' * (max_result_length - len(str(stack)))}|")
	print(f"|Chests |{chest}{' ' * (max_result_length - len(str(chest)))}|")
	print(f"+-------+{'-' * max_result_length}+")
	print("\nMade by @furry_onko")

if __name__ == "__main__": main()