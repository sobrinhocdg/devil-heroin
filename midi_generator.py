import argparse
import math
import os
import random
from datetime import datetime

from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

MODES = {
    'aeolian': [0, 2, 3, 5, 7, 8, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
}

DARK_INSTRUMENTS = [
    89,  # Pad 2 (Warm)
    90,  # Pad 3 (Polysynth)
    91,  # Pad 4 (Choir)
    93,  # Pad 6 (Metallic)
    48,  # Strings Ensemble
    58,  # Synth Bass 1
    80,  # Lead 2 (Sawtooth)
    71,  # Clarinet
    86,  # Synth Voice
    97,  # FX 3 (Crystal)
    113, # FX 9 (Sweep)
    120, # Synth Drum (for subtle percussion-like textures)
]

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def note_name_to_midi(note_name: str, octave: int):
    base = NOTE_NAMES.index(note_name)
    return base + 12 * (octave + 1)


def build_scale(root_note: int, mode: str):
    intervals = MODES[mode]
    return [(root_note + step) for step in intervals]


def build_progression(scale, length):
    root = scale[0]
    chord_pattern = [0, 4, 5, 3, 1]
    progression = []
    for i in range(length):
        idx = chord_pattern[i % len(chord_pattern)]
        chord_root = scale[idx % len(scale)]
        progression.append(chord_root)
    return progression


def build_chord(root_note, scale, quality='minor'):
    third = root_note + scale[2] if quality == 'minor' else root_note + scale[2]
    fifth = root_note + scale[4]
    seventh = root_note + scale[6]
    return [root_note, third, fifth, seventh]


def add_track_notes(track, notes, start_tick, duration, velocity=80):
    for note in notes:
        track.append(Message('note_on', note=note, velocity=velocity, time=start_tick))
        track.append(Message('note_off', note=note, velocity=velocity // 2, time=duration))
        start_tick = 0


def make_counterpoint(scale, base_progression, bars, step, length):
    line = []
    for i in range(bars):
        chord_root = base_progression[i % len(base_progression)]
        root_index = scale.index(chord_root) if chord_root in scale else 0
        note = scale[(root_index + step) % len(scale)] + 12 * 4
        line.append((note, length))
    return line


def create_midi(title, tempo, bars, tracks_count, seed, output_dir):
    random.seed(seed)
    root = random.choice([note_name_to_midi(n, 3) for n in ['D', 'E', 'F', 'G', 'A']])
    mode = random.choice(list(MODES.keys()))
    scale = build_scale(root, mode)
    progression = build_progression(scale, bars)
    ticks_per_beat = 480
    beats_per_bar = 4
    ticks_per_bar = ticks_per_beat * beats_per_bar
    total_ticks = bars * ticks_per_bar

    midi = MidiFile(ticks_per_beat=ticks_per_beat)
    meta = MidiTrack()
    meta.append(MetaMessage('track_name', name=title, time=0))
    meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(tempo), time=0))
    meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
    midi.tracks.append(meta)

    track_definitions = []
    if tracks_count >= 1:
        track_definitions.append({'name': 'Drone Pad', 'program': DARK_INSTRUMENTS[0], 'velocity': 56, 'pattern': 'drone'})
    if tracks_count >= 2:
        track_definitions.append({'name': 'Pulse Bass', 'program': DARK_INSTRUMENTS[5], 'velocity': 92, 'pattern': 'bass'})
    if tracks_count >= 3:
        track_definitions.append({'name': 'Lead Melody', 'program': DARK_INSTRUMENTS[6], 'velocity': 78, 'pattern': 'melody'})
    if tracks_count >= 4:
        track_definitions.append({'name': 'Arpeggio', 'program': DARK_INSTRUMENTS[1], 'velocity': 65, 'pattern': 'arpeggio'})
    if tracks_count >= 5:
        track_definitions.append({'name': 'Bell Motif', 'program': DARK_INSTRUMENTS[8], 'velocity': 70, 'pattern': 'bell'})
    if tracks_count >= 6:
        track_definitions.append({'name': 'Choir Pad', 'program': DARK_INSTRUMENTS[2], 'velocity': 60, 'pattern': 'pad'})
    if tracks_count >= 7:
        track_definitions.append({'name': 'Counterpoint', 'program': DARK_INSTRUMENTS[7], 'velocity': 66, 'pattern': 'counterpoint'})
    if tracks_count >= 8:
        track_definitions.append({'name': 'Harmonic Texture', 'program': DARK_INSTRUMENTS[3], 'velocity': 62, 'pattern': 'texture'})
    if tracks_count >= 9:
        track_definitions.append({'name': 'Ambient Drone', 'program': DARK_INSTRUMENTS[9], 'velocity': 54, 'pattern': 'ambience'})
    if tracks_count >= 10:
        track_definitions.append({'name': 'Dark Lead', 'program': DARK_INSTRUMENTS[6], 'velocity': 72, 'pattern': 'dark_lead'})
    if tracks_count >= 11:
        track_definitions.append({'name': 'Pad Sweep', 'program': DARK_INSTRUMENTS[4], 'velocity': 58, 'pattern': 'sweep'})
    if tracks_count >= 12:
        track_definitions.append({'name': 'Sub Bass', 'program': DARK_INSTRUMENTS[5], 'velocity': 88, 'pattern': 'sub'})

    for idx, config in enumerate(track_definitions, start=1):
        track = MidiTrack()
        track.append(Message('program_change', program=config['program'], time=0))
        track.append(MetaMessage('track_name', name=config['name'], time=0))
        midi.tracks.append(track)

        if config['pattern'] == 'drone':
            for bar in range(bars):
                chord_root = progression[bar % len(progression)]
                chord = build_chord(chord_root, MODES[mode], quality='minor')
                octave_chord = [note + 12 for note in chord]
                add_track_notes(track, octave_chord[:3], start_tick=0 if bar == 0 else ticks_per_bar, duration=ticks_per_bar, velocity=config['velocity'])
        elif config['pattern'] == 'bass':
            for bar in range(bars):
                root_note = progression[bar % len(progression)] - 12
                track.append(Message('note_on', note=root_note, velocity=config['velocity'], time=0 if bar == 0 else ticks_per_bar))
                track.append(Message('note_off', note=root_note, velocity=config['velocity'] // 2, time=ticks_per_bar))
        elif config['pattern'] == 'melody':
            for bar in range(bars):
                chord_root = progression[bar % len(progression)]
                for step in range(4):
                    note = scale[(scale.index(chord_root) + step * 2) % len(scale)] + 12 * 4
                    time = 0 if (bar == 0 and step == 0) else ticks_per_beat
                    track.append(Message('note_on', note=note, velocity=config['velocity'], time=time))
                    track.append(Message('note_off', note=note, velocity=config['velocity'] // 2, time=ticks_per_beat * 2))
        elif config['pattern'] == 'arpeggio':
            for bar in range(bars):
                chord_root = progression[bar % len(progression)]
                for i, interval in enumerate([0, 2, 4, 7]):
                    note = chord_root + interval + 12 * 3
                    time = 0 if (bar == 0 and i == 0) else ticks_per_beat // 2
                    track.append(Message('note_on', note=note, velocity=config['velocity'], time=time))
                    track.append(Message('note_off', note=note, velocity=config['velocity'] // 2, time=ticks_per_beat // 2))
        elif config['pattern'] == 'bell':
            for bar in range(bars):
                if random.random() < 0.6:
                    note = scale[random.choice([0, 2, 4, 6])] + 12 * 5
                    time = 0 if bar == 0 else ticks_per_bar
                    track.append(Message('note_on', note=note, velocity=config['velocity'], time=time))
                    track.append(Message('note_off', note=note, velocity=config['velocity'] // 2, time=int(ticks_per_bar * 1.5)))
        elif config['pattern'] == 'pad':
            for bar in range(bars):
                chord_root = progression[bar % len(progression)]
                notes = [chord_root + 12, chord_root + 15, chord_root + 19]
                add_track_notes(track, notes, start_tick=0 if bar == 0 else ticks_per_bar, duration=ticks_per_bar * 2, velocity=config['velocity'])
        elif config['pattern'] == 'counterpoint':
            sequence = make_counterpoint(scale, progression, bars, step=2, length=ticks_per_beat * 2)
            for i, (note, length) in enumerate(sequence):
                track.append(Message('note_on', note=note, velocity=config['velocity'], time=0 if i == 0 else ticks_per_bar))
                track.append(Message('note_off', note=note, velocity=config['velocity'] // 2, time=length))
        elif config['pattern'] == 'texture':
            for bar in range(bars):
                note = scale[(bar * 2) % len(scale)] + 12 * 4
                track.append(Message('note_on', note=note, velocity=config['velocity'], time=0 if bar == 0 else ticks_per_bar * 2))
                track.append(Message('note_off', note=note, velocity=config['velocity'] // 2, time=ticks_per_bar * 2))
        elif config['pattern'] == 'ambience':
            for bar in range(0, bars, 2):
                note = scale[random.choice([1, 3, 5, 6])] + 12 * 4
                track.append(Message('note_on', note=note, velocity=config['velocity'], time=0 if bar == 0 else ticks_per_bar * 2))
                track.append(Message('note_off', note=note, velocity=config['velocity'] // 2, time=ticks_per_bar * 4))
        elif config['pattern'] == 'dark_lead':
            for bar in range(bars):
                note = scale[(bar * 3 + 1) % len(scale)] + 12 * 5
                track.append(Message('note_on', note=note, velocity=config['velocity'], time=0 if bar == 0 else ticks_per_bar // 2))
                track.append(Message('note_off', note=note, velocity=config['velocity'] // 2, time=ticks_per_beat))
        elif config['pattern'] == 'sweep':
            for bar in range(bars):
                for i in range(3):
                    note = scale[(i + bar) % len(scale)] + 12 * 4
                    time = 0 if (bar == 0 and i == 0) else ticks_per_beat // 2
                    track.append(Message('note_on', note=note, velocity=config['velocity'], time=time))
                    track.append(Message('note_off', note=note, velocity=config['velocity'] // 2, time=ticks_per_beat // 2))
        elif config['pattern'] == 'sub':
            for bar in range(bars):
                note = progression[bar % len(progression)] - 24
                track.append(Message('note_on', note=note, velocity=config['velocity'], time=0 if bar == 0 else ticks_per_bar))
                track.append(Message('note_off', note=note, velocity=config['velocity'] // 2, time=ticks_per_bar))

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_title = ''.join(ch for ch in title.lower().replace(' ', '_') if ch.isalnum() or ch == '_')
    file_name = f"{safe_title}_{timestamp}.mid"
    path = os.path.join(output_dir, file_name)
    midi.save(path)
    return path


def parse_args():
    parser = argparse.ArgumentParser(description='Gerador de MIDI dungeon synth para FL Studio (até 12 faixas).')
    parser.add_argument('--title', default='dungeon_synth_release', help='Nome do release/MIDI file')
    parser.add_argument('--tempo', type=int, default=60, help='BPM do projeto (50-80 recomendado)')
    parser.add_argument('--bars', type=int, default=32, help='Quantidade de compassos do release')
    parser.add_argument('--tracks', type=int, default=8, choices=range(1, 13), help='Número de tracks (1-12)')
    parser.add_argument('--seed', type=int, default=None, help='Seed para gerar variações diferentes ou repetir o mesmo resultado')
    parser.add_argument('--output-dir', default='releases', help='Pasta onde o MIDI será salvo')
    return parser.parse_args()


def main():
    args = parse_args()
    seed = args.seed if args.seed is not None else random.randint(0, 2**31 - 1)
    path = create_midi(args.title, clamp(args.tempo, 40, 90), clamp(args.bars, 8, 128), args.tracks, seed, args.output_dir)
    print('MIDI gerado com sucesso:')
    print(f'  arquivo: {path}')
    print(f'  tempo: {args.tempo} BPM')
    print(f'  compassos: {args.bars}')
    print(f'  tracks: {args.tracks}')
    print(f'  seed: {seed}')


if __name__ == '__main__':
    main()
