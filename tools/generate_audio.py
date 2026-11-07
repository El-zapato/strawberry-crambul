"""Genera la música y efectos de sonido placeholder (estilo chiptune).

Uso:  python3 tools/generate_audio.py

Todo se sintetiza aquí (sin samples externos). Los WAV se escriben en
assets/audio/music y assets/audio/sfx; el equipo puede reemplazarlos por su
propia música manteniendo el mismo nombre de archivo.
"""
import math
import os
import random
import struct
import wave

RATE = 22050
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "audio")


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ---------------------------------------------------------------- osciladores
def square(phase, duty=0.5):
    return 1.0 if (phase % 1.0) < duty else -1.0


def triangle(phase):
    p = phase % 1.0
    return 4 * p - 1 if p < 0.5 else 3 - 4 * p


class Noise:
    def __init__(self, seed=1):
        self.rnd = random.Random(seed)
        self.last = 0.0

    def sample(self, smooth=0.0):
        v = self.rnd.uniform(-1, 1)
        self.last = self.last * smooth + v * (1 - smooth)
        return self.last


class Track:
    def __init__(self, seconds):
        self.buf = [0.0] * int(seconds * RATE)

    def add(self, start, dur, fn, vol=0.3, attack=0.005, release=0.05):
        """fn(t, i) -> muestra en [-1, 1]; t en segundos desde el inicio de la nota"""
        s0 = int(start * RATE)
        n = int(dur * RATE)
        for i in range(n):
            j = s0 + i
            if j >= len(self.buf):
                break
            t = i / RATE
            env = min(1.0, t / attack) if attack > 0 else 1.0
            left = dur - t
            if left < release:
                env *= max(0.0, left / release)
            self.buf[j] += fn(t, i) * vol * env

    def note(self, start, dur, n, wave_kind="square", vol=0.2, duty=0.5, decay=0.0, vibrato=0.0):
        f = midi(n)

        def fn(t, i):
            ph = f * t + (vibrato * math.sin(2 * math.pi * 5 * t) / 5 if vibrato else 0)
            v = square(ph, duty) if wave_kind == "square" else triangle(ph)
            return v * (math.exp(-decay * t) if decay else 1.0)

        self.add(start, dur, fn, vol)

    def save(self, path, gain=1.0):
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        peak = max(1e-6, max(abs(v) for v in self.buf))
        scale = gain * min(1.0, 0.95 / peak)
        with wave.open(full, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v * scale)) * 32767))
                                   for v in self.buf))


# ---------------------------------------------------------------- utilidades musicales
def melody(track, notes, bpm, start=0.0, **kw):
    beat = 60.0 / bpm
    t = start
    for n, beats in notes:
        if n is not None:
            track.note(t, beats * beat * 0.95, n, **kw)
        t += beats * beat
    return t


def drums(track, bars, bpm, start=0.0, seed=3):
    beat = 60.0 / bpm
    noise = Noise(seed)
    for b in range(bars * 4):
        t = start + b * beat
        # bombo: triángulo que baja de tono
        if b % 2 == 0:
            track.add(t, 0.12, lambda tt, i: triangle(tt * (120 - 500 * tt)), vol=0.35)
        else:
            track.add(t, 0.08, lambda tt, i: noise.sample(0.3) * math.exp(-30 * tt), vol=0.18)
        for h in (0, 0.5):
            track.add(t + h * beat, 0.03, lambda tt, i: noise.sample(0.0), vol=0.05)


# ---------------------------------------------------------------- música
CHORDS = {"F": [53, 57, 60], "Dm": [50, 53, 57], "Bb": [46, 50, 53], "C": [48, 52, 55],
          "Am": [45, 48, 52], "G": [43, 47, 50], "E": [40, 44, 47]}


