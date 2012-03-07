import os
import pycco
import shutil


modules = [
    'paip/',
    'paip/examples/gps',
    'paip/examples/eliza',
    'paip/examples/search'
    'paip/examples/logic',
    ]
outdir = 'docs'


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
        

if __name__ == '__main__':
    main()
