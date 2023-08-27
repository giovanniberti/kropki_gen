import sys

from generator import generate_kropki
from ken import encode_constraints, retrieve_kropki_solution


def main():
    sampled_constraints = int(sys.argv[1])

    solution = retrieve_kropki_solution()
    kropki, full_solution = generate_kropki(sampled_constraints)

    print(encode_constraints(kropki))
    print(encode_constraints(full_solution))


if __name__ == '__main__':
    main()
