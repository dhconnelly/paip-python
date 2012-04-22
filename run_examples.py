import argparse
import logging
import os
import sys


parser = argparse.ArgumentParser(description='Run example AI programs.')
parser.add_argument('--log', action='store_true', help='Turn on logging')


def main():
    print 'Please choose an example to run:'
    modules = []
    for i, name in enumerate(discover_modules('paip/examples')):
        __import__(name)
        module = sys.modules[name]
        modules.append(module)
        print '%d\t%s' % (i, module.__name__)
    while True:
        try:
            choice = raw_input('>> ')
            if not choice:
                continue
            ind = int(choice)
        except ValueError:
            print 'That is not a valid option.  Please try again.'
            continue
        except EOFError:
            print 'Goodbye.'
            return
        try:
            module = modules[ind]
        except IndexError:
            print 'That is not a valid option.  Please try again.'
        else:
            print module.__doc__
            return module.main()


def discover_modules(root):
    modules = []
    for root, dirs, files in os.walk(root):
        for f in (f for f in files if f.endswith('.py') and '__init__' not in f):
            path = os.path.join(root, f)[:-3]
            if root.startswith('.'):
                path = path[2:]
            modules.append(path.replace(os.sep, '.'))
    return modules


if __name__ == '__main__':
    args = vars(parser.parse_args())
    if args['log']:
        logging.basicConfig(level=logging.DEBUG)
    main()
