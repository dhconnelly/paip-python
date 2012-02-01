import os
import pycco
import shutil


modules = ['paip/']
outdir = 'docs'
style = 'docs/templates/pycco.css'
index = 'docs/templates/index.html'


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
    shutil.copyfile(style, os.path.join(outdir, 'pycco.css'))
    shutil.copyfile(index, os.path.join(outdir, 'index.html'))
        

if __name__ == '__main__':
    main()
