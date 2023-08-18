import sys
import time
from pprint import pprint

from generator import generate_kropki
from ken import encode_constraints


def main():
    sampled_constraints = int(sys.argv[1])

    kropki, full_solution = generate_kropki(sampled_constraints)

    print(encode_constraints(kropki))
    print(encode_constraints(full_solution))


if __name__ == '__main__':
    main()
