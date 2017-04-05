# Fansite Analytics

## Completed Feature 1/2/3/4
Tested with the testsuites.
## Python 2.7.x and Standard Libraries, NO other dependencies.
Take good use of defaultdict of Python collections libary for counting purpose.
For performance issue, Counter() is not used.
## Single threaded
No multi-threads/multi-processes.

## Performance

Tested with the provide log file (>4 millions lines). Feature 1/2/4 can
be done in 18 seconds total with a medicore Celeron 2.1Ghz PC runnning Linux Mint 18.1.
Feature 3 is more time consuming and can take up to 2 minutes. So the total run time
for a 450MB log file is about 2 minutes  on a medicore Linux PC.
