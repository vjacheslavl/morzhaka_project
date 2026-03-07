import pygame
import array
import math

pygame.mixer.init()


def create_shoot_sound():
    sample_rate = 22050
    duration = 0.1
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        freq = 800 - (t * 4000)
        buf[i] = int(4000 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.3)
    return sound


def create_damage_sound():
    sample_rate = 22050
    duration = 0.15
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        freq = 200 + (t * 100)
        buf[i] = int(6000 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.4)
    return sound


def create_kill_sound():
    sample_rate = 22050
    duration = 0.2
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        freq = 400 + (t * 800)
        buf[i] = int(5000 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.4)
    return sound


def create_heal_sound():
    sample_rate = 22050
    duration = 0.25
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        freq = 600 + (t * 400)
        buf[i] = int(3000 * math.sin(2 * math.pi * freq * t) * math.sin(math.pi * t / duration))
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.4)
    return sound


def create_victory_sound():
    sample_rate = 22050
    duration = 2.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    
    ta_duration = 0.25
    da_start = 0.3
    
    ta_freq = 392.00
    da_chord = [523.25, 659.25, 783.99, 1046.50]
    
    for i in range(n_samples):
        t = i / sample_rate
        val = 0
        
        if t < ta_duration:
            envelope = min(1.0, t * 40) * max(0.0, 1 - t / ta_duration)
            val = math.sin(2 * math.pi * ta_freq * t)
            val += 0.5 * math.sin(2 * math.pi * ta_freq * 2 * t)
            val *= envelope * 0.7
        
        if t >= da_start:
            chord_t = t - da_start
            chord_duration = duration - da_start
            envelope = min(1.0, chord_t * 15) * max(0.0, 1 - (chord_t / chord_duration) * 0.6)
            
            chord_val = 0
            for freq in da_chord:
                chord_val += math.sin(2 * math.pi * freq * t)
                chord_val += 0.3 * math.sin(2 * math.pi * freq * 2 * t)
            chord_val /= len(da_chord)
            val += chord_val * envelope
        
        buf[i] = int(4500 * val)
    
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.5)
    return sound


def create_background_music():
    sample_rate = 22050
    duration = 8.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    
    notes = [130.81, 146.83, 164.81, 174.61, 196.00, 220.00, 246.94, 261.63]
    melody = [0, 2, 4, 5, 4, 2, 3, 1, 0, 4, 5, 7, 5, 4, 2, 0]
    note_duration = duration / len(melody)
    
    for i in range(n_samples):
        t = i / sample_rate
        note_idx = int(t / note_duration) % len(melody)
        freq = notes[melody[note_idx]]
        
        bass_freq = freq / 2
        val = int(1500 * math.sin(2 * math.pi * freq * t))
        val += int(1000 * math.sin(2 * math.pi * bass_freq * t))
        val += int(500 * math.sin(2 * math.pi * freq * 1.5 * t))
        
        envelope = min(1.0, (t % note_duration) * 10) * max(0.3, 1 - (t % note_duration) / note_duration)
        buf[i] = int(val * envelope * 0.4)
    
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.25)
    return sound


def create_boss_music():
    sample_rate = 22050
    duration = 3.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    
    power_chords = [55.00, 61.74, 55.00, 73.42, 55.00, 82.41, 73.42, 55.00]
    note_duration = duration / len(power_chords)
    
    for i in range(n_samples):
        t = i / sample_rate
        note_idx = int(t / note_duration) % len(power_chords)
        root = power_chords[note_idx]
        fifth = root * 1.5
        octave = root * 2
        
        guitar = math.sin(2 * math.pi * root * t)
        guitar += 0.9 * math.sin(2 * math.pi * fifth * t)
        guitar += 0.7 * math.sin(2 * math.pi * octave * t)
        guitar += 0.5 * math.sin(2 * math.pi * root * 0.5 * t)
        
        distortion = math.tanh(guitar * 4) * 0.8
        
        for h in range(2, 10):
            distortion += 0.2 * math.sin(2 * math.pi * root * h * t + math.sin(t * 5)) / h
        
        beat_pos = (t * 6) % 1
        kick = 0
        if beat_pos < 0.08:
            kick = math.sin(2 * math.pi * 50 * beat_pos) * (1 - beat_pos * 12) * 1.0
        snare = 0
        if int(t * 6) % 2 == 1 and beat_pos < 0.04:
            snare = (hash(int(t * 10000)) % 1000 / 500 - 1) * 0.6
        double_kick = 0
        if int(t * 12) % 4 == 3 and (t * 12) % 1 < 0.1:
            double_kick = math.sin(2 * math.pi * 55 * ((t * 12) % 1)) * 0.5
        
        envelope = min(1.0, (t % note_duration) * 30) * max(0.7, 1 - (t % note_duration) / note_duration * 0.4)
        val = int((distortion * 3000 + kick * 3500 + snare * 2500 + double_kick * 2000) * envelope)
        buf[i] = max(-32767, min(32767, val))
    
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.35)
    return sound


