"""The web log analyzer in Python 2.7.x.

Author: Qing Wang
for Insight coding challenges
4/4/2017
"""
import sys
import operator
import datetime
from collections import defaultdict
# the output limit for rankings, set it to 10
OUTPUT_LIMIT = 10


def time_converter(timestamp_str):
    """Convert timestramp string to python datetime object."""
    timestamp, timezone = timestamp_str.split()
    base = datetime.datetime.strptime(timestamp, '%d/%b/%Y:%H:%M:%S')
    return base


def log_line_parser(line):
    """Parse one line of the log file."""
    split_line = line.split()
    hosts, status_code, traffic = (split_line[0], split_line[-2],
                                   split_line[-1])
    timestamp = split_line[3][1:] + ' ' + split_line[4][:-1]
    resources = split_line[6].rstrip('"')
    traffic = 0 if traffic == '-' else int(traffic)
    return hosts, timestamp, resources, traffic, status_code


def ranking_output(ranking, path, output_num=True):
    """Generate rankings and output it in specified format."""
    count = 0
    with open(path, 'w') as f:
        for data in sorted(ranking.items(), key=operator.itemgetter(1),
                           reverse=True):
            if count < OUTPUT_LIMIT:
                if output_num:
                    f.write(','.join([data[0], str(data[1])]) + '\n')
                else:
                    f.write(data[0] + '\n')
                count += 1
            else:
                break
        f.close()


def monitor_login(login_records, blocked_ip, hosts, status_code, timestamp):
    """Set flag based on login activity and decide if it should be blocked."""
    record = login_records.get(hosts, None)
    if status_code == "401":
        if not record:
            login_records[hosts] = [time_converter(timestamp), 1]
        else:
            if time_converter(timestamp) - record[0] > datetime.timedelta(seconds=20):
                record = [time_converter(timestamp), 1]
            else:
                record[1] += 1
                if record[1] >= 3:
                    # trigger blocke ip flag and reset flag
                    blocked_ip[hosts] = time_converter(timestamp)
                    del login_records[hosts]
    elif status_code == "200":
        if record:
            del login_records[hosts]


def ts_generator(path):
    """Generate the timestamp data from the data file stream."""
    with open(path) as input_file:
        for line in input_file:
            hosts, timestamp, resources, traffic, status_code = log_line_parser(line)
            ts = time_converter(timestamp)
            yield ts


def access_peak(start_ts, tz, input_path, output_path):
    """Generate access peak report hours.txt."""
    access_distribution = defaultdict(int)
    for ts in ts_generator(input_path):
        offset = int((ts - start_ts).total_seconds())
        key_range = xrange(0, offset + 1) if offset <= 3600 else (offset-3600, offset + 1)
        for key in key_range:
            access_distribution[key] += 1
    count = 0
    with open(output_path, 'w') as f:
        for data in sorted(access_distribution.items(), key=operator.itemgetter(1),
                           reverse=True):
            if count < OUTPUT_LIMIT:
                ts_string = (start_ts + datetime.timedelta(seconds=data[0])).strftime('%d/%b/%Y:%H:%M:%S')
                f.write(','.join([ts_string + ' ' + tz, str(data[1])]) + '\n')
                count += 1
            else:
                break


def main(argv):
    """The main funciton of the log processor."""
    if len(argv) == 5:
        input_path, hosts_path, hours_path, resources_path, blocked_path = argv
        hosts_ranking = defaultdict(int)
        resources_ranking = defaultdict(int)
        login_records = {}
        blocked_ip = {}
        line_counter = 0
        blocked_output = open(blocked_path, 'w')
        with open(input_path) as input_file:
            for line in input_file:
                # parse one line of the log
                hosts, timestamp, resources, traffic, status_code = log_line_parser(line)
                # count resources and hosts
                hosts_ranking[hosts] += 1
                resources_ranking[resources] += traffic
                # record start_timestamp
                if line_counter == 0:
                    start_ts = time_converter(timestamp)
                    tz = timestamp.split()[-1]
                # check if the request needs to be blocked
                if hosts in blocked_ip:
                    if time_converter(timestamp) - blocked_ip[hosts] <= datetime.timedelta(seconds=300):
                        blocked_output.write(line)
                    else:
                        # 5 minitures expired and unblock it
                        del blocked_ip[hosts]
                        if resources == '/login':
                            monitor_login(login_records, blocked_ip,
                                          hosts, status_code, timestamp)
                # monitor login attempts if the ip is not blocked
                elif resources == '/login':
                    monitor_login(login_records, blocked_ip,
                                  hosts, status_code, timestamp)
                line_counter += 1
        blocked_output.close()
        print "The blocked.txt has been generated."
        ranking_output(hosts_ranking, hosts_path)
        print "The hosts.txt has been generated."
        ranking_output(resources_ranking, resources_path, False)
        print "The resources.txt has been generated."
        # Generate hours.txt
        print "Generating hours.txt. Depending on data size, it may take some time.."
        access_peak(start_ts, tz, input_path, hours_path)
        print "The hours.txt has been generated."
    else:
        print "The number of input parameters must be exactly 5."
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
