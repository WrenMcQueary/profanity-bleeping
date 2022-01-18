# profanity-bleeping
Sometimes you may find a wonderful educational resource that is woefully expletive-ridden.  This program automatically bleeps chosen words from audio, making an educational resource more presentable to students in certain age ranges.

Uses Google Cloud API to bleep out a chosen list of words from an audio sample.

Big shoutout to [Soham Sil](https://github.com/sohamsil).  This code borrows heavily from their method.

## Requirements
1. Set up a Google Cloud API account and gain a license (in .json form) to use Google Cloud Speech.
2. Create identical copies of the same audio: one as a .flac, one as a .wav.  Make sure their names line up wtih lines 93 and 94 of main.py.
3. Run!

## Install dependencies
wave  
struct  
numpy  
tqdm  
google.cloud  
io  
google.oauth2
