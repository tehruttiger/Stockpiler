# Stockpiler
A Foxhole logi companion app for quickly reading and transcribing stockpile contents

Stockpiler aims to simplify tracking the contents of stockpiles by automating the process and exporting a spreadsheet with the stockpile's contents.

Current (arbitrary) version is .6b

# To use:
Launch Foxhole and Deploy
Launch Stockpiler
Open your Map
Hover your cursor over the Stockpile/Bunker Base/Town Hall/etc you wish to transcribe **on the map**
- Remember you can tab while hovering over a Seaport/Storage Depot where you have multiple private stockpiles
Press the **F3** key
- If the stockpile is a named stockpile that Stockpiler has never seen before:
-   Stockpiler will display an image of the stockpile name and ask you to enter the name
-   The stockpile's contents will be exported to ../Stockpiles folder as:
-     CSV TXT file of contents
-     Image of the stockpile title
-     A copy of the stockpile image grabbed by Stockpiler
- If the stockpile is a named stockpile that Stockpile has seen before:
-   Stockpiler will overwrite any existing (previous) export of the stockpile contents as:
-    CSV TXT file of contents
-    A copy of the stockpile image grabbed by Stockpiler


Stockpiler runs each stockpile "grab" as a separate thread, so you do not have to wait for one to complete before initiating the next


Currently, pressing the F2 key will grab an image of the stockpile/BB/Relic Base contents you are hovering over and


Compiled versions compiled to EXE using Nuitka

Compile string (without console window) is:
python -m nuitka --mingw64 --plugin-enable=tk-inter --plugin-enable=numpy --standalone --windows-disable-console --follow-imports --show-progress Stockpiler.py

Compile string (with console window):
python -m nuitka --mingw64 --plugin-enable=tk-inter --plugin-enable=numpy --standalone --follow-imports --show-progress Stockpiler.py
