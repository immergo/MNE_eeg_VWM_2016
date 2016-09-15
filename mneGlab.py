import mne, csv

def correctFilter(behDataPath):
    """Input path and filename of extracted behavioral responses.  Returns boolean array
       to be used when dropping epochs."""

    accuracies = []
    with open(behDataPath, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            if int(row[0][3:]) == 1:
                accuracies.append(False)
            else:
                accuracies.append(True)

    return accuracies


def loadData(eegDataPath):
    """Input path and filename to .cnt, return raw data object."""

    raw = mne.io.read_raw_cnt(eegDataPath, None, date_format='dd/mm/yy', preload=True)
    return raw


def rawPrep(rawObj):
    """Input name of raw data object. Rename channels, set montage, and re-reference to average."""

    rawObj.rename_channels(mapping={'FP2': 'Fp2', 'As REF': 'AsREF', 'Af7': 'AF7'})
    rawObj.info['bads'] = ['AsREF']
    montages = mne.channels.read_montage('d:\home\mskorko\apps\Anaconda2\Lib\site-packages\mne\channels\data\montages\M1_Custom.txt')
    rawObj.set_montage(montages)
    mne.io.set_eeg_reference(rawObj, ref_channels=None)


def rawResample_Filter(rawObj):
    """Input name of raw data object. Resample and bandpass filter."""

    rawObj.resample(256, npad='auto')
    rawObj.filter(0.5, 100.0)


def epochRaw(rawObj):
    """Input name of raw object. Return epoched data."""

    tmin, tmax = -0.5, 1.1
    events = mne.find_events(rawObj)
    event_id = {'Left_2': 12, 'Left_3': 13, 'Left_4': 14, 'Left_5': 15,
                'Right_2': 22, 'Right_3': 23, 'Right_4': 24, 'Right_5': 25}
    picks = mne.pick_types(rawObj.info, meg=False, eeg=True, stim=True, eog=False,
                           exclude='bads')
    epochs = mne.Epochs(rawObj, events, event_id, tmin, tmax, baseline=(None, 0), preload=False, reject=None)

    return epochs

#epochs.plot(n_channels, n_epochs) | ie. 32, 15
#epochs.save(path/filename-epo.fif)
#epochs.drop(accuracies, reason='USER')
#dataPath = 'C:/Users/GamesLab_2/Desktop/Py EEG Analysis/'