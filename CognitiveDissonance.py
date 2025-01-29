import pygame
import numpy as np
import pandas as pd
import time

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))  # Adjust size as needed
pygame.display.set_caption("Cognitive Dissonance Experiment")

strong_beat = pygame.mixer.Sound(r"C:\Users\sreep\OneDrive\Desktop\SaiU\Honors Cogneuro Research\kick-classic.wav")
weak_beat = pygame.mixer.Sound(r"C:\Users\sreep\OneDrive\Desktop\SaiU\Honors Cogneuro Research\snare-808.wav")

# Generate the tones
def generate_complex_tone(frequencies, duration=0.2, sample_rate=44100, amplitude=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = sum(amplitude * np.sin(2 * np.pi * freq * t) for freq in frequencies)
    max_amplitude = np.max(np.abs(tone))
    if max_amplitude > 1.0:
        tone /= max_amplitude
    stereo_tone = np.array([tone, tone]).T
    stereo_tone = np.ascontiguousarray(stereo_tone)
    return pygame.sndarray.make_sound((stereo_tone * 32767).astype(np.int16))

in_tune_frequencies = [600, 600 * 5/4, 600 * 3/2]  # Root, perfect 4th, perfect 5th
out_of_tune_frequencies = [600, 600 * 5/4, 600 * 2.85/2]  # Slightly detuned 5th

# Generate tones
in_tune_tone = generate_complex_tone(in_tune_frequencies)
out_of_tune_tone = generate_complex_tone(out_of_tune_frequencies)

# Prepare reaction data
reaction_data = pd.DataFrame(columns=['Gap', 'tGap', 'Tone', 'Key', 'RT'])

# Generate shuffled trials without repeating tones in successive trials
gaps = [i * 10 for i in range(5, 51)]  # Gap values in ms
tones = [1, 2]  # Tone types (1 for in-tune, 2 for out-of-tune)

# Prepare trials with shuffling logic
df1 = pd.DataFrame({'Gap': gaps, 'Tone': 1, 'tGap': 0, 'Key': 0, 'RT': 0})  # In-tune trials
df2 = pd.DataFrame({'Gap': gaps, 'Tone': 2, 'tGap': 0, 'Key': 0, 'RT': 0})  # Out-of-tune trials
dfx1 = df1.sample(frac=1).reset_index(drop=True)  # Shuffle in-tune trials
dfx2 = df2.sample(frac=1).reset_index(drop=True)  # Shuffle out-of-tune trials

# Concatenate and shuffle all trials
reaction_data = pd.concat([dfx1, dfx2]).sample(frac=1).reset_index(drop=True)

tempo = 0.2   # Time between beats in seconds
trial_num = 0
running = True
num_repetitions = 2  # Repetitions for strong and weak beats

# Main experiment loop
while running and trial_num < len(reaction_data):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Space bar starts the trial
                for rep in range(num_repetitions):  # Repeat the sequence
                    # Play strong beat
                    pygame.mixer.Sound.play(strong_beat)
                    time.sleep(0.250)

                    # Play weak beats
                    for i in range(3):  # 3 weak beats
                        pygame.mixer.Sound.play(weak_beat)
                        if not (rep == num_repetitions - 1 and i == 2):
                            time.sleep(0.250)
                        
                # After the 8th beat (strong + 3 weak x 2 repetitions), apply the gap
                gap = reaction_data.loc[trial_num, 'Gap'] / 1000  # Convert ms to seconds
                time.sleep(gap)  # Wait for the predefined gap before playing the tone

                # Play in-tune or out-of-tune tone
                tone_type = reaction_data.loc[trial_num, 'Tone']
                if tone_type == 1:
                    pygame.mixer.Sound.play(in_tune_tone)
                else:
                    pygame.mixer.Sound.play(out_of_tune_tone)

                t0 = time.time()  # Record the time when the tone plays
                reaction_data.loc[trial_num, 'tGap'] = round(gap * 1000, 0)  # Record tGap in ms

                # Waiting for response
                waiting_for_response = True
                while waiting_for_response:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_m:  # M key for "in-tune"
                                reaction_data.loc[trial_num, 'Key'] = 'M'
                                reaction_data.loc[trial_num, 'RT'] = round((time.time() - t0) * 1000, 0)
                                print(reaction_data.loc[trial_num])
                                trial_num += 1
                                waiting_for_response = False
                            elif event.key == pygame.K_c:  # C key for "out-of-tune"
                                reaction_data.loc[trial_num, 'Key'] = 'C'
                                reaction_data.loc[trial_num, 'RT'] = round((time.time() - t0) * 1000, 0)
                                print(reaction_data.loc[trial_num])
                                trial_num += 1
                                waiting_for_response = False
                    
                reaction_data.to_csv("pilot1_4data.csv", index=False)
                print("END")

# Quit pygame
pygame.quit()