def accompaniment(track, prog, bpm, wave_bass="triangle", arp=True, start=0.0, arp_vol=0.06):
    beat = 60.0 / bpm
    for bar, ch in enumerate(prog):
        t0 = start + bar * 4 * beat
        root = CHORDS[ch][0]
        for b in (0, 2):
            track.note(t0 + b * beat, beat * 1.8, root - 12, wave_bass, vol=0.28)
        if arp:
            for k in range(8):
                n = CHORDS[ch][k % 3] + 12
                track.note(t0 + k * beat / 2, beat / 2 * 0.9, n, "square", vol=arp_vol, duty=0.125, decay=6)


MENU_MELODY = [
    (69, 1), (72, 1), (77, 1.5), (76, .5),
    (74, 2), (72, 1), (69, 1),
    (70, 1), (74, 1), (77, 1), (74, 1),
    (72, 3), (None, 1),
    (69, 1), (72, 1), (77, 1), (79, 1),
    (81, 2), (77, 1), (74, 1),
    (74, 1), (72, 1), (70, 1), (67, 1),
    (67, 1), (69, 1), (72, 2),
]
MENU_PROG = ["F", "Dm", "Bb", "C"] * 2


def music_menu():
    bpm = 96
    bars = 16
    tr = Track(bars * 4 * 60 / bpm)
    t = melody(tr, MENU_MELODY, bpm, wave_kind="square", vol=0.13, duty=0.25, vibrato=0.01)
    melody(tr, MENU_MELODY, bpm, start=t, wave_kind="triangle", vol=0.22)
    accompaniment(tr, MENU_PROG * 2, bpm)
    tr.save("music/menu.wav")


LEVEL_MELODY = [
    (76, .5), (79, .5), (76, .5), (72, .5), (74, .5), (76, .5), (79, 1),
    (81, .5), (79, .5), (76, .5), (72, .5), (74, 1), (72, 1),
    (77, .5), (77, .5), (81, .5), (77, .5), (76, .5), (74, .5), (72, 1),
    (74, .5), (76, .5), (77, .5), (74, .5), (79, 2),
    (76, .5), (79, .5), (84, 1), (83, .5), (79, .5), (76, 1),
    (81, 1), (79, .5), (76, .5), (72, 1), (69, 1),
    (77, .5), (76, .5), (74, .5), (72, .5), (69, 1), (72, 1),
    (71, 1), (74, 1), (79, 1), (None, 1),
]
LEVEL_PROG = ["C", "Am", "F", "G"] * 2


def music_level1():
    bpm = 132
    bars = 16
    tr = Track(bars * 4 * 60 / bpm)
    t = melody(tr, LEVEL_MELODY, bpm, wave_kind="square", vol=0.12, duty=0.25)
    # segunda vuelta una octava abajo con eco
    melody(tr, [(n - 12 if n else None, b) for n, b in LEVEL_MELODY], bpm, start=t,
           wave_kind="square", vol=0.12, duty=0.5)
    melody(tr, LEVEL_MELODY, bpm, start=t + 60 / bpm / 2, wave_kind="triangle", vol=0.07)
    accompaniment(tr, LEVEL_PROG * 2, bpm, arp_vol=0.05)
    drums(tr, bars, bpm)
    tr.save("music/level1.wav")


def music_bad_ending():
    # caja de música lenta en menor
    bpm = 60
    prog = ["Am", "F", "Dm", "E"]
    tr = Track(len(prog) * 4)
    beat = 1.0
    for bar, ch in enumerate(prog):
        for k in range(4):
            n = CHORDS[ch][[0, 1, 2, 1][k]] + 24
            tr.note(bar * 4 + k * beat, 1.6, n, "triangle", vol=0.22, decay=2.5)
        tr.note(bar * 4, 3.9, CHORDS[ch][0] - 12, "triangle", vol=0.2)
    tr.save("music/bad_ending.wav")


def music_true_ending():
    bpm = 80
    tr = Track(8 * 4 * 60 / bpm)
    melody(tr, MENU_MELODY, bpm, wave_kind="triangle", vol=0.26, vibrato=0.015)
    melody(tr, [(n + 12 if n else None, b) for n, b in MENU_MELODY], bpm, wave_kind="square",
           vol=0.05, duty=0.125)
    accompaniment(tr, MENU_PROG, bpm, arp_vol=0.07)
    tr.save("music/true_ending.wav")


