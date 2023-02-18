import argparse
import sys

from sha256 import SHA256

parser = argparse.ArgumentParser()
parser.add_argument("string", type=str)
parser.add_argument("-d", "--debug", action="store_true")


def main():
    args = parser.parse_args()

    try:
        hash_ = SHA256(args.debug).hash(args.string)
        print(hash_)
    except Exception as exc:
        sys.exit(exc)


if __name__ == "__main__":
    main()
