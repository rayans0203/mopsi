# PROJECT: DEV. OF A WEBSITE FOR OPTION PRICING WITH MULTILEVEL MONTE-CARLO METHODS

# MOPSI folders:
## optionPricer: 
- mlmc.py: contains the classes used to price an option given a set of parameters
- figures: all the .png files proving empirically the convergence of the methods used 
- __init__.py: to import our files into others

## notes & doc: 
- the maths papers we studied to implement the MLMC methods

## tests: 
- series of unitary tests for the classes developed in mlmc.py.

# TDLOG folders:
## website: 
### optionPricer: name of the Django Project
- optionPricer: folder automatically created with django. Contains all the "settings" files
- userInterface: name of the application of our website: contains the admin settings,the migrations, the M-T-V files, and the static files for the graphic interface
