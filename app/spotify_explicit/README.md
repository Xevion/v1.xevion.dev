# spotify-explicit

## About

The purpose of this repository/project is to capture my liked songs from my Spotify account, and then create a stacked bar graph representing my explicit vs "clean" songs.

Yes, the project is super simple and doesn't have that much usefulness, but it's the first time I've genuinely used `matplotlib` or `logger` in a serious context and it was definitely interesting.

## Demonstration

![Output Matplotlib Stacked Bar-graph](./graph.png)

---

```css
> python main.py
INFO:root:Pulling data from Spotify
INFO:root:Authorizing with Spotify via Spotipy
WARNING:root:May require User Interaction to authenticate properly!
INFO:root:Authorized with Spotify via Spotipy
WARNING:root:Clearing all files in tracks folder for new files
INFO:root:Cleared folder, ready to download new track files
INFO:root:Requesting 0 to 50
INFO:root:Received 0 to 50
INFO:root:Saved at "\tracks\saved-tracks-0-50.json" (150K)
INFO:root:Requesting 50 to 100
INFO:root:Received 50 to 100
INFO:root:Saved at "\tracks\saved-tracks-50-100.json" (151K)
INFO:root:Requesting 100 to 150
INFO:root:Received 100 to 150
INFO:root:Saved at "\tracks\saved-tracks-100-150.json" (146K)
INFO:root:Requesting 150 to 200
INFO:root:Received 150 to 200
INFO:root:Saved at "\tracks\saved-tracks-150-200.json" (147K)
INFO:root:Requesting 200 to 250
INFO:root:Received 200 to 250
INFO:root:Saved at "\tracks\saved-tracks-200-250.json" (146K)
INFO:root:Requesting 250 to 300
INFO:root:Received 250 to 300
INFO:root:Saved at "\tracks\saved-tracks-250-300.json" (137K)
INFO:root:Requesting 300 to 350
INFO:root:Received 300 to 350
INFO:root:Saved at "\tracks\saved-tracks-300-350.json" (140K)
INFO:root:Requesting 350 to 400
INFO:root:Received 350 to 400
INFO:root:Saved at "\tracks\saved-tracks-350-400.json" (149K)
INFO:root:Requesting 400 to 450
INFO:root:Received 400 to 450
INFO:root:Saved at "\tracks\saved-tracks-400-450.json" (140K)
INFO:root:Requesting 450 to 500
INFO:root:Received 450 to 500
INFO:root:Saved at "\tracks\saved-tracks-450-500.json" (149K)
INFO:root:Requesting 500 to 550
INFO:root:Received 500 to 550
INFO:root:Saved at "\tracks\saved-tracks-500-550.json" (137K)
INFO:root:Requesting 550 to 600
INFO:root:Received 550 to 600
INFO:root:Saved at "\tracks\saved-tracks-550-600.json" (137K)
INFO:root:Requesting 600 to 650
INFO:root:Received 600 to 650
INFO:root:Saved at "\tracks\saved-tracks-600-650.json" (135K)
INFO:root:Requesting 650 to 700
INFO:root:Received 650 to 700
INFO:root:Saved at "\tracks\saved-tracks-650-700.json" (140K)
INFO:root:Requesting 700 to 750
INFO:root:Received 700 to 750
INFO:root:Saved at "\tracks\saved-tracks-700-750.json" (134K)
INFO:root:Requesting 750 to 800
INFO:root:Received 750 to 800
INFO:root:Saved at "\tracks\saved-tracks-750-800.json" (137K)
INFO:root:Requesting 800 to 850
INFO:root:Received 800 to 850
INFO:root:Saved at "\tracks\saved-tracks-800-850.json" (132K)
INFO:root:Requesting 850 to 900
INFO:root:Received 850 to 900
INFO:root:Saved at "\tracks\saved-tracks-850-900.json" (143K)
INFO:root:Requesting 900 to 950
INFO:root:Received 900 to 919
INFO:root:Saved at "\tracks\saved-tracks-900-919.json" (55K)
INFO:root:Requested and saved 919 tracks split over 19 files (2 MB)
INFO:root:Reading track files
INFO:root:Read and parse 19 track files
INFO:root:Combining into single track file for ease of access
INFO:root:File combined with 919 items
INFO:root:Processing file...
INFO:root:Processed data, creating plot from data
INFO:root:Saving the figure to the 'export' folder
INFO:root:Showing plot to User
>
```

# Requirements

The requirements for this project are outlined in the [requirements.txt](requirements.txt) file.

You can use the `pip` tool to instantly download and install all required modules via `pip install -r requirements.txt`.

## License

This project uses the GNU General Public License, see the [LICENSE](./LICENSE) file for more information.