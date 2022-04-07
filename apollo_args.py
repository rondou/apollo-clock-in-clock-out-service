import argparse


def start():
    print('Start')


parser = argparse.ArgumentParser(description='Main')
subparsers = parser.add_subparsers(help='Sub-command')

parser_start = subparsers.add_parser('start', help='start the service')
parser_start.set_defaults(func=start)


if __name__ == '__main__':
    args = parser.parse_args()
    args.func()
