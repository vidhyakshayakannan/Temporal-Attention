import pygame
import numpy as np
import pandas as pd
import time
import sys
import random

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Set up the display
screen = pygame.display.set_mode((1000, 800))  
pygame.display.set_caption("Cognitive Dissonance Experiment")

strong_beat = pygame.mixer.Sound("/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Drum Sounds/kick-classic.wav")
weak_beat = pygame.mixer.Sound("/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Drum Sounds/snare-808.wav")

# Generate the tones
def generate_complex_tone(frequencies, duration=0.15, sample_rate=44100, amplitude=0.5):
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

gaps = [i * 10 for i in range(5, 51)]  # Gap values in ms
tones = [1, 2]  # Tone types (1 for in-tune, 2 for out-of-tune)

df1 = pd.DataFrame({'Gap': gaps, 'Tone': 1, 'tGap': 0, 'Key': 0, 'RT': 0})  # In-tune trials
df2 = pd.DataFrame({'Gap': gaps, 'Tone': 2, 'tGap': 0, 'Key': 0, 'RT': 0})  # Out-of-tune trials

dfx1 = df1.sample(frac=1).reset_index(drop=True)  # Shuffle in-tune trials
dfx2 = df2.sample(frac=1).reset_index(drop=True)  # Shuffle out-of-tune trials

reaction_data = pd.concat([dfx1, dfx2]).sample(frac=1).reset_index(drop=True)

tempo = 0.2   # Time between beats in seconds
trial_num = 0
running = True
num_repetitions = 2  # Repetitions for strong and weak beats

def instruction_screen():
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)
    
    instructions = [
        "Welcome to the experiment.",
        "You will hear a series of tones.",
        "Press 'M' if you think the tone is in tune.",
        "Press 'C' if you think the tone is out of tune.",
        "Try to respond as quickly as possible.",
        "Press SPACE when you are ready to begin."
    ]

    y_offset = 100
    for line in instructions:
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (100, y_offset))
        y_offset += 50

    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False  

    # Small pause before practice trials
    pygame.time.delay(1000)

def first_instruction_screen():
    screen.fill((0, 0, 0))  # Clear screen
    font = pygame.font.Font(None, 36)
    
    instructions = [
        "We will do some practice.",
        "First, you will hear no beats, only a tone.",
        "When you think you hear an in-tune tone, press 'M'.",
        "If you think it is out of tune, press 'C'.",
        "Do this as fast as possible.",
        "When you are ready for the next tone, press the spacebar."
    ]

    y_offset = 100
    for line in instructions:
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (50, y_offset))
        y_offset += 50

    pygame.display.flip()

    # Wait for user to press SPACE before starting practice
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False  

    pygame.time.delay(1000)  # Brief pause before practice starts

# Run instruction screen before practice trials
first_instruction_screen()

for _ in range(20):  # 10 practice trials
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        text = font.render("Listen carefully...", True, (255, 255, 255))
        screen.blit(text, (250, 250))
        pygame.display.flip()
        pygame.time.delay(500)
        
        # Randomly pick tone type
        tone_type = random.choice([1, 2])  
        
        if tone_type == 1:
            pygame.mixer.Sound.play(in_tune_tone)
            tone_label = "In-Tune"
        else:
            pygame.mixer.Sound.play(out_of_tune_tone)
            tone_label = "Out-of-Tune"

        t0 = time.time()
        response = None
        

        while response is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        response = "Correct" if tone_type == 1 else "Incorrect"
                    elif event.key == pygame.K_c:
                        response = "Correct" if tone_type == 2 else "Incorrect"
        
        rt = round((time.time() - t0) * 1000, 0)  # Reaction time in ms

        # Display result
        screen.fill((0, 0, 0))
        result_text = font.render(f"Tone: {tone_label} | RT: {rt} ms | {response}", True, (255, 255, 255))
        screen.blit(result_text, (100, 250))
        pygame.display.flip()
        pygame.time.delay(1500)

# Wait for user to start main experiment
screen.fill((0, 0, 0))
text = font.render("Press SPACE to start the experiment.", True, (255, 255, 255))
screen.blit(text, (200, 300))
pygame.display.flip()

waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            waiting = False
total_trials = len(reaction_data)


def draw_experiment_screen(trial_num, total_trials, first_screen=False):
    screen.fill((0, 0, 0))  # Clear the screen
    font = pygame.font.Font(None, 36)

    if first_screen:  
        instructions = [
            "This is the main experiment",
            "When you think you hear an in-tune tone, press 'M'.",
            "If you think it is out of tune, press 'C'.",
            "Do this as fast as possible.",
            "When you are ready for the next tone, press SPACE.",
        ]
    else:
        instructions = [f"Trial {trial_num+1} / {total_trials}"]

    y_offset = 100
    for line in instructions:
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (50, y_offset))
        y_offset += 50

    pygame.display.flip()  # Update screen

