Requires PyQt6.

Download and run dlssg_sm86_proton_installer.py

GUI installer that automates the process seen in README_original.md. 

Downloads the needed files from tb0ne's and sdli1995's repos

You can select any installed Steam game / non-steam game added to steam that support DLSS FG with a proton prefix. 

After pressing apply, select the game's exe (it doesn't change it, just adds version.dll and dlssg_sm86.ini), the program change's proton's version.dll within the prefix.

Then copy the command and add it to the game's steam properties. The command is for proton-cachyos specifically, I don't know what other Proton versions it will work.


Issues:
On some occasions, it looks like the program replaced the cached downloaded files by empty ones. Since it changes Proton's version.dll, your game will no longer launch (it will briefly launch a small window that says "Installing Game-Specific fixes, please wait").
If that happens, update the cache (make sure you are connected to the internet) and run it again. 
Maybe I'll add an option to restore the prefix's original version.dll later if I feel like it. Probably won't.
