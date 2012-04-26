import os
import pycco
import shutil


modules = [
    'paip/',
    'paip/examples/gps',
    'paip/examples/eliza',
    'paip/examples/search',
    'paip/examples/logic',
    'paip/examples/emycin',
    'paip/examples/othello',
    './'
    ]
outdir = 'docs'
prolog_examples = 'paip/examples/prolog'


def module_sources(module):
    sources = []
    for filename in os.listdir(os.path.abspath(module)):
        if filename != '__init__.py' and filename.endswith('.py'):
            sources.append(os.path.join(module, filename))
    return sources


def main():
    sources = []
    for module in modules:
        sources.extend(module_sources(module))
    pycco.process(sources, outdir=outdir)
    shutil.rmtree(os.path.join(outdir, prolog_examples), True)
    shutil.copytree(prolog_examples, os.path.join(outdir, prolog_examples))
        

if __name__ == '__main__':
    main()
