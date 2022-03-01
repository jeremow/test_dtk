import datetime
import os
import glob
from dtk_quality._io import _read_spectrums_from_h5_file as h5read
from scipy.interpolate import interp1d
from obspy import read

def probe_below_noise_model(netsta, site, channel, directory, start_date: datetime.date, end_date: datetime.date):
    try:
        with open('SLNM2.txt', 'r') as noise_model:
            f, pxx = [], []
            for line in noise_model:
                data = line.split()
                f.append(float(data[0]))
                pxx.append(float(data[1]))

            interp_noise_model = interp1d(f, pxx, kind='linear')
    except FileNotFoundError:
        print('Error. Low Noise Model text file not found.')
        return 3

    nb_days = end_date - start_date

    for i in range(0, nb_days.days+1):
        i_date = start_date + datetime.timedelta(i)
        i_year = str(i_date.year)
        i_julian_date = i_date.strftime('%Y-%j')
        i_directory = os.path.join(directory, i_year, i_julian_date, netsta)
        nc_file_list = glob.glob(i_directory + '*')

        if not nc_file_list:
            print(f'Error. No NC file for {netsta}.{site}.{channel} on {i_julian_date}.')
            return 3

        for nc_file in nc_file_list:
            parsed_spectrum_list = h5read(nc_file)
            parsed_spectrum_list = list(filter(
                lambda x:
                x.header.sensor_name == site
                and x.header.channel == channel,
                parsed_spectrum_list
            ))

            for parsed_spectrum in parsed_spectrum_list:
                for hourly_spectrum in parsed_spectrum.hourly_spectrums:
                    for k, frequency in enumerate(hourly_spectrum.frequencies):
                        try:
                            interp_value = interp_noise_model(frequency)
                            if hourly_spectrum.values[k] < interp_value and 0.1 < frequency < 0.4:
                                print(f'Warning. Signal below Noise Model '
                                      f'for {netsta}.{site}.{channel} on {i_julian_date}.')
                                return 1
                        except ValueError:
                            pass

    print('OK. Signal above Noise Model.')
    return 0


def probe_flat_signal(netsta, site, channel, directory, start_date, end_date):
    nb_days = end_date - start_date

    for i in range(0, nb_days.days + 1):
        i_date = start_date + datetime.timedelta(i)
        i_year = str(i_date.year)
        i_julian_date = i_date.strftime('%Y.%j')
        i_mseed_name = f'{netsta}.{site}..{channel}.D.{i_julian_date}'
        i_directory = os.path.join(directory, i_year, netsta, site, channel+'.D', i_mseed_name)
        mseed_file_list = glob.glob(i_directory + '*')

        if not mseed_file_list:
            print(f'Error. No MSEED file for {netsta}.{site}.{channel} on {i_julian_date}.')
            return 3

        for mseed_file in mseed_file_list:
            spectrum = read(mseed_file)[0]
            hour = int(3600 * spectrum.stats.sampling_rate)
            length_data = len(spectrum.data)

            if hour > length_data:
                hour = length_data

            for j in range(0, length_data, hour):
                hour_data = sum(spectrum.data[j:j+hour])
                if hour_data == 0:
                    print(f'Critical. Flat Signal on {netsta}.{site}.{channel} on {i_julian_date}')
                    return 2

    print('OK. No problem with the Flat Probe.')
    return 0


def probe_harmonic_spikes(netsta, site, channel, directory, start_date, end_date):
    pass
