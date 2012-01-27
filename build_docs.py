import os
import pycco


modules = ['gps', 'eliza']
outdir = 'docs'


def module_sources(module):
    sources = []
    for filename in os.listdir(os.path.abspath(module)):
        if filename.endswith('.py'):
            sources.append(os.path.join(module, filename))
    return sources


def main():
    sources = []
    for module in modules:
        sources.extend(module_sources(module))
    pycco.process(sources, outdir=outdir)
        

if __name__ == '__main__':
    main()
