# pyNSL

### v0.0.1

Direct Python port of parts of NSL toolbox [Chi et al., 2005](https://asa.scitation.org/doi/full/10.1121/1.1945807). The original Matlab implementation is available [here](http://nsl.isr.umd.edu/downloads.html). The package has been tested against the original matlab implementation.

**Note**: At the moment, the package is only partial implementation of early-stage part of the model. The current functionality allows for modelling simple peripheral auditory processing, extracting features of speech, etc. Remaining functionalities shall be ported soon...

### Requires:
- [NumPy](https://numpy.org/doc/stable/index.html)
- [SciPy](https://www.scipy.org/)
- [SoundFile](https://pysoundfile.readthedocs.io/en/latest/)
- [matplotlib](https://matplotlib.org/) (optional - for demo visualization)

### Installation:
From terminal (or `conda shell` in Windows), `cd` in root directory of the package (directory containing `setup.py` file) and type:

To get the package installed only through symbolic links, namely so that you can modify the source code and use modified versions at will when importing the package in your python scripts do:

```python
python setup.py develop
```

Otherwise, for a standard installation (but this will require to be installed if you need to install another version of the library):

```python
python setup.py install
```

### Usage

After the package is installed, see the ```demo.py``` for an example usage.

## TODOs
- [ ] Write proper docstrings and comment the code 
- [ ] Systematic tests
- [ ] Implement remaining functionality of the early-stage subcortical processing model
- [ ] Implement higher-level cortical processing model

#### Contact

[Mikolaj Kegler](https://mkegler.github.io/) (mikolaj.kegler16@imperial.ac.uk)