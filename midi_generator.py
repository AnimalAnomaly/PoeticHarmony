import os
import random
from midiutil import MIDIFile
import logging

class MIDIGenerator:
    def __init__(self):
        self.scales = {
            'C': [60, 62, 64, 65, 67, 69, 71],  # C major
            'Am': [57, 59, 60, 62, 64, 65, 67],  # A minor
            'G': [67, 69, 71, 72, 74, 76, 78],   # G major
            'Em': [64, 66, 67, 69, 71, 72, 74],  # E minor
            'F': [65, 67, 69, 70, 72, 74, 76],   # F major
            'Dm': [62, 64, 65, 67, 69, 70, 72],  # D minor
        }
        
        self.chord_progressions = {
            'major': [[0, 2, 4], [3, 5, 0], [1, 3, 5], [0, 2, 4]],  # I-IV-ii-I
            'minor': [[0, 2, 4], [3, 5, 0], [1, 3, 5], [0, 2, 4]],  # i-iv-ii-i
        }
        
        self.instruments = {
            'piano': 0,
            'acoustic_guitar': 24,
            'electric_guitar': 27,
            'strings': 48,
            'violin': 40,
            'cello': 42,
            'flute': 73,
            'clarinet': 71,
            'drums': 128  # Percussion channel
        }
    
    def generate_composition(self, analysis, title="Untitled", instruments=['piano'], filename=None):
        """
        Generate MIDI composition based on poetry analysis
        """
        try:
            if not filename:
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_title.replace(' ', '_')}.mid"
            
            # Create MIDI file
            midi = MIDIFile(len(instruments))
            
            # Set tempo
            tempo = analysis.get('tempo_suggestion', 120)
            for i in range(len(instruments)):
                midi.addTempo(i, 0, tempo)
            
            # Generate music for each instrument
            for i, instrument in enumerate(instruments):
                self._add_instrument_track(midi, i, instrument, analysis)
            
            # Save MIDI file
            midi_path = os.path.join('static', 'midi', filename)
            os.makedirs(os.path.dirname(midi_path), exist_ok=True)
            
            with open(midi_path, 'wb') as output_file:
                midi.writeFile(output_file)
            
            logging.info(f"Generated MIDI file: {midi_path}")
            return filename
            
        except Exception as e:
            logging.error(f"Error generating MIDI: {str(e)}")
            raise
    
    def _add_instrument_track(self, midi, track, instrument_name, analysis):
        """Add a track for a specific instrument"""
        # Set instrument
        program = self.instruments.get(instrument_name, 0)
        if instrument_name != 'drums':
            midi.addProgramChange(track, 0, 0, program)
        
        # Get musical parameters
        key = analysis.get('key_suggestion', 'C')
        scale = self.scales.get(key, self.scales['C'])
        syllable_counts = analysis.get('syllable_counts', [8, 8, 8, 8])
        line_count = analysis.get('line_count', 4)
        
        if instrument_name == 'drums':
            self._add_drum_track(midi, track, analysis)
        elif instrument_name in ['piano', 'acoustic_guitar', 'electric_guitar']:
            self._add_melody_and_harmony_track(midi, track, scale, syllable_counts, analysis)
        else:
            self._add_melody_track(midi, track, scale, syllable_counts, analysis)
    
    def _add_melody_track(self, midi, track, scale, syllable_counts, analysis):
        """Add a melody track"""
        time = 0
        beat_duration = 0.5  # Half note per syllable
        
        for line_idx, syllable_count in enumerate(syllable_counts):
            # Generate melody for this line
            for syllable in range(syllable_count):
                # Choose note based on position and analysis
                note_idx = self._choose_note_index(syllable, syllable_count, line_idx, analysis)
                note = scale[note_idx % len(scale)]
                
                # Add some octave variation
                if random.random() < 0.3:
                    note += 12 if random.random() < 0.5 else -12
                
                # Ensure note is in reasonable range
                note = max(48, min(84, note))
                
                # Add note
                velocity = self._get_velocity(syllable, syllable_count, analysis)
                midi.addNote(track, 0, note, time, beat_duration, velocity)
                time += beat_duration
            
            # Add pause between lines
            time += beat_duration
    
    def _add_melody_and_harmony_track(self, midi, track, scale, syllable_counts, analysis):
        """Add both melody and harmony for piano/guitar"""
        time = 0
        beat_duration = 0.5
        
        # Add bass line first
        key = analysis.get('key_suggestion', 'C')
        is_minor = 'm' in key
        chord_progression = self.chord_progressions['minor' if is_minor else 'major']
        
        chord_time = 0
        chord_duration = 2.0  # 2 beats per chord
        
        for line_idx, syllable_count in enumerate(syllable_counts):
            # Add chord for this line
            chord_idx = line_idx % len(chord_progression)
            chord = chord_progression[chord_idx]
            
            # Add bass note
            bass_note = scale[chord[0]] - 24  # One octave lower
            bass_note = max(24, min(60, bass_note))
            midi.addNote(track, 0, bass_note, chord_time, chord_duration, 70)
            
            # Add chord notes
            for note_idx in chord:
                chord_note = scale[note_idx % len(scale)] - 12
                chord_note = max(36, min(72, chord_note))
                midi.addNote(track, 0, chord_note, chord_time, chord_duration, 60)
            
            chord_time += chord_duration
        
        # Add melody on top
        time = 0
        for line_idx, syllable_count in enumerate(syllable_counts):
            for syllable in range(syllable_count):
                note_idx = self._choose_note_index(syllable, syllable_count, line_idx, analysis)
                note = scale[note_idx % len(scale)]
                
                # Melody octave
                note = max(60, min(84, note))
                
                velocity = self._get_velocity(syllable, syllable_count, analysis)
                midi.addNote(track, 0, note, time, beat_duration, velocity)
                time += beat_duration
            
            time += beat_duration
    
    def _add_drum_track(self, midi, track, analysis):
        """Add drum track"""
        # Drum channel is 9 (0-indexed)
        channel = 9
        
        # Basic drum pattern
        kick = 36
        snare = 38
        hihat = 42
        
        time = 0
        beat_duration = 0.5
        total_beats = sum(analysis.get('syllable_counts', [8, 8, 8, 8])) + len(analysis.get('syllable_counts', [8, 8, 8, 8]))
        
        for beat in range(int(total_beats)):
            # Kick on beats 1 and 3
            if beat % 4 == 0 or beat % 4 == 2:
                midi.addNote(track, channel, kick, time, beat_duration, 100)
            
            # Snare on beats 2 and 4
            if beat % 4 == 1 or beat % 4 == 3:
                midi.addNote(track, channel, snare, time, beat_duration, 90)
            
            # Hi-hat on every beat
            midi.addNote(track, channel, hihat, time, beat_duration * 0.8, 70)
            
            time += beat_duration
    
    def _choose_note_index(self, syllable_pos, total_syllables, line_idx, analysis):
        """Choose a note index based on position and analysis"""
        # Start with scale degree based on position
        if syllable_pos == 0:
            # Start of line - use tonic
            return 0
        elif syllable_pos == total_syllables - 1:
            # End of line - resolve to tonic or dominant
            return 0 if random.random() < 0.7 else 4
        else:
            # Middle of line - use scale degrees with some logic
            sentiment = analysis.get('sentiment', {})
            mood = sentiment.get('mood', 'neutral')
            
            if mood == 'positive':
                # Use brighter notes (3rd, 5th)
                return random.choice([2, 4, 6])
            elif mood == 'negative':
                # Use more somber notes (2nd, 6th)
                return random.choice([1, 3, 5])
            else:
                # Neutral - use all scale degrees
                return random.randint(0, 6)
    
    def _get_velocity(self, syllable_pos, total_syllables, analysis):
        """Get note velocity based on position and analysis"""
        base_velocity = 80
        
        # Vary velocity based on position
        if syllable_pos == 0 or syllable_pos == total_syllables - 1:
            # Emphasize beginning and end
            velocity = base_velocity + 10
        else:
            velocity = base_velocity + random.randint(-10, 10)
        
        # Adjust based on sentiment
        sentiment = analysis.get('sentiment', {})
        mood = sentiment.get('mood', 'neutral')
        
        if mood == 'positive':
            velocity += 10
        elif mood == 'negative':
            velocity -= 10
        
        return max(40, min(127, velocity))
