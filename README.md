# Facebook Messenger Statistics
This is a Python script that generates statistics about your Facebook Messenger usage.
Project is forked from [simonwongwong/Facebook-Messenger-Statistics](https://github.com/simonwongwong/Facebook-Messenger-Statistics) and modified to work with Czech language.

Have you downloaded your Facebook data? Are you curious/concerned about your Messenger usage?
Discover fun stats about your Facebook Messenger usage such as: most used words, most active year, most active hours, etc.

Plots can be created using a Jupyter Notebook for exploratory analysis or a basic HTML report can be generated using the `generate_report.py` script.

![demo](pictures/demo.gif)

For **instructions** [scroll down](#how-to-use)

# Example Report
An interactive sample report can be found on previous author's [website](https://simonwong.io/sample_report.html)
![report](pictures/screenshot.png)

# How to use
## Download your Messenger data from Facebook
Download your Facebook Messenger data [in your settings page](https://www.facebook.com/settings)
![facebook settings](pictures/download.png)

Make sure to download in **JSON format**. Media quality can be set to low for a faster download
![download](pictures/download_page.PNG)
## Clone this repository
Clone this repo using:
```
git clone https://github.com/JakubAndrysek/Facebook-Messenger-Statistics.git
```
Or download the zip file and extract it.


## Install Python and Python libraries

1. If you don't have Python, install Python 3.7+
2. Open a console on the project directory (or create your own custom environment) and run:
```
pip install -r "requirements.txt"
```

## Generate an HTML report
Run the `generate_report_***.py` script either using your terminal or double-click the file on Windows

Choose one of the following options (using the console):
- Input string path to message directory
- Open Tkinter file dialog to select message directory
- Use default path (./messages/inbox)

If you choose to Open Tkinter file dialog, you should see a file dialog similar to this:

Locate your `inbox` folder from your extracted Facebook data using the file dialog. This folder should contain more folders for each chat and each of those folders should contain a `message_1.json` file.
![filedialog](pictures/file_dialog.png)

If it runs successfully, you should receive a message similar to:
```
Parsing data from C:/Users/Simon/Desktop/messages/inbox
Report generated successfully!
```
And an HTML report should be at your current working directory.

## Exploratory analysis on Jupyter (Not tested)
Open a console in the folder and start Jupyter Notebook using `jupyter notebook` command.
From the Notebook file tree, open the Statistics notebook `Statistics.ipynb`

![notebook](pictures/notebook.png)

Make sure the correct directory is passed into `loader.parse_from_json()` and then have fun!

See `chatstat.py` or docstrings for parameters you can play with in the plot generators.
