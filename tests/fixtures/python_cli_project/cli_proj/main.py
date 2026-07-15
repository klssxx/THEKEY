import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    args = parser.parse_args()
    print('hello ' + args.name)


if __name__ == '__main__':
    main()
