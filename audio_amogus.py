import requests
from pydub import AudioSegment
import numpy as np
import math


def gen_basic(text: str, output_file: str, api_key: str) -> bool:
    url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"

    headers = {"Authorization": "Api-Key " + api_key}

    data = {"text": text, "lang": "ru-RU", "voice": "zahar", "speed": "0.7"}

    r = requests.post(url, headers=headers, data=data)

    with open(output_file, "wb") as file:
        file.write(r.content)
    return True


def bass_line_freq(track: AudioSegment) -> int:
    sample_track = list(track)

    est_mean = np.mean(sample_track)

    est_std = 3 * np.std(sample_track) / (math.sqrt(2))
    bass_factor = int(round((est_std - est_mean) * 0.005))

    return bass_factor


def attune_ogg(input_file: str) -> AudioSegment:
    accentuate_db = 50
    octaves = -0.5

    sample = AudioSegment.from_ogg(input_file)

    new_sample_rate = int(sample.frame_rate * (2.0 ** octaves))
    sample = sample._spawn(sample.raw_data, overrides={"frame_rate": new_sample_rate})

    filtered = sample.low_pass_filter(bass_line_freq(sample.get_array_of_samples()))
    combined = sample.overlay(filtered + accentuate_db)

    return combined


def gen_amogus(text: str, amogus_file: str, voice_file: str, output_file: str, api_key: str) -> None:
    gen_basic(text, voice_file, api_key)

    audio_text = attune_ogg(voice_file)
    audio_music = AudioSegment.from_mp3(amogus_file)

    res = audio_text + audio_music
    res.export(output_file, format="mp3")
