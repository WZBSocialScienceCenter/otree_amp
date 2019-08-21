# Affect Misattribution Procedure (AMP) experiment for oTree

August 2019, Markus Konrad <markus.konrad@wzb.eu> / [Berlin Social Science Center](https://wzb.eu)

## Introduction

This repository contains an application for [oTree](http://www.otree.org/) ([Chen et al. 2016](http://dx.doi.org/10.1016/j.jbef.2015.12.001)) which implements the Affect Misattribution Procedure (AMP) experiment ([Payne et al. 2005](https://doi.org/10.1037/0022-3514.89.3.277), [Payne & Lundberg 2014](https://doi.org/10.1111/spc3.12148), [Teige-Mocigemba et al. 2017](https://doi.org/10.1027/1618-3169/a000364)).

Images of targets (Chinese characters) in directory `_static/amp/targets` were published by Keith Payne at http://bkpayne.web.unc.edu/research-materials/.

Makes use of the [otreeutils](https://github.com/WZBSocialScienceCenter/otreeutils) package ([Konrad 2018](https://doi.org/10.1016/j.jbef.2018.10.006)).

## Features and limitations

- precise timing of prime and target exposures in milliseconds
- prime and target images are pre-loaded before first display to prevent download delay
- precise measurement of responses in milliseconds
- each measurement is stored individually in the database
- easily adjustable (see configuration)
- requires keyboard for responses but may be extended to work on mobile devices as well
- results are transferred to server at the end of each *round* (each round or *block* consists of several trials), *not* after each trial

## Requirements

- Python 3.5 or higher (tested with Python 3.6)
- otree 2.1.41
- otreeutils 0.9.1

You can install the exact requirements using *pip*: `pip install -r requirements.txt`

## Code structure and page sequence



## Configuration

images

Constants

## Data export

## Tests

## License

Apache License 2.0. See LICENSE file.
