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
import matplotlib.pyplot as plt
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
dependent_variables = ["import", "setup", "build", "connect", "record", "run"]
conditions = parameters.flatten()

abscissae = []
ordinates = defaultdict(list)
for record in records:
    if all((record[condition] == value)
           for condition, value in conditions.items()):
        pprint(record)
        abscissae.append(record[independent_variable])
        for var in dependent_variables:
            ordinates[var].append(record[var])

print abscissae
pprint(ordinates)

# Generate figure
for var in dependent_variables:
    plt.plot(abscissae, ordinates[var], "o", label=var)
plt.legend()
plt.xlabel(independent_variable)
plt.ylabel("Time (s)")
plt.loglog()
plt.xlim(xmin=min(abscissae)/2.0)
plt.title(conditions["simulator"])
plt.savefig(args.o)
