# gittrayindicator
Never forget to push your repos ever again.

# Dependencies

- AppIndicator3
- python3-gi
- GTK (probaly installed)

sudo apt install gir1.2-appindicator3-0.1 python3-gi

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
add python3 /path/to/repo/gittrayindicator.py to startup applications

# Todo
* notify if error in config file after change
