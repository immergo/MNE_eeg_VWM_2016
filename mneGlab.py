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


def loadRawData(eegDataPath):
    """Input path and filename to .cnt, return raw data object."""

    raw = mne.io.read_raw_cnt(eegDataPath, None, date_format='dd/mm/yy', preload=True)
    return raw


def rawPrep(rawObj):
    """Input name of raw data object. Rename channels, set montage, and re-reference to average."""

    rawObj.rename_channels(mapping={'FP2': 'Fp2', 'As REF': 'AsREF', 'Af7': 'AF7'})
    rawObj.info['bads'] = ['AsREF']
    montages = mne.channels.read_montage('C:\Users\GamesLab_2\mne-python\mne\channels\data\montages\M1_Custom.txt')
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


def loadEpochs(directory):
    """Input directory of .fif epoch files.  Return list of epoch objects and list of epoch filenames."""

    fileList = []
    for file in directory:
        if file.endswith('.fif'):
            fileList.append(file)
    print "File Names Gathered: ", fileList

    epochList = []
    for ep in fileList:
        epoch = mne.read_epochs(ep)
        epochList.append(epoch)

    return epochList, fileList


def loadICA(directory):
    """Input directory of ICA weight .fif files.  Return list of ICA objects."""

    icaList = []
    for file in directory:
        if file.endswith('ica.fif'):
            ica = mne.preprocessing.read_ica(file)
            icaList.append(ica)

    return icaList


def getICA(epochList, fileList):
    """Input list of epoch objects.  Save ICA solutions for each participant."""

    for num, obj in enumerate(epochList):
        this_ica = mne.preprocessing.ICA(method='extended-infomax').fit(obj)
        this_file = fileList[num]
        fileName = this_file[:this_file.find('_')] + "VWM_solution-ica.fif"
        this_ica.save(fileName)


def epochForICA(directory):
    """Input directory of raw .cnt.  Prepare, filter, and save."""

    for file in directory:
        if file.endswith('.cnt'):
            print "Current file: " + str(file)
            raw = loadRawData(file)
            print raw.info
            rawPrep(raw)
            rawResample_Filter(raw)

            epochs = epochRaw(raw)
            epochs.save(file[:file.find('.')] + "_forICA-epo.fif", split_size='2GB')


def epochCorrectData(directory):
    """Input directory of raw .cnt.  Drop incorrect trial epochs and save."""

    for file in directory:
        if file.endswith('.cnt'):
            print "Current file: " + str(file)
            raw = loadRawData(file)
            rawPrep(raw)
            rawResample_Filter(raw)

            epochs = epochRaw(raw)
            accuracies = correctFilter(file[:file.find('_')]+"_markers.csv")

            print "Number of epochs: " + str(len(epochs.events))
            print "Number of behavioral responses" + str(len(accuracies))

            epochs.drop(accuracies, reason='USER')
            epochs.save(file[:file.find('.')]+"_correctFiltered-epo.fif", split_size='2GB')

#epochs.drop(accuracies, reason='USER')
#dataPath = 'C:/Users/GamesLab_2/Desktop/Py EEG Analysis/'