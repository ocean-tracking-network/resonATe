#!/bin/bash
python setup.py sdist upload -r testpypi;
python setup.py sdist upload -r pypi
rm -f ~/anaconda3/conda-bld/osx-64/resonate*;
conda-build conda.recipe &&
rm -rf conda-dist &&
mkdir conda-dist;
mkdir conda-dist/osx-64;
conda convert --platform all ~/anaconda3/conda-bld/osx-64/resonate-*.tar.bz2 -o conda-dist/ &&
cp -r ~/anaconda3/conda-bld/osx-64/ ./conda-dist/osx-64/ &&
anaconda upload ./conda-dist/osx-64/resonate-*.tar.bz2 &&
anaconda upload ./conda-dist/linux-32/resonate-*.tar.bz2  &&
anaconda upload ./conda-dist/linux-64/resonate-*.tar.bz2  &&
anaconda upload ./conda-dist/win-32/resonate-*.tar.bz2  &&
anaconda upload ./conda-dist/win-64/resonate-*.tar.bz2
