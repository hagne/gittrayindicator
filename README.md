# gittrayindicator
Never forget to push your repos ever again.

# Installation
## Dependencies

- AppIndicator3
- python3-gi
- GTK (probaly installed)

## Deb system
sudo apt install gir1.2-appindicator3-0.1 python3-gi

## Red Hat

1) sudo dnf install gnome-shell-extension-appindicator libappindicator-gtk3 python3-gobject
2) Restart gnome, e.g. log out and backin
3) gnome-extensions enable appindicatorsupport@rgcjonas.gmail.com


# Usage

## Create configuration file
Create a configuration file at 
```
~/.git_tray_config.json
```
witch list the repositories that should be checked:
```
{
    "repositories": [
        "~/projects/myrepo1",
        "~/projects/myrepo2"
    ]
}
```

## Run script
python3 /path/to/repo/gittrayindicator.py

# Run on startup

## Deb system
add python3 /path/to/repo/gittrayindicator.py to startup applications

## Red Hat
1) Create gittrayindicator.desktop file in 
```
~/.local/share/applications/
```
example file content:
```
[Desktop Entry]
Type=Application
Exec=python3 /home/grad/htelg/prog_dev/gittrayindicator/gittrayindicator.py
Name=gittrayindicator
Icon=utilities-terminal
Terminal=false
Categories=Utility;
```

2) Update GNOME’s application cache:

```
update-desktop-database ~/.local/share/applications/
```
Now you are able to launch the script e.g. via the super key.

3) Use gnome-tweak to add program to the list of startup applications


# Todo
* notify if error in config file after change
