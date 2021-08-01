from pydub import AudioSegment
import numpy as np
import math

from google.cloud import texttospeech


def gen_basic(text: str, output_file: str, api_client: str) -> bool:

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ru-RU", ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    r = api_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(output_file, "wb") as file:
        file.write(r.audio_content)
    return True


def bass_line_freq(track: AudioSegment) -> int:
    sample_track = list(track.get_array_of_samples())

    est_mean = np.mean(sample_track)

    est_std = 3 * np.std(sample_track) / (math.sqrt(2))
    bass_factor = int(round((est_std - est_mean) * 0.005))

    return bass_factor


def attune_voice(input_file: str) -> AudioSegment:
    accentuate_db = 45
    octaves = -0.5

    sample = AudioSegment.from_mp3(input_file)

    new_sample_rate = int(sample.frame_rate * (2.0 ** octaves))
    sample = sample._spawn(sample.raw_data, overrides={"frame_rate": new_sample_rate})

    filtered = sample.low_pass_filter(bass_line_freq(sample))
    combined = sample.overlay(filtered + accentuate_db)

    return combined


def gen_amogus(
    text: str, amogus_file: str, voice_file: str, output_file: str, api_key: str
) -> None:
    gen_basic(text, voice_file, api_key)

    audio_text = attune_voice(voice_file)
    audio_music = AudioSegment.from_mp3(amogus_file)

    res = audio_text + audio_music
    res.export(output_file, format="mp3")
