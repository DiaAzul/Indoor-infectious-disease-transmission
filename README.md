# Indoor infectious disease transmission
Infectious diseases may be transmitted through several mechanisms including touch, droplets and formites. This model considers the potential impact of disease transmission within an indoor microenvironment where the prime mode of transmission is an aerosol.

The model is based upon a number of simplifying assumptions, the most critical of which are:
* The only mode of transmission of the infectous disease is by aerosol.
* The aerosol is instantly well-mixed and uniformly distributed throughout the environment.

Any results for the models should be considered in the light of these assumptions prior to drawing any conclusions about transmission of the infectious disease within the environment.

The modelling follows the approach set out in the paper: Buonanno, G., Stabile, L., & Morawska, L. (2020). Estimation of airborne viral emission: Quanta emission rate of SARS-CoV-2 for infection risk assessment Preprint. Infectious Diseases (except HIV/AIDS). https://doi.org/10.1101/2020.04.12.20062828

## Modelling framework
The model uses simpy as the underpinning discrete event simulation framework. On top of this the model creates several classes to create the simulation:
* **Person** - The person class represents an individual within the model. Each person may be given a list of microenvironments to visit in turn.
* **Microenvironment** - The microenvironment class represents the indoor environment within which infectious disease transmission may occur. The environment may contain several diffent types of person, such as staff or visitor.
* **Simulation** - The simulation class controls the simulation and is responsible for instantiating microenvironments; defining the routing of people between environments; creating people within the simulation of the required type and at the required time.
* **DataCollection** - The data collection class is reponsible for collating data from across the simulation either by periodic sampling or receiving and logging data as it is submitted.

The simulation is designed such that it can be run and analysed within a Jupyter notebook.
