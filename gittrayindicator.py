import os
import subprocess
import json
import gi
import pathlib as pl

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
from gi.repository import AppIndicator3, Gtk, GLib

# Define icons for different states
# ICON_CLEAN = "/usr/share/icons/gnome/16x16/status/weather-clear.png"
# ICON_DIRTY = "/usr/share/icons/gnome/16x16/status/error.png"
# ICON_STALE = "/usr/share/icons/gnome/16x16/status/dialog-warning.png"
# Load repositories from config file
CONFIG_FILE = os.path.expanduser("~/.git_tray_config.json")

def find_icon(icon_list):
    for p2f in icon_list:
        if pl.Path(p2f).is_file():
            return p2f
    icon_list_j = '\n'.join(icon_list)
    assert(False), f'Icon not found. None of the path options below exist\n{icon_list_j}'
        


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("repositories", [])
    return []

REPOS = load_config()

class GitTrayMonitor:
    def __init__(self):
        self.icon_clean = find_icon(["/usr/share/icons/gnome/16x16/status/weather-clear.png",
                                     "/usr/share/icons/Adwaita/16x16/legacy/face-laugh.png"])
        self.icon_dirty = find_icon(["/usr/share/icons/gnome/16x16/status/error.png",
                                     "/usr/share/icons/Adwaita/16x16/legacy/dialog-error.png"])
        self.icon_stale = find_icon(["/usr/share/icons/gnome/16x16/status/dialog-warning.png",
                                     "/usr/share/icons/Adwaita/16x16/legacy/dialog-warning.png"])
        
        #/usr/share/icons/Adwaita/16x16/legacy
        
        self.indicator = AppIndicator3.Indicator.new(
                            "git_status_indicator",
                            self.icon_clean,
                            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
                        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        self.log_messages = []
        
        # Create a menu
        self.menu = Gtk.Menu()
        
        update_item = Gtk.MenuItem(label="Refresh")
        update_item.connect("activate", self.update_status)
        self.menu.append(update_item)
        
        config_item = Gtk.MenuItem(label="Edit Config File")
        config_item.connect("activate", self.open_config_editor)
        self.menu.append(config_item)
        
        log_item = Gtk.MenuItem(label="Log / Messages")
        log_item.connect("activate", self.show_log)
        self.menu.append(log_item)
        
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit)
        self.menu.append(quit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        

        
        # Start monitoring
        self.update_status()
    


    def check_git_status(self, repo):
        repo_path = os.path.expanduser(repo)
        if not os.path.exists(repo_path):
            self.log_messages.append(f"Checked {repo}: repo not found")
            return 'Dirty'
            
        
        # Check for uncommitted changes
        status_output = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True
        )
        has_changes = bool(status_output.stdout.strip())
        
        # Check for unpushed commits
        cherry_output = subprocess.run(
            ["git", "cherry", "-v"], cwd=repo_path, capture_output=True, text=True
        )
        has_unpushed = bool(cherry_output.stdout.strip())
        
        # Check for unpulled commits (remote changes)
        subprocess.run(["git", "fetch"], cwd=repo_path, capture_output=True, text=True)
        remote_changes_output = subprocess.run(
            ["git", "rev-list", "--left-right", "@{upstream}...HEAD"], cwd=repo_path, capture_output=True, text=True
        )
        has_unpulled = bool(remote_changes_output.stdout.strip())
        
        if has_changes:
            status = 'Dirty'
        elif has_unpushed:
            status = 'Dirty'
        elif has_unpulled:
            status = 'Stale'
        else:
            status = 'Clean'
        
        self.log_messages.append(f"Checked {repo}: {status}")
        
        return status
    
    def update_status(self, event = None):
        self.log_messages.append('============')
        self.log_messages.append('Refresh')
        self.log_messages.append('------------')
        statuses = [self.check_git_status(repo) for repo in REPOS]
        
        if 'Dirty' in statuses:
            icon = self.icon_dirty #ICON_DIRTY
        elif 'Stale' in statuses:
            icon = self.icon_stale
        else:
            icon = self.icon_clean #ICON_CLEAN
        # Update the tray icon based on repo status
        # self.indicator.set_icon(ICON_DIRTY if dirty else ICON_CLEAN)
        self.indicator.set_icon_full(icon, "Git Status")
        self.log_messages.append('------------')
        # Schedule next check
        GLib.timeout_add_seconds(600, self.update_status)
        return False
    
    def show_log(self, _):
        dialog = Gtk.Dialog(title="Git Status Log", 
                            modal=True,
                            destroy_with_parent=True,
                            # flags=Gtk.DialogFlags.MODAL,
                            )
        dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_buffer = text_view.get_buffer()
        text_buffer.set_text("\n".join(self.log_messages))
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(text_view)
        scroll.set_min_content_height(300)
        scroll.set_min_content_width(400)
        
        content_area = dialog.get_content_area()
        content_area.add(scroll)
        dialog.show_all()
        
        dialog.run()
        dialog.destroy()
    
    def open_config_editor(self, _):
        dialog = Gtk.Dialog(title="Edit Config File",
                            modal=True,
                            destroy_with_parent=True,
                            # flags=Gtk.DialogFlags.MODAL,
                            )
        dialog.add_buttons(Gtk.STOCK_SAVE, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        
        text_view = Gtk.TextView()
        text_buffer = text_view.get_buffer()
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                text_buffer.set_text(f.read())
        
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        text_view.set_editable(True)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(text_view)
        scroll.set_min_content_height(300)
        scroll.set_min_content_width(400)
        
        content_area = dialog.get_content_area()
        content_area.add(scroll)
        dialog.show_all()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            start_iter, end_iter = text_buffer.get_bounds()
            with open(CONFIG_FILE, "w") as f:
                f.write(text_buffer.get_text(start_iter, end_iter, True))
            global REPOS
            REPOS = load_config()
            self.update_status()
        
        dialog.destroy()
    
    def quit(self, _):
        Gtk.main_quit()

if __name__ == "__main__":
    if not REPOS:
        print("No repositories configured. Please add repositories to ~/.git_tray_config.json")
    app = GitTrayMonitor()
    Gtk.main()