def create_ice_cave_music():
    sample_rate = 22050
    duration = 6.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)

    melody = [261.63, 293.66, 261.63, 246.94, 220.00, 246.94, 261.63, 293.66]
    bass_notes = [130.81, 130.81, 146.83, 146.83, 110.00, 110.00, 130.81, 130.81]
    note_duration = duration / len(melody)

    for i in range(n_samples):
        t = i / sample_rate
        note_idx = int(t / note_duration) % len(melody)
        freq = melody[note_idx]
        bass_freq = bass_notes[note_idx]
        
        wind = math.sin(2 * math.pi * 80 * t + math.sin(t * 0.3) * 5) * 0.08
        wind += math.sin(2 * math.pi * 120 * t + math.sin(t * 0.5) * 3) * 0.05
        
        crystal = math.sin(2 * math.pi * freq * t) * 0.25
        crystal += math.sin(2 * math.pi * freq * 2.0 * t) * 0.12
        crystal += math.sin(2 * math.pi * freq * 3.0 * t) * 0.06
        
        detune = math.sin(t * 0.8) * 2
        shimmer = math.sin(2 * math.pi * (freq * 1.5 + detune) * t) * 0.1
        shimmer *= (1 + math.sin(t * 4)) * 0.5
        
        bass = math.sin(2 * math.pi * bass_freq * t) * 0.2
        bass += math.sin(2 * math.pi * bass_freq * 0.5 * t) * 0.15
        
        echo_delay = 0.15
        echo_t = max(0, t - echo_delay)
        echo_note_idx = int(echo_t / note_duration) % len(melody)
        echo_freq = melody[echo_note_idx]
        echo = math.sin(2 * math.pi * echo_freq * t) * 0.08 if t > echo_delay else 0
        
        chime_trigger = (t % 1.5) < 0.1
        chime = 0
        if chime_trigger:
            chime_t = t % 1.5
            chime = math.sin(2 * math.pi * 880 * chime_t) * math.exp(-chime_t * 20) * 0.15
        
        note_pos = (t % note_duration) / note_duration
        envelope = min(1.0, note_pos * 10) * max(0.4, 1 - note_pos * 0.5)
        
        sample = (wind + crystal + shimmer + bass + echo + chime) * envelope
        val = int(sample * 6000)
        buf[i] = max(-32767, min(32767, val))

    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.3)
    return sound


