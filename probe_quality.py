import os
import argparse
import datetime
from utils import formatted_list_date
from config import *
from probes import *


def get_arguments():
    """returns AttribDict with command line arguments"""
    parser = argparse.ArgumentParser(
        description='DTK-Quality Probes on DASE Data',
        formatter_class=argparse.RawTextHelpFormatter)

    # Script functionalities
    parser.add_argument('-p', '--probe', help='Choose a probe: bnmd, flat, ', required=True)
    parser.add_argument('-S', '--netsta', help='Choose a network/station to analyze', required=True)
    parser.add_argument('-s', '--site', help='Choose the site to analyze', required=True)
    parser.add_argument('-c', '--channel', help='Choose the channel to analyze', required=True)
    parser.add_argument('-d', '--directory', help='Choose the PSD/MSEED directory', required=True)

    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument('-y', '--yesterday', help='Analyze the last day of data', action="store_true")
    date_group.add_argument('-o', '--onedate', help='<yyyymmdd>, choose one date to analyze')
    date_group.add_argument('-i', '--interval', nargs=2, help='<yyyymmdd> <yyyymmdd>, choose an interval of two dates')

    args = parser.parse_args()

    print("DTK-QUALITY - PROBES")
    if args.yesterday is False and args.onedate is None and args.interval is None:
        print("No date argument passed. Analyzing yesterday's data")
        args.yesterday = True

    return args


def probe_quality():
    args = get_arguments()

    if args.probe not in PROBES_LIST:
        print('Error. Probe not in list.')
        exit(3)

    if args.yesterday:
        start_date = end_date = datetime.date.today()-datetime.timedelta(1)
    elif args.onedate is not None:
        one_date = formatted_list_date(args.onedate)
        if one_date is False:
            print('Error. Date not in the right format <yyyymmdd>')
            exit(3)

        start_date = end_date = datetime.date(one_date[0], one_date[1], one_date[2])
    else:
        start_date = formatted_list_date(args.interval[0])
        end_date = formatted_list_date(args.interval[1])
        if start_date is False or end_date is False:
            print('Error. Date not in the right format <yyyymmdd>')
            exit(3)

        start_date = datetime.date(start_date[0], start_date[1], start_date[2])
        end_date = datetime.date(end_date[0], end_date[1], end_date[2])
        if (end_date-start_date).days < 0:
            print('Error. End date is inferior to start date.')
            exit(3)

    if args.probe == 'below_noise_model' or args.probe == 'bnmd':
        exit_code = probe_below_noise_model(args.netsta, args.site, args.channel, args.directory, start_date, end_date)
    elif args.probe == 'flat':
        exit_code = probe_flat_signal(args.netsta, args.site, args.channel, args.directory, start_date, end_date)
    elif args.probe == 'harmonic':
        exit_code = probe_harmonic_spikes(args.netsta, args.site, args.channel, args.directory, start_date, end_date)
    else:
        exit_code = 3
        print('Error. Probe not in list.')
        exit(exit_code)

    exit(exit_code)


if __name__ == "__main__":
    probe_quality()