# ---------------------------------------------------------------- efectos
def sweep(tr, start, dur, f0, f1, kind="square", vol=0.3, duty=0.5):
    state = {"ph": 0.0}

    def fn(t, i):
        f = f0 + (f1 - f0) * (t / dur)
        state["ph"] += f / RATE
        return square(state["ph"], duty) if kind == "square" else triangle(state["ph"])

    tr.add(start, dur, fn, vol, release=dur * 0.4)


def sfx():
    tr = Track(0.16)
    sweep(tr, 0, 0.15, 260, 620, duty=0.25)
    tr.save("sfx/jump.wav", 0.6)

    tr = Track(0.3)
    nz = Noise(5)
    tr.add(0, 0.3, lambda t, i: nz.sample(0.85) * math.sin(math.pi * t / 0.3), vol=0.8, release=0.1)
    sweep(tr, 0, 0.2, 500, 900, "triangle", vol=0.15)
    tr.save("sfx/glide.wav", 0.5)

    tr = Track(0.32)
    sweep(tr, 0, 0.3, 420, 110, duty=0.5, vol=0.3)
    nz = Noise(9)
    tr.add(0, 0.12, lambda t, i: nz.sample(0.2), vol=0.25)
    tr.save("sfx/hurt.wav", 0.7)

    tr = Track(0.45)
    for k, n in enumerate((84, 88, 91, 96)):
        tr.note(k * 0.07, 0.2, n, "square", vol=0.18, duty=0.25, decay=8)
    tr.save("sfx/collect.wav", 0.6)

    tr = Track(0.6)
    tr.note(0, 0.25, 79, "triangle", vol=0.3, decay=5)
    tr.note(0.12, 0.45, 84, "triangle", vol=0.3, decay=4)
    tr.save("sfx/checkpoint.wav", 0.6)

    tr = Track(0.05)
    tr.note(0, 0.04, 81, "square", vol=0.2, duty=0.25)
    tr.save("sfx/ui_hover.wav", 0.35)

    tr = Track(0.1)
    sweep(tr, 0, 0.09, 660, 990, duty=0.25, vol=0.25)
    tr.save("sfx/ui_click.wav", 0.5)

    # muerte del personaje: caída lenta y grave
    tr = Track(0.9)
    sweep(tr, 0, 0.85, 330, 55, duty=0.5, vol=0.3)
    sweep(tr, 0, 0.85, 349, 58, "triangle", vol=0.3)
    tr.save("sfx/death.wav", 0.8)

    # jumpscare: golpe de ruido + chillido disonante
    tr = Track(1.0)
    nz = Noise(13)
    tr.add(0, 0.9, lambda t, i: nz.sample(0.05) * math.exp(-2.5 * t), vol=0.6, attack=0.001)
    sweep(tr, 0, 0.9, 1800, 700, duty=0.3, vol=0.25)
    sweep(tr, 0, 0.9, 1270, 495, duty=0.5, vol=0.25)
    tr.save("sfx/jumpscare.wav", 1.0)

    # el puente desapareció: zumbido grave con tritono
    tr = Track(4.0)
    for n, v in ((33, 0.3), (39, 0.18), (45, 0.12)):
        f = midi(n)
        tr.add(0, 4.0, lambda t, i, f=f: triangle(f * t) * (0.6 + 0.4 * math.sin(2 * math.pi * 0.7 * t)),
               vol=v, attack=0.8, release=1.5)
    tr.note(0.5, 3.0, 70, "square", vol=0.04, duty=0.125, vibrato=0.05)
    tr.save("sfx/bridge.wav", 0.9)


if __name__ == "__main__":
    music_menu()
    music_level1()
    music_bad_ending()
    music_true_ending()
    sfx()
    print("Audio generado en", os.path.normpath(ROOT))
