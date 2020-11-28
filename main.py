import wave
import struct
import numpy as np
from tqdm import tqdm
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import io
from google.oauth2 import service_account


def transcribe_with_timestamps(filename):
    # Big shoutout to Soham Sil.  This code borrows heavily from their method.
    credentials = service_account.Credentials.from_service_account_file("INSERT_YOUR_CREDENTIALS_HERE.json")
    client = speech.SpeechClient(credentials=credentials)  # Check credentials

    with io.open(filename, "rb") as audio_file:
        content = audio_file.read()  # Read audio file.  Note: Audio must be mono.

    audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        language_code="en-US",
        enable_word_time_offsets=True
    )

    response = client.recognize(config, audio)  # Send audio to Google API for recognizing.
    print("Received back from Google Cloud API!")
    return response


def produce_censored_audio(wav_file, response, words_to_be_censored):  # The response object contains the start and end
    # times of each word, in nanoseconds.

    # [v] Read the audio file to be censored.
    uncensored_audio = wave.open(wav_file, "rb")
    print("Wave opened")

    # [v] Create a sine wave function with as many samples as the original file.
    amp = 30000
    sampling_rate = uncensored_audio.getframerate()
    sine_tone_hz = 20
    x = np.arange(uncensored_audio.getnframes())
    sine_wave_signal = amp * (np.sin(2 * np.pi * sine_tone_hz * x / sampling_rate))

    # [v] Create a copy of the .wav file, currently empty.
    audio_to_be_censored = wave.open("censored_audio.wav", "wb")
    nchannels = uncensored_audio.getnchannels()
    sampwidth = uncensored_audio.getsampwidth()
    framerate = uncensored_audio.getframerate()
    nframes = uncensored_audio.getnframes()
    comptype = uncensored_audio.getcomptype()
    compname = uncensored_audio.getcompname()
    audio_to_be_censored.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))  # Now we've created
    # a blank .wav file with the same params as the original wav.

    # [v] Write censored timespans to time_ranges_to_censor.
    time_ranges_to_censor = []
    for result in response.results:
        alternative = result.alternatives[0]
        for word_info in alternative.words:
            if word_info.word in words_to_be_censored:
                start_time = word_info.start_time
                end_time = word_info.end_time
                time_ranges_to_censor.append([start_time.seconds + start_time.nanos * 1e-9, end_time.seconds + end_time.
                                             nanos * 1e-9])
    print("Time ranges to censor: " + str(time_ranges_to_censor))

    # [v] Write the new audio file.
    # For each sample, if the sample is in any of the ranges in time_ranges_to_occur, put the corresponding number
    # sample from sine_wave_signal there.  Else, put the corresponding sample from uncensored_audio there.
    # TODO: Change so that instead of going sample by sample, just change the times that we want to change.
    for sample in tqdm(range(nframes)):  # if sample/framerate is greater than or equal than a 1st entry and less than
        # or equal to the corresponding 2nd entry
        censor_flag = 0
        for pair in time_ranges_to_censor:
            if pair[0] <= sample / framerate <= pair[1]:
                censor_flag = 1
        if censor_flag == 1:
            audio_to_be_censored.writeframes(struct.pack('h', int(sine_wave_signal[sample])))
        else:
            uncensored_audio.setpos(sample)
            audio_to_be_censored.writeframes(uncensored_audio.readframes(1))

    # [v] Close both audio files.
    uncensored_audio.close()
    audio_to_be_censored.close()
    return

censor_list_colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]

reply = transcribe_with_timestamps("sample_audio_before_censoring_mono.flac")
produce_censored_audio("sample_audio_before_censoring.wav", reply, censor_list_colors)
# TODO: Produce a flac file automatically from the wav file, so that the user only needs to provide the wav file.
