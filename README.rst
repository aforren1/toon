toon: tools for neuroscience
============================

Install:

(This is somewhat temporary, until the pip-enhanced version of psychopy hits pypi)

```shell
pip install git+https://github.com/aforren1/toon@pypi --process-dependency-links
```

Create environment:

```shell
conda create --name toon python==3.6
activate toon
conda install numpy scipy
pip install git+https://github.com/psychopy/psychopy
```
