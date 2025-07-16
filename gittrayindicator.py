#!/usr/bin/env python3

import os
import subprocess
import json
import gi
import pathlib as pl
import datetime
import webbrowser
import shutil


gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
from gi.repository import AppIndicator3, Gtk, GLib

# Define icons for different states
# ICON_CLEAN = "/usr/share/icons/gnome/16x16/status/weather-clear.png"
# ICON_DIRTY = "/usr/share/icons/gnome/16x16/status/error.png"
# ICON_STALE = "/usr/share/icons/gnome/16x16/status/dialog-warning.png"
# Load repositories from config file
CONFIG_FILE = os.path.expanduser("~/.git_tray_config.json")


def determine_terminal():
    terminal = 'xtermemul'
    if shutil.which("x-terminal-emulator") is None:
        terminal = 'gnometerm'
    
    return terminal

terminal = determine_terminal()

def find_icon(icon_list):
    for p2f in icon_list:
        if pl.Path(p2f).is_file():
            return p2f
    icon_list_j = '\n'.join(icon_list)
    assert(False), f'Icon not found. None of the path options below exist\n{icon_list_j}'
        




# REPOS = load_config()
class GitTrayMonitor:
    def __init__(self):
        self.verbose = True
        self.icon_clean = find_icon(["/usr/share/icons/gnome/16x16/status/weather-clear.png",
                                     "/usr/share/icons/Adwaita/16x16/legacy/face-laugh.png"])
        self.icon_dirty = find_icon(["/usr/share/icons/gnome/16x16/status/error.png",
                                     "/usr/share/icons/Adwaita/16x16/legacy/dialog-error.png"])
        self.icon_stale = find_icon(["/usr/share/icons/gnome/16x16/status/dialog-warning.png",
                                     "/usr/share/icons/Adwaita/16x16/legacy/dialog-warning.png"])
        self.log_messages = []
        
        self.repos = self.load_config()
        #/usr/share/icons/Adwaita/16x16/legacy
        
        self.indicator = AppIndicator3.Indicator.new(
                            "git_status_indicator",
                            self.icon_clean,
                            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
                        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        

        # Create a menu
        self.menu = Gtk.Menu()
        
        app_name_item = Gtk.MenuItem(label="Git Tray Indicator")
        app_name_item.set_sensitive(False)
        self.menu.append(app_name_item)
        
        separator = Gtk.SeparatorMenuItem()
        self.menu.append(separator)
        
        update_item = Gtk.MenuItem(label="Refresh")
        update_item.connect("activate", self.update_status)
        self.menu.append(update_item)
                
        dirty_repos_item = Gtk.MenuItem(label="Dirty Repos")
        dirty_repos_item.connect("activate", self.show_changed_repos, 'Dirty')
        self.menu.append(dirty_repos_item)
        
        stale_repos_item = Gtk.MenuItem(label="Stale Repos")
        stale_repos_item.connect("activate", self.show_changed_repos, 'Stale')
        self.menu.append(stale_repos_item)
        
        separator = Gtk.SeparatorMenuItem()
        self.menu.append(separator)
        
        config_item = Gtk.MenuItem(label="Edit Config File")
        config_item.connect("activate", self.open_config_editor)
        self.menu.append(config_item)
        
        log_item = Gtk.MenuItem(label="Log / Messages")
        log_item.connect("activate", self.show_log)
        self.menu.append(log_item)

        
        separator2 = Gtk.SeparatorMenuItem()
        self.menu.append(separator2)
        
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit)
        self.menu.append(quit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        

        
        # Start monitoring
        self.update_status()

    def quick_git_commit(self,_, commit_message="quick commit"):
        for repo, status in self.repos_stati.items():
            if status == 'Dirty':
                try:
                    # Step 1: Change to the target directory
                    repo_path = os.path.expanduser(repo)
                    os.chdir(repo_path)
            
                    # Step 2–4: Run git commands
                    subprocess.run(["git", "add", "."], check=True)
                    subprocess.run(["git", "commit", "-m", commit_message], check=True)
                    subprocess.run(["git", "push"], check=True)
                    env=dict(os.environ, GIT_ASKPASS='true', SSH_ASKPASS='true')
                    print('tp_130')
                    self.update_status(which = repo)
                    print(f'quick commit and pushed {repo}')
                except Exception as e:
                    dialog = Gtk.Dialog(title=f"repo {repo} return error:\n{e}", 
                                        modal=True,
                                        )
                    dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        return
    
    def pull_all(self,_, commit_message="quick commit"):
        for repo, status in self.repos_stati.items():
            if status == 'Stale':
                try:
                    # Step 1: Change to the target directory
                    repo_path = os.path.expanduser(repo)
                    os.chdir(repo_path)
            
                    # Step 2–4: Run git commands
                    subprocess.run(["git", "pull", "."], check=True)
                    self.update_status(which = repo)
                    print(f'pulled {repo}')
                except Exception as e:
                    dialog = Gtk.Dialog(title=f"repo {repo} return error:\n{e}", 
                                        modal=True,
                                        )
                    dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        return
        
        
    def open_repo(self,_,repo, dialog, how2open = 'terminal'):
        
        if how2open == 'jupyter':
            link = repo.replace('~', 'http://localhost:8888/lab/tree')
            webbrowser.open(link)
            
        elif how2open == 'terminal':
            
            # Define the path where the terminal should open
            working_directory = os.path.expanduser(repo)
            
            # Open the terminal in the specified directory and run the command
            # p = subprocess.Popen(["gnome-terminal", "--working-directory", working_directory, "--", "bash", "-c", command])
            if terminal == 'xtermemul':
                p = subprocess.Popen(["x-terminal-emulator", "-e", f"bash -c 'cd {working_directory}; git status; exec bash --noprofile --norc -i'"])
            else:
                p = subprocess.Popen(["gnome-terminal", "--working-directory", working_directory])
            p.wait()
            
            self.update_status(which = repo)
            
        else:
            raise ValueError(f'{how2open} is not a valid option for how2open.')
            
        dialog.destroy()
            
        return
        
    def show_changed_repos(self, _, test):
        dialog = Gtk.Dialog(title="Changed Repositories", 
                            modal=True,
                            )
        dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dialog.get_content_area()

        # for status,repo in zip(self.repos_stati,self.repos):
        for repo, status in self.repos_stati.items():
            if status == test:
                repo_item = Gtk.Button(label=repo)
                repo_item.connect("clicked", self.open_repo, repo, dialog)
                box.add(repo_item)
        if test == 'Dirty':
            print('s1')
            repo_item = Gtk.Button(label='quick commit and push')
            repo_item.connect("clicked", self.quick_git_commit)
            box.add(repo_item)
        if test == 'Stale':
            print('s2')
            repo_item = Gtk.Button(label='pull all')
            repo_item.connect("clicked", self.pul, repo, dialog)
            box.add(repo_item)
        repo_item.connect("clicked", self.open_repo, repo, dialog)
        dialog.show_all()      
        dialog.run()
        dialog.destroy()
        
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f).get("repositories", [])
            except Exception as e:
                self.log_messages.append(f'Error when parsing configuration file: {str(e)}')
                return []
                
        else:
            self.log_messages.append("No repositories configured. Please add repositories to ~/.git_tray_config.json")
            return []

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
        
        message = f"Checked {repo}: {status}"
        self.log_messages.append(message)
        if self.verbose:
            print(message)
        
        return status
    
    def update_status(self, event = None, which = 'all'):
        if self.verbose:
            print('update_status')
        self.log_messages.append('============')
        self.log_messages.append(f'Refresh -- {datetime.datetime.now()}')
        self.log_messages.append('------------')
        if which == 'all':
            self.repos_stati = {repo: self.check_git_status(repo) for repo in self.repos}
        else:
            if which not in self.repos_stati.keys():
                raise KeyError(f'{which} not a ins repos_stati.\n {self.repo_stati}')
            else:
                self.repos_stati[which] = self.check_git_status(which)
        
        statuses = self.repos_stati.values()
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
        max_len = 20
        if len(self.log_messages) > max_len:
            self.log_messages = self.log_messages[-max_len:]
            
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
            self.repos = self.load_config()
            self.update_status()
        
        dialog.destroy()
    
    def quit(self, _):
        Gtk.main_quit()

if __name__ == "__main__":        
    app = GitTrayMonitor()
    Gtk.main()
