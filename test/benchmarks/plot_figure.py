"""
Plot graphs summarizing benchmark results generated by simple_network.py


Usage: python plot_figure.py [-h] [-o FILENAME] parameter_file data_store

positional arguments:
  parameter_file  parameter file given to simple_network.py
  data_store      data file produced by simple_network.py, in CSV format

optional arguments:
  -h, --help      show this help message and exit
  -o FILENAME     output file name
"""


import csv
import argparse
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import defaultdict
from parameters import ParameterSet

# Parse command-line arguments and read parameter file
parser = argparse.ArgumentParser()
parser.add_argument("parameter_file", help="parameter file given to simple_network.py")
parser.add_argument("data_store", help="data file produced by simple_network.py, in CSV format")
parser.add_argument("-o", metavar="FILENAME", help="output file name",
                    default="Results/benchmark_summary.png")
args = parser.parse_args()
parameters = ParameterSet(args.parameter_file)

# Read data from CSV file
with open(args.data_store, "rb") as csvfile:
    reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
    records = list(reader)

# Filter and re-format data for plotting
independent_variable = "num_processes"
dependent_variables = ["import", "setup", "build", "connect", "record", "run", "get_data"]
conditions = parameters.flatten()
results = dict((var, defaultdict(list)) for var in dependent_variables)
stats = dict((var, {}) for var in dependent_variables)

def matches_conditions(record, conditions):
    return all((record[condition] == value) for condition, value in conditions.items())

# ... for each record that matches the conditions, add the timing data to the filtered results
for record in records:
    if matches_conditions(record, conditions):
        x = record[independent_variable]
        for var in dependent_variables:
            results[var][x].append(record[var])

# ... then calculate the statistics across repetitions
for var in dependent_variables:
    for x, values in results[var].items():
        stats[var][x] = np.mean(values), np.std(values, ddof=1)


# Plot the results

def sort_by_first(*y):
    zipped = zip(*y)
    zipped_sorted = sorted(zipped, key=lambda x: x[0])
    return map(list, zip(*zipped_sorted))
    
settings = {
    'lines.linewidth': 0.5,
    'axes.linewidth': 0.5,
    'axes.labelsize': 'small',
    'legend.fontsize': 'small',
    'font.size': 8,
    'savefig.dpi': 150,
}
plt.rcParams.update(settings)

width, height = 6, 10
fig = plt.figure(1, figsize=(width, height))
gs = gridspec.GridSpec(1, 1)
gs.update(bottom=0.6)  # leave space for annotations
gs.update(top=1 - 0.8/height, hspace=0.1)
ax = plt.subplot(gs[0, 0])
for var in dependent_variables:   
    x = stats[var].keys()
    y, yerr = map(list, zip(*stats[var].values()))
    x, y, yerr = sort_by_first(x, y, yerr)
    ax.errorbar(x, y, yerr=yerr, fmt='o-', label=var)
    ax.set_xlabel(independent_variable)
    ax.set_xlim([x[0]/1.4, x[-1]*1.4])
    ax.set_ylabel("Time (s)")
    ax.set_xscale("log", basex=2)
    ax.set_yscale("log", basex=2)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
title = args.parameter_file
fig.text(0.5, 1 - 0.5/height, title,
              ha="center", va="top", fontsize="large")
annotations = parameters.pretty()
plt.figtext(0.01, 0.01, annotations, fontsize=6, verticalalignment='bottom')
fig.savefig(args.o)
