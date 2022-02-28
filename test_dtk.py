from dtk_quality import read_measures, read_spectrums
from dtk_quality._io import _read_spectrums_from_h5_file
from dtk_quality import MeasureType
from datetime import datetime
import os

noise_model = MeasureType('NoiseModelComparison')
spectrum_path = os.path.realpath(os.path.join("test_dtk", "quality_output", "computer", "spectrums", "2019", "2019-154",
                                              "ARCES.nc"))

# arces = _read_spectrums_from_h5_file(h5_file_path=spectrum_path)

arces_read = read_spectrums(spectrum_path, 'ARA0', 'IM.ARA0..BHZ', datetime(2019,6,1), datetime(2019,6,4))
print(arces_read)