def draw_practice_screen(trial_num, total_trials):
    screen.fill((0, 0, 0))  # Clear the screen
    font = pygame.font.Font(None, 36)

    instructions = [
        "Practice Round",
        "You will hear eight drum beats ",
        "and a randomly induced tone."
        "Press 'M' for In-Tune, 'C' for Out-of-Tune.",
        "Try to respond as fast as possible.",
        "When you're ready for the next tone, press SPACE.",
        f"Practice Trial {trial_num+1} / {total_trials}"
    ]

    y_offset = 100
    for line in instructions:
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (50, y_offset))
        y_offset += 50

    pygame.display.flip()

practice_trials = 20  # Number of practice trials

for trial in range(practice_trials):
    draw_practice_screen(trial, practice_trials)
    waiting_for_next_trial = True
    while waiting_for_next_trial:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting_for_next_trial = False  # Proceed with trial

    # Play beat sequence
    for rep in range(num_repetitions):
        pygame.mixer.Sound.play(strong_beat)
        time.sleep(0.250)
        for i in range(3):
            pygame.mixer.Sound.play(weak_beat)
            if not (rep == num_repetitions - 1 and i == 2):
                time.sleep(0.250)

    gap = random.choice(gaps) / 1000  # Random gap in seconds
    time.sleep(gap)

    tone_type = random.choice([1, 2])
    if tone_type == 1:
        pygame.mixer.Sound.play(in_tune_tone)
    else:
        pygame.mixer.Sound.play(out_of_tune_tone)

    t0 = time.time()
    waiting_for_response = True
    user_key = None
    while waiting_for_response:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    user_key = 'M'
                elif event.key == pygame.K_c:
                    user_key = 'C'
                
                if user_key:
                    rt = round((time.time() - t0) * 1000, 0)
                    correct = (tone_type == 1 and user_key == 'M') or (tone_type == 2 and user_key == 'C')
                    feedback_text = "Correct" if correct else "Incorrect"
                    tone_label = "In-Tune" if tone_type == 1 else "Out-of-Tune"
                    
                    # Display feedback
                    screen.fill((0, 0, 0))
                    font = pygame.font.Font(None, 36)
                    result_text = font.render(f"Tone: {tone_label} - Reaction Time: {rt} ms - {feedback_text}", True, (255, 255, 255))
                    screen.blit(result_text, (100, 250))
                    pygame.display.flip()
                    time.sleep(1.5)
                    waiting_for_response = False

# Wait for user to start main experiment
screen.fill((0, 0, 0))
text = font.render("Press SPACE to start the experiment.", True, (255, 255, 255))
screen.blit(text, (200, 300))
pygame.display.flip()

waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            waiting = False
total_trials = len(reaction_data)


# Main experiment loop
while running and trial_num < total_trials:
    
    draw_experiment_screen(trial_num, total_trials)
    waiting_for_next_trial = True
    while waiting_for_next_trial:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting_for_next_trial = False  # Exit loop and proceed with trial

    # Start trial after SPACE is pressed
    for rep in range(num_repetitions):  # Repeat the sequence
        pygame.mixer.Sound.play(strong_beat)
        time.sleep(0.250)

        for i in range(3):  # 3 weak beats 
            pygame.mixer.Sound.play(weak_beat)
            if not (rep == num_repetitions - 1 and i == 2):
                time.sleep(0.250)
    
    gap = reaction_data.loc[trial_num, 'Gap'] / 1000  # Convert ms to seconds
    time.sleep(gap)  # Apply the gap before the tone

    tone_type = reaction_data.loc[trial_num, 'Tone']
    if tone_type == 1:
        pygame.mixer.Sound.play(in_tune_tone)
    else:
        pygame.mixer.Sound.play(out_of_tune_tone)

    t0 = time.time()  # Start reaction timer

    reaction_data.loc[trial_num, 'tGap'] = round(gap * 1000, 0)  # Store gap

    waiting_for_response = True
    while waiting_for_response:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:  # M key for "in-tune"
                    reaction_data.loc[trial_num, 'Key'] = 'M'
                    reaction_data.loc[trial_num, 'RT'] = round((time.time() - t0) * 1000, 0)
                    waiting_for_response = False
                elif event.key == pygame.K_c:  # C key for "out-of-tune"
                    reaction_data.loc[trial_num, 'Key'] = 'C'
                    reaction_data.loc[trial_num, 'RT'] = round((time.time() - t0) * 1000, 0)
                    waiting_for_response = False

    trial_num += 1
    reaction_data.to_csv("pilot1_4data.csv", index=False)  # Save progress

pygame.quit()
sys.exit()  # Ensure script fully exits
