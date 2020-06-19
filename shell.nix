with import <nixpkgs> {};
let
  my-python-packages = python-packages: with python-packages; [
    pip
    setuptools
    fusepy
    virtualenv
  ];
  my-python = python37.withPackages my-python-packages;

  inputs = [
    fuse
    my-python
  ];

in mkShell {
  buildInputs = inputs;
  shellHooks = ''
    alias pip="PIP_PREFIX='$(pwd)/_build/pip_packages' \pip"
    export PYTHONPATH="$(pwd)/_build/pip_packages/lib/python3.7/site-packages:$PYTHONPATH"
    export PATH=$PATH:$(pwd)/_build/pip_packages/bin
    unset SOURCE_DATE_EPOCH
  '';
}