def create_final_boss_music():
    sample_rate = 22050
    duration = 8.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)

    section1 = [55.00, 65.41, 73.42, 82.41, 73.42, 65.41, 55.00, 49.00]
    section2 = [55.00, 58.27, 69.30, 82.41, 87.31, 82.41, 69.30, 55.00]
    
    all_chords = section1 + section2
    note_duration = duration / len(all_chords)

    for i in range(n_samples):
        t = i / sample_rate
        note_idx = int(t / note_duration) % len(all_chords)
        section = note_idx // 8
        root = all_chords[note_idx]
        fifth = root * 1.5
        octave = root * 2

        deep_bass = math.sin(2 * math.pi * root * 0.25 * t) * 1.2
        deep_bass += math.sin(2 * math.pi * root * 0.5 * t) * 0.9

        if section == 0:
            power = math.tanh(math.sin(2 * math.pi * root * t) * 4) * 0.7
            power += math.tanh(math.sin(2 * math.pi * fifth * t) * 3) * 0.5
            for h in range(2, 8):
                power += 0.1 * math.sin(2 * math.pi * root * h * t) / h
        else:
            power = math.tanh(math.sin(2 * math.pi * root * t) * 5) * 0.8
            power += math.tanh(math.sin(2 * math.pi * fifth * t) * 4) * 0.6
            power += math.tanh(math.sin(2 * math.pi * octave * t) * 3) * 0.4
            for h in range(2, 10):
                power += 0.12 * math.sin(2 * math.pi * root * h * t + math.sin(t * 5)) / h

        bpm = 8
        beat_pos = (t * bpm) % 1
        kick = 0
        if beat_pos < 0.07:
            kick = math.sin(2 * math.pi * 38 * beat_pos) * (1 - beat_pos * 14) * 1.4

        double_kick = 0
        if section == 1 and (int(t * bpm) % 4 == 3) and beat_pos > 0.5 and beat_pos < 0.57:
            double_kick = math.sin(2 * math.pi * 38 * (beat_pos - 0.5)) * (1 - (beat_pos - 0.5) * 14) * 1.2

        snare = 0
        if int(t * bpm) % 2 == 1 and beat_pos < 0.04:
            snare = (hash(int(t * 10000)) % 1000 / 500 - 1) * 0.9

        evil_lead = math.sin(2 * math.pi * root * 4 * t + math.sin(t * 12) * 2) * 0.35
        if section == 1:
            evil_lead += math.sin(2 * math.pi * root * 3 * t + math.sin(t * 8)) * 0.25

        choir = math.sin(2 * math.pi * root * 2 * t) * 0.25
        choir += math.sin(2 * math.pi * fifth * t) * 0.2
        choir *= (0.6 + 0.4 * math.sin(t * 2))

        strings = math.sin(2 * math.pi * root * t) * 0.3
        strings += math.sin(2 * math.pi * root * 1.5 * t) * 0.2
        strings *= (0.7 + 0.3 * math.sin(t * 3))

        note_pos = t % note_duration
        envelope = min(1.0, note_pos * 30) * max(0.75, 1 - note_pos / note_duration * 0.25)
        
        intensity = 0.85 + 0.15 * (section)

        val = int((deep_bass * 2800 + power * 3500 + kick * 4500 + double_kick * 3800 + 
                   snare * 3000 + evil_lead * 2200 + choir * 1800 + strings * 1500) * envelope * intensity)
        buf[i] = max(-32767, min(32767, val))

    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.5)
    return sound


def create_castle_music():
    sample_rate = 22050
    duration = 4.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    
    notes = [110.00, 116.54, 130.81, 116.54, 110.00, 103.83, 98.00, 103.83]
    note_duration = duration / len(notes)
    
    for i in range(n_samples):
        t = i / sample_rate
        note_idx = int(t / note_duration) % len(notes)
        root = notes[note_idx]
        
        organ = math.sin(2 * math.pi * root * t) * 0.4
        organ += math.sin(2 * math.pi * root * 2 * t) * 0.2
        organ += math.sin(2 * math.pi * root * 0.5 * t) * 0.3
        
        choir = math.sin(2 * math.pi * root * 1.5 * t + math.sin(t * 2)) * 0.15
        
        beat_pos = (t * 2) % 1
        drum = 0
        if beat_pos < 0.1:
            drum = math.sin(2 * math.pi * 40 * beat_pos) * (1 - beat_pos * 10) * 0.5
        
        envelope = min(1.0, (t % note_duration) * 8) * max(0.4, 1 - (t % note_duration) / note_duration * 0.5)
        val = int((organ + choir + drum) * 4500 * envelope)
        buf[i] = max(-32767, min(32767, val))
    
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(0.3)
    return sound


# Initialize sounds
SHOOT_SOUND = create_shoot_sound()
DAMAGE_SOUND = create_damage_sound()
KILL_SOUND = create_kill_sound()
HEAL_SOUND = create_heal_sound()
VICTORY_SOUND = create_victory_sound()
BACKGROUND_MUSIC = create_background_music()
BOSS_MUSIC = create_boss_music()
ICE_CAVE_MUSIC = create_ice_cave_music()
FINAL_BOSS_MUSIC = create_final_boss_music()
CASTLE_MUSIC = create_castle_music()
