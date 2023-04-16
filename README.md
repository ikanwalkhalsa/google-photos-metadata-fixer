# Google-Photos-Metadata-Fixer (Free)
This project is a replica of Google Photo Metadata Fixer, a tool that helps users to fix their photo metadata. The tool allows users to bulk modify their photos’ date and time properties.

This replica is written in Python. The tool provides a command-line interface (CLI) that just requires the location of zip files and handle the rest from there.

Features:
* Modify photos’ date and time in bulk.
* Provide a CLI for easy interaction with the tool.
* Handle errors and exceptions gracefully to ensure smooth execution.

Installation:
To use the script, you just need Python installed on your system. And then follow the given steps.
* Download the script 'google_photos_metadata_fixer.py' on your system
* run 'python google_photos_metadata_fixer.py "PATH OF FOLDER CONTAINTING ZIP FILES"'

Note:
Here are a few things that can help you in the process
* Make sure your zip files follow the same naming convention as google (takeout-*.zip)
* Source Folder Location can be modified on line 9
* Output Folder Location can be modified on line 10

How it Works:
* Scans all the takeout zips in the given folder
* Unzip the files in the same folder location
* Merges folders from different zips into a single intermediate Folder
* Looks and pairs JSON metadata for all file types
* Moves all files to output destination and updates the metadata
* If no JSON found for the file the file will be moved to /FAILED dir

Sample Output:
Fixing Google Takeout MetaData :  /Users/beast/Downloads
Found 7 zip files, Unzipping...
         |||||||||||||||||||||||||||||||||||||||||||||||||| (7/7)
Creating Intermediate Locations...
         |||||||||||||||||||||||||||||||||||||||||||||||||| (62/62)
Moving Files to Intermediate Location...
         |||||||||||||||||||||||||||||||||||||||||||||||||| (19606/19606)
Creating File Pairs...
         |||||||||||||||||||||||||||||||||||||||||||||||||| (20/20)
Merging Files with metadata...
         |||||||||||||||||||||||||||||||||||||||||||||||||| (9266/9277)

Moving Remaining Files to  /Users/beast/Downloads/Output-20230417T010529/FAILED
         |||||||||||||||||||||||||||||||||||||||||||||||||| (983/983)
Cleaning Directories...
         |||||||||||||||||||||||||||||||||||||||||||||||||| (8/8)

All Files (MetaData+File) :  19547
JSON Files                :  9287
Files with MetaData       :  9277
Files without MetaData    :  983
Finished! Files saved in the following location
/Users/beast/Downloads/Output-20230417T010529

Thank you for checking out this project. I hope it helps you fix your photo metadata and saves you time and effort!
