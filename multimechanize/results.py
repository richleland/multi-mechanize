#!/usr/bin/env python
#
#  Copyright (c) 2010-2012 Corey Goldberg (corey@goldb.org)
#  License: GNU LGPLv3
#
#  This file is part of Multi-Mechanize | Performance Test Framework
#


import os
import time
from collections import defaultdict
from shutil import copytree

from jinja2 import Environment, FileSystemLoader, PackageLoader, Template

#import graph
#import reportwriter
#import reportwriterxml


def copy_static_media(results_dir):
    """
    Copies static media into the results folder.
    """
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    destination = os.path.abspath(os.path.join(results_dir, '..', 'static'))
    try:
        copytree(static_dir, destination)
    except OSError:
        print destination, "already exists, not copying static files"

def output_results(results_dir, results_file, run_time, rampup, ts_interval, user_group_configs=None, xml_reports=False):
    """
    Outputs the results to a folder in the results directory.
    """
    copy_static_media(results_dir)

    #env = Environment(loader=PackageLoader('multimechanize', 'templates'))
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('base.html')

    # parse the results and prepare them for the template
    results = Results(results_dir + results_file, run_time)

    # summary values
    total_transactions = results.total_transactions
    total_errors = results.total_errors
    start_datetime = results.start_datetime
    finish_datetime = results.finish_datetime

    # all transactions
    trans_timer_points = []  # [elapsed, timervalue]
    trans_timer_vals = []
    for resp_stats in results.resp_stats_list:
        t = (resp_stats.elapsed_time, resp_stats.trans_time)
        trans_timer_points.append(t)
        trans_timer_vals.append(resp_stats.trans_time)
    # MATPLOTLIB GRAPH WAS CREATED HERE USING THE FOLLOWING CALL:
    # graph.resp_graph_raw(trans_timer_points, 'All_Transactions_response_times.png', results_dir)

    # all transactions - transaction response summary
    transaction_summary = {
        'count': results.total_transactions,
        'min': '%.3f' % min(trans_timer_vals),
        'avg': '%.3f' % average(trans_timer_vals),
        'pct_80': '%.3f' % percentile(trans_timer_vals, 80),
        'pct_90': '%.3f' % percentile(trans_timer_vals, 90),
        'pct_95': '%.3f' % percentile(trans_timer_vals, 95),
        'max': '%.3f' % max(trans_timer_vals),
        'stdev': '%.3f' % standard_dev(trans_timer_vals),
    }

    # all transactions - interval details
    avg_resptime_points = {}  # {intervalnumber: avg_resptime}
    percentile_80_resptime_points = {}  # {intervalnumber: 80pct_resptime}
    percentile_90_resptime_points = {}  # {intervalnumber: 90pct_resptime}
    interval_secs = ts_interval
    splat_series = split_series(trans_timer_points, interval_secs)
    intervals = []
    for i, bucket in enumerate(splat_series):
        interval = {
            'num': i + 1,
            'count': 0,
            'rate': None,
            'min': None,
            'avg': None,
            'pct_80': None,
            'pct_90': None,
            'pct_95': None,
            'max': None,
            'stdev': None
        }

        interval_start = int((i + 1) * interval_secs)
        cnt = len(bucket)
        interval['count'] = cnt

        if cnt > 0:
            interval['rate'] = cnt / float(interval_secs)
            interval['min'] = '%.3f' % min(bucket)
            interval['avg'] = '%.3f' % average(bucket)
            interval['pct_80'] = '%.3f' % percentile(bucket, 80)
            interval['pct_90'] = '%.3f' % percentile(bucket, 90)
            interval['pct_95'] = '%.3f' % percentile(bucket, 95)
            interval['max'] = '%.3f' % max(bucket)
            interval['stdev'] = '%.3f' % standard_dev(bucket)

            avg_resptime_points[interval_start] = interval['avg']
            percentile_80_resptime_points[interval_start] = interval['pct_80']
            percentile_90_resptime_points[interval_start] = interval['pct_90']

        intervals.append(interval)

    # MATPLOTLIB GRAPH WAS CREATED HERE USING THE FOLLOWING CALL:
    #graph.resp_graph(avg_resptime_points, percentile_80_resptime_points, percentile_90_resptime_points, 'All_Transactions_response_times_intervals.png', results_dir)

    # all transactions - throughput
    throughput_points = {}  # {intervalnumber: numberofrequests}
    interval_secs = ts_interval
    splat_series = split_series(trans_timer_points, interval_secs)
    for i, bucket in enumerate(splat_series):
        throughput_points[int((i + 1) * interval_secs)] = (len(bucket) / interval_secs)

    # MATPLOTLIB GRAPH WAS CREATED HERE USING THE FOLLOWING CALL:
    #graph.tp_graph(throughput_points, 'All_Transactions_throughput.png', results_dir)

    # custom timers
    custom_timers = []
    for timer_name in sorted(results.uniq_timer_names):
        timer = {
            'name': timer_name,
            'throughput_points': {},
            'summary': {},
            'intervals': []
        }

        custom_timer_vals = []
        custom_timer_points = []
        for resp_stats in results.resp_stats_list:
            try:
                val = resp_stats.custom_timers[timer_name]
                custom_timer_points.append((resp_stats.elapsed_time, val))
                custom_timer_vals.append(val)
            except KeyError:
                pass
        #graph.resp_graph_raw(custom_timer_points, timer_name + '_response_times.png', results_dir)

        interval_secs = ts_interval
        splat_series = split_series(custom_timer_points, interval_secs)
        for i, bucket in enumerate(splat_series):
            timer['throughput_points'][int((i + 1) * interval_secs)] = (len(bucket) / interval_secs)
        #graph.tp_graph(throughput_points, timer_name + '_throughput.png', results_dir)

        # custom timer summary
        timer['summary'] = {
            'count': len(custom_timer_vals),
            'min': '%.3f' % min(custom_timer_vals),
            'avg': '%.3f' % average(custom_timer_vals),
            'pct_80': '%.3f' % percentile(custom_timer_vals, 80),
            'pct_90': '%.3f' % percentile(custom_timer_vals, 90),
            'pct_95': '%.3f' % percentile(custom_timer_vals, 95),
            'max': '%.3f' % max(custom_timer_vals),
            'stdev': '%.3f' % standard_dev(custom_timer_vals),
        }

        # custom timers - interval details
        interval_secs = ts_interval
        splat_series = split_series(custom_timer_points, interval_secs)

        for i, bucket in enumerate(splat_series):
            interval = {
                'num': i + 1,
                'count': 0,
                'rate': None,
                'min': None,
                'avg': None,
                'pct_80': None,
                'pct_90': None,
                'pct_95': None,
                'max': None,
                'stdev': None
            }

            interval_start = int((i + 1) * interval_secs)
            cnt = len(bucket)
            interval['count'] = cnt

            if cnt > 0:
                interval['rate'] = cnt / float(interval_secs)
                interval['min'] = '%.3f' % min(bucket)
                interval['avg'] = '%.3f' % average(bucket)
                interval['pct_80'] = '%.3f' % percentile(bucket, 80)
                interval['pct_90'] = '%.3f' % percentile(bucket, 90)
                interval['pct_95'] = '%.3f' % percentile(bucket, 95)
                interval['max'] = '%.3f' % max(bucket)
                interval['stdev'] = '%.3f' % standard_dev(bucket)

                avg_resptime_points[interval_start] = interval['avg']
                percentile_80_resptime_points[interval_start] = interval['pct_80']
                percentile_90_resptime_points[interval_start] = interval['pct_90']

            timer['intervals'].append(interval)
        #graph.resp_graph(avg_resptime_points, percentile_80_resptime_points, percentile_90_resptime_points, timer_name + '_response_times_intervals.png', results_dir)

        # add this timer to the list of custom timers
        custom_timers.append(timer)

    ### user group times
    ##for user_group_name in sorted(results.uniq_user_group_names):
    ##    ug_timer_vals = []
    ##    for resp_stats in results.resp_stats_list:
    ##        if resp_stats.user_group_name == user_group_name:
    ##            ug_timer_vals.append(resp_stats.trans_time)
    ##    print user_group_name
    ##    print 'min: %.3f' % min(ug_timer_vals)
    ##    print 'avg: %.3f' % average(ug_timer_vals)
    ##    print '80pct: %.3f' % percentile(ug_timer_vals, 80)
    ##    print '90pct: %.3f' % percentile(ug_timer_vals, 90)
    ##    print '95pct: %.3f' % percentile(ug_timer_vals, 95)
    ##    print 'max: %.3f' % max(ug_timer_vals)
    ##    print ''

    # render the template with the data
    rendered = template.render({
        'total_transactions': total_transactions,
        'total_errors': total_errors,
        'run_time': run_time,
        'rampup': rampup,
        'start_datetime': start_datetime,
        'finish_datetime': finish_datetime,
        'ts_interval': ts_interval,
        'user_group_configs': user_group_configs,
        'transaction_summary': transaction_summary,
        'intervals': intervals,
        'trans_timer_points': trans_timer_points,
        'throughput_points': throughput_points,
        'custom_timers': custom_timers,
    })

    # write the rendered template to disk
    output_file = os.path.join(results_dir, 'results.html')
    with open(output_file, 'w') as f:
        f.write(rendered)

    ## write the results in XML
    #if xml_reports:
        #reportwriterxml.write_jmeter_output(results.resp_stats_list, results_dir)



