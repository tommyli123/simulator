# Overview

This is a simulator to run of a live editing scenarios for various loads of concurrent live editing documents where each document can have a randomly generatated number of concurrent live editing users and each user engages in a live editing session with different characteristics.  Each user can engage in an editing session of a document with a randomly generated duration, and within the engagement duration the writing of delta changes pattern varies depend on the user is a power, regular, or casual users.

The delta change a user writes to a document is simulated with writing a record to stdout.   The record format is designed to be easily imported to a time series database for query and dashboarding purpose.   For example, we can observe given a simulation load pattern, how many concurrent documents are under active editing for a given interval (second, minute, hour) so that we can infer into the capacity model of upstream services. 

This simulator can simulate work load of many thousands of concurrent documents per second where each document editing session can have up to 100 concurrent users.


# installation and configuration

This simulator requires python3.  Preferaby 3.9 and up.

## setup
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## configuration
edit `config.json`.   Hopefully the properties are self explanatory enough.

# run
- Collect the events in an output file for easy import to time series database for analysis.
- simulation summary is written to `summary.log`

```
python simulation.py > output.log
```
