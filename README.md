# Stockpiler
A Foxhole logi companion app for quickly reading and transcribing stockpile contents

Stockpiler aims to simplify tracking the contents of stockpiles by automating the process and exporting a spreadsheet with the stockpile's contents.

Constructive criticism is welcome, but keep in mind **I DO NOT CODE FOR A LIVING**.  Thanks. :)

Current Features:
- Hotkey (F3) to read and transcribe contents of any stockpile/BB/Town Base/etc from the Map.
- Hotkey (F2) to screenshot a stockpile without reading it
- Results tab displaying a spreadsheet of the results, from which you can copy to paste elsewhere
- Learning mode for creating a custom icon set for those that use Mods
- App is threaded, so you can initiate a new scan while previous scan(s) are still processing.
- Most items can be read, other than those with missing icons as noted in Missing.csv
- Ability to set a filter to ignore unwanted items
- Toggles to turn on/off faction-specific items and entire categories of items in filter
- Filter can be saved and is automatically loaded at launch
- Choose which exports you want, save this setting and it will load automatically in the future

# To use:
1. Launch Foxhole and Deploy
2. Launch Stockpiler
3. If you're using modded icons, set your icon set to Modded in the upper left and make sure Learning Mode is checked
4. Open your Map
5. Hover your cursor over the Stockpile/Bunker Base/Town Hall/etc you wish to transcribe **on the map**
- Remember you can tab while hovering over a Seaport/Storage Depot where you have multiple private stockpiles
6. Press the **F3** key

If you are using modded icons and have Learning Mode on, you will get a series of popups where you are asked to identify each new icon it finds.  It will remember your choices, so over time you will build your set.  Once it has run through all new icons with you, it will export the results as normal.

If the stockpile is a named stockpile that Stockpiler has never seen before:
- Stockpiler will display an image of the stockpile name and ask you to enter the name
- The stockpile's contents will be exported to ../Stockpiles folder as:
- XLSX (Excel Spreadsheet) of the contents
- CSV TXT file of contents
- Image of the stockpile title
- A copy of the stockpile image grabbed by Stockpiler

If the stockpile is a named stockpile that Stockpile has seen before:
- Stockpiler will overwrite any existing (previous) export of the stockpile contents as:
- XLSX (Excel Spreadsheet) of the contents
- CSV TXT file of contents
- A copy of the stockpile image grabbed by Stockpiler


Stockpiler runs each stockpile "grab" as a separate thread, so you do not have to wait for one to complete before initiating the next


Currently, pressing the F2 key will grab an image of the stockpile/BB/Relic Base contents you are hovering over and save it to the root folder.  If you are willing to help contribute missing items so that Stockpiler can properly tally them, these are the images that are needed.  Please message me on Discord if you're interested in helping get the remaining missing item images added.
My Discord is ruttiger#6198

Special thanks to **Catalinuru**, **AceAstra** and **Drougavis** for their help testing and hunting down missing icons.

Compiled versions compiled to EXE using Nuitka

Nuitka was a giant pain in the butt to get working the first time around and I honestly don't remember all the steps I took to get it to where I have it now.  If you're able to work your way through that, you can use either compile string below.

Compile string (without console window) is:
python -m nuitka --mingw64 --plugin-enable=tk-inter --plugin-enable=numpy --standalone --windows-disable-console --follow-imports --show-progress Stockpiler.py

Compile string (with console window):
python -m nuitka --mingw64 --plugin-enable=tk-inter --plugin-enable=numpy --standalone --follow-imports --show-progress Stockpiler.py


Code can also be compiled (more easily) with auto-py-to-exe

auto-py-to-exe settings:

Onefile - One Directory

Console Window - Console Based (helpful for troubleshooting, please submit any errors you get as Issues here on GitHub)

Additional Files - Add Folder - add the CheckImages, Stockpiles and UI folders

Additional Files - Add Files - add the Filter.csv and ItemNumbering.csv files

Advanced - collect-all - pynput