class Results(object):
    def __init__(self, results_file_name, run_time):
        self.results_file_name = results_file_name
        self.run_time = run_time
        self.total_transactions = 0
        self.total_errors = 0
        self.uniq_timer_names = set()
        self.uniq_user_group_names = set()

        self.resp_stats_list = self.__parse_file()

        self.epoch_start = self.resp_stats_list[0].epoch_secs
        self.epoch_finish = self.resp_stats_list[-1].epoch_secs
        self.start_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.epoch_start))
        self.finish_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.epoch_finish))



    def __parse_file(self):
        f = open(self.results_file_name, 'rb')
        resp_stats_list = []
        for line in f:
            fields = line.strip().split(',')

            request_num = int(fields[0])
            elapsed_time = float(fields[1])
            epoch_secs = int(fields[2])
            user_group_name = fields[3]
            trans_time = float(fields[4])
            error = fields[5]

            self.uniq_user_group_names.add(user_group_name)

            custom_timers = {}
            timers_string = ''.join(fields[6:]).replace('{', '').replace('}', '')
            splat = timers_string.split("'")[1:]
            timers = []
            vals = []
            for x in splat:
                if ':' in x:
                    x = float(x.replace(': ', ''))
                    vals.append(x)
                else:
                    timers.append(x)
                    self.uniq_timer_names.add(x)
            for timer, val in zip(timers, vals):
                custom_timers[timer] = val

            r = ResponseStats(request_num, elapsed_time, epoch_secs, user_group_name, trans_time, error, custom_timers)

            if elapsed_time < self.run_time:  # drop all times that appear after the last request was sent (incomplete interval)
                resp_stats_list.append(r)

            if error != '':
                self.total_errors += 1

            self.total_transactions += 1

        return resp_stats_list



class ResponseStats(object):
    def __init__(self, request_num, elapsed_time, epoch_secs, user_group_name, trans_time, error, custom_timers):
        self.request_num = request_num
        self.elapsed_time = elapsed_time
        self.epoch_secs = epoch_secs
        self.user_group_name = user_group_name
        self.trans_time = trans_time
        self.error = error
        self.custom_timers = custom_timers



def split_series(points, interval):
    offset = points[0][0]
    maxval = int((points[-1][0] - offset) // interval)
    vals = defaultdict(list)
    for key, value in points:
        vals[(key - offset) // interval].append(value)
    series = [vals[i] for i in xrange(maxval + 1)]
    return series



def average(seq):
    avg = (float(sum(seq)) / len(seq))
    return avg



def standard_dev(seq):
    avg = average(seq)
    sdsq = sum([(i - avg) ** 2 for i in seq])
    try:
        stdev = (sdsq / (len(seq) - 1)) ** .5
    except ZeroDivisionError:
        stdev = 0
    return stdev



def percentile(seq, percentile):
    i = int(len(seq) * (percentile / 100.0))
    seq.sort()
    return seq[i]




if __name__ == '__main__':
    output_results('./', 'results.csv', 60, 30, 10)
