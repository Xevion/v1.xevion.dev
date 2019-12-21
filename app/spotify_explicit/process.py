import os
import sys
import json
import logging
import datetime
import collections
import numpy as np
import dateutil.parser
import PIL.Image as Image
import matplotlib.pyplot as plt

# Gets all files in tracks folder, returns them in parsed JSON
def get_files():
    folder = os.path.join(sys.path[0], 'tracks')
    files = []
    for file in os.listdir(folder):
        with open(os.path.join(os.path.join(folder, file))) as file:
            files.append(
                json.load(file)
            )
    return files

# Simple function to combine a bunch of items from different files
def combine_files(files):
    items = []
    for file in files:
        items.extend(file['items'])
    return items

# Prints the data in a interesting format
def print_data(data):
    for i, item in enumerate(data):
        date = dateutil.parser.parse(item['added_at'])
        explicit = '!' if item['track']['explicit'] else ' '
        track_name = item['track']['name']
        artists = ' & '.join(artist['name'] for artist in item['track']['artists'])
        print('[{}] {} "{}" by {}'.format(date, explicit, track_name, artists))

def process_data(data):
    # Process the data by Month/Year, then by Clean/Explicit
    scores = {}
    for item in data:
        date = dateutil.parser.parse(item['added_at']).strftime('%b %Y')
        if date not in scores.keys():
            scores[date] = [0, 0]
        scores[date][1 if item['track']['explicit'] else 0] += 1
    
    # Create simplified arrays for each piece of data
    months = list(scores.keys())[::-1]
    clean, explicit = [], []
    for item in list(scores.values())[::-1]:
        clean.append(item[0])
        explicit.append(item[1])

    # Done processing date properly, start plotting work
    logging.info('Processed data, creating plot from data')
    # Weird numpy stuff
    n = len(scores.values())
    ind = np.arange(n)
    width = 0.55
    # Resizer figuresize to be 2.0 wider
    plt.figure(figsize=(10.0, 6.0))    
    # Stacked Bars
    p1 = plt.bar(ind, explicit, width)
    p2 = plt.bar(ind, clean, width, bottom=explicit) # bottom= just has the bar sit on top of the explicit
    # Plot labeling
    plt.title('Song Count by Clean/Explicit')
    plt.ylabel('Song Count')
    plt.xlabel('Month')
    plt.xticks(ind, months, rotation=270) # Rotation 90 will have the 
    plt.legend((p1[0], p2[0]), ('Explicit', 'Clean'))
    fig = plt.gcf() # Magic to save to image and then show

    # Save the figure, overwriting anything in your way
    logging.info('Saving the figure to the \'export\' folder')
    export_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'export')
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
    plt.tight_layout()
    fig.savefig(
        os.path.join(
            export_folder,
            'export'
            # datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        ),
        dpi=100,
        quality=95
    )
    
    # Finally show the figure to 
    logging.info('Showing plot to User')
    # plt.show()

    # Copy the figure to your clipboard to paste in Excel
    # logging.info('Copying the plot data to clipboard')
    # copy(months, clean, explicit)

# Simple method for exporting data to a table like format
# Will paste into Excel very easily
def copy(months, clean, explicit):
    from pyperclip import copy
    top = 'Period\tClean\tExplicit\n'
    copy(top + '\n'.join([
        f'{item[0]}\t{item[1]}\t{item[2]}' for item in zip(months, clean, explicit)
    ]))

def main():
    # logging.basicConfig(level=logging.INFO)
    logging.info("Reading track files")
    files = get_files()
    logging.info(f"Read and parse {len(files)} track files")
    logging.info("Combining into single track file for ease of access")
    data = combine_files(files)
    data.sort(key=lambda item : dateutil.parser.parse(item['added_at']).timestamp(), reverse=True)
    logging.info(f'File combined with {len(data)} items')
    logging.info('Processing file...')
    process_data(data)