#!/usr/bin/env python3
import sys
import os
import re
import urllib.request
import pathlib
import binascii
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTextEdit, QProgressBar, QMessageBox, 
    QGroupBox, QFileDialog, QCheckBox
)

# URLs des dépôts et dossier de cache local
CACHE_DIR = pathlib.Path.home() / ".local" / "share" / "dlssg-installer"

# Dictionnaire des textes bilingues
TRANSLATIONS = {
    "en": {
        "window_title": "Frame Generation Mod Installer (Proton)",
        "header": "Frame Generation Installation Assistant (dlssg_for_sm86)",
        "lang_btn": "Français",
        "group_game": "Game Selection (Steam & Non-Steam)",
        "games_detected": "Detected games:",
        "show_all": "Show all games (including non-DLSS-G compatible and tools)",
        "game_path": "Game folder: None",
        "game_path_prefix": "Game folder: ",
        "group_env": "Required Steam Configuration",
        "env_label": "Environment variables to add in Steam launch options (proton-cachyos):",
        "copy_btn": "Copy",
        "group_logs": "Execution Log",
        "update_cache_btn": "Update Cache",
        "apply_btn": "Apply Mod",
        "copied_title": "Copied",
        "copied_msg": "Environment variable copied to clipboard!",
        "cache_success_title": "Success",
        "cache_success_msg": "Cache successfully cleared and updated!",
        "cache_error_title": "Error",
        "cache_error_msg": "Failed to update cache:\n",
        "install_success_msg": "The mod was successfully installed on the selected game!",
        "install_error_msg": "An error occurred:\n",
        "cancel_install": "Installation cancelled: no executable selected.",
        "select_exe": "Select executable (.exe) for: ",
        "exe_filter": "Windows Executables (*.exe);All Files (*)",
        "scan_start": "Global search for Steam and Non-Steam games...",
        "steam_found": "Steam folder found: ",
        "steam_error": "ERROR: Could not locate Steam folder.",
        "unsupported": "[No DLSS-G]",
        "display_count": "Displaying {count} game(s) in the list (Filter active: {filter}).",
        "cache_clearing": "=== Clearing and updating local cache ===",
        "deleting_old": "Deleting old file: ",
        "downloading": "Downloading ",
        "cache_updated": "=== Cache updated successfully! ===",
        "cache_update_ok": "Cache updated.",
        "install_start": "=== Starting mod installation ===",
        "missing_cache": "Missing file in cache ({name}), automatic download...",
        "dll_conflict": "Existing version.dll file (not managed by this installer) detected.",
        "conflict_avoided": "Conflict avoided: the mod will be named '{name}' in the game folder.",
        "saving_orig": "Creating backup: version_orig.dll",
        "old_dll_removed": "Old version.dll removed from prefix.",
        "installing_tbone": "Installing tB0nE's version.dll into system32...",
        "wine_reg": "Configuring DLL overrides in Wine registry (user.reg)...",
        "install_done": "=== Installation completed successfully! ===",
        "mod_applied": "Mod applied successfully.",
        "copy_files": "Copying files to game directory: ",
        "warn_remove_dll": "Warning removing old dll: ",
        "exe_validated": "Validated executable: ",
        "error_prefix": "ERROR: "
    },
    "fr": {
        "window_title": "Installateur de Mods Frame Generation (Proton)",
        "header": "Assistant d'installation Frame Generation (dlssg_for_sm86)",
        "lang_btn": "English",
        "group_game": "Sélection du jeu Steam (et Non-Steam)",
        "games_detected": "Jeux détectés :",
        "show_all": "Afficher tous les jeux (y compris non-compatibles DLSS-G et outils)",
        "game_path": "Dossier du jeu : Aucun",
        "game_path_prefix": "Dossier du jeu : ",
        "group_env": "Configuration Steam requise",
        "env_label": "Variables d'environnement à ajouter dans les options de lancement Steam (proton-cachyos):",
        "copy_btn": "Copier",
        "group_logs": "Journal d'exécution",
        "update_cache_btn": "Mettre à jour le cache",
        "apply_btn": "Appliquer le mod",
        "copied_title": "Copié",
        "copied_msg": "Variable d'environnement copiée dans le presse-papier !",
        "cache_success_title": "Succès",
        "cache_success_msg": "Le cache a été vidé et mis à jour avec succès !",
        "cache_error_title": "Erreur",
        "cache_error_msg": "Échec de la mise à jour du cache :\n",
        "install_success_msg": "Le mod a été installé avec succès sur le jeu sélectionné !",
        "install_error_msg": "Une erreur est survenue :\n",
        "cancel_install": "Installation annulée : aucun exécutable sélectionné.",
        "select_exe": "Sélectionner l'exécutable (.exe) pour : ",
        "exe_filter": "Exécutables Windows (*.exe);Tous les fichiers (*)",
        "scan_start": "Recherche globale des jeux Steam et Non-Steam...",
        "steam_found": "Dossier Steam trouvé : ",
        "steam_error": "ERREUR: Impossible de localiser le dossier Steam.",
        "unsupported": "[Sans DLSS-G]",
        "display_count": "Affichage de {count} jeu(x) dans la liste (Filtre actif: {filter}).",
        "cache_clearing": "=== Vidage et mise à jour du cache local ===",
        "deleting_old": "Suppression ancien fichier : ",
        "downloading": "Téléchargement de ",
        "cache_updated": "=== Cache mis à jour avec succès ! ===",
        "cache_update_ok": "Cache mis à jour.",
        "install_start": "=== Début de l'installation du mod ===",
        "missing_cache": "Fichier manquant dans le cache ({name}), téléchargement automatique...",
        "dll_conflict": "Un fichier version.dll existant (non géré par cet installateur) a été détecté.",
        "conflict_avoided": "Conflit évité : le mod sera nommé '{name}' dans le dossier du jeu.",
        "saving_orig": "Création de la sauvegarde : version_orig.dll",
        "old_dll_removed": "Ancien fichier version.dll supprimé du préfixe.",
        "installing_tbone": "Installation du fichier version.dll de tB0nE dans system32...",
        "wine_reg": "Configuration des surcharges DLL dans le registre Wine (user.reg)...",
        "install_done": "=== Installation terminée avec succès ! ===",
        "mod_applied": "Mod appliqué avec succès.",
        "copy_files": "Copie des fichiers dans le dossier du jeu : ",
        "warn_remove_dll": "Avertissement suppression ancien dll : ",
        "exe_validated": "Exécutable validé : ",
        "error_prefix": "ERREUR: "
    }
}


def is_known_tool(name, appid):
    if str(appid) in ["0", "1493710", "228980"]:
        return True
    lower_name = name.lower()
    tool_keywords = [
        "proton", "steam linux runtime", "steamworks", "lossless scaling",
        "steam controller", "shared resources"
    ]
    return any(keyword in lower_name for keyword in tool_keywords)


def check_dlssg_in_path(folder_path):
    """
    Vérifie la présence de nvngx_dlssg.dll et renvoie le dossier racine du jeu 
    (évite de s'arrêter trop profondément dans des sous-dossiers comme NVStreamline/Production).
    """
    if not folder_path or not folder_path.exists():
        return False, None

    try:
        for p in folder_path.glob("**/*.dll"):
            parts_lower = [part.lower() for part in p.parts]
            if "windows" in parts_lower or "users" in parts_lower:
                continue
            if p.name.lower() == "nvngx_dlssg.dll":
                # Remonte au dossier principal du jeu (par ex. s'arrête 2 ou 3 niveaux au-dessus si c'est dans Binaries/Win64)
                # On cherche un dossier commun ou on prend le parent direct si aucun sous-dossier standard n'est détecté
                parent_dir = p.parent
                while parent_dir != folder_path and parent_dir.parent != folder_path:
                    # Si on croise un dossier comme Binaries, Win64, ou qu'on veut s'approcher de la racine du jeu
                    if parent_dir.name.lower() in ["binaries", "win64", "win32", "engine", "plugins"]:
                        parent_dir = parent_dir.parent
                        break
                    parent_dir = parent_dir.parent
                return True, folder_path  # Renvoie la base du dossier du jeu au lieu du sous-dossier lointain
    except Exception:
        pass
    return False, None


class CacheWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, cache_path, lang):
        super().__init__()
        self.cache_path = cache_path
        self.lang = lang

    def run(self):
        t = TRANSLATIONS[self.lang]
        try:
            self.log_signal.emit(t["cache_clearing"])
            if self.cache_path.exists():
                for file in self.cache_path.glob("*"):
                    try:
                        file.unlink()
                        self.log_signal.emit(t["deleting_old"] + file.name)
                    except Exception:
                        pass

            os.makedirs(self.cache_path, exist_ok=True)

            files_to_download = {
                "version_sdli.dll": "https://raw.githubusercontent.com/sdli1995/dlssg_for_sm86/main/version.dll",
                "dlssg_sm86.ini": "https://raw.githubusercontent.com/sdli1995/dlssg_for_sm86/main/dlssg_sm86.ini",
                "version_tbone.dll": "https://raw.githubusercontent.com/tB0nE/dlssg_for_sm86/main/linux-proton-fix/version.dll"
            }

            for filename, url in files_to_download.items():
                dest_file = self.cache_path / filename
                self.log_signal.emit(t["downloading"] + filename + "...")
                urllib.request.urlretrieve(url, dest_file)

            self.log_signal.emit(t["cache_updated"])
            self.finished_signal.emit(True, t["cache_update_ok"])
        except Exception as e:
            self.log_signal.emit(t["error_prefix"] + str(e))
            self.finished_signal.emit(False, str(e))


class InstallWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, game_info, cache_path, lang):
        super().__init__()
        self.game_info = game_info
        self.cache_path = cache_path
        self.lang = lang

    def run(self):
        t = TRANSLATIONS[self.lang]
        try:
            self.log_signal.emit(t["install_start"])
            os.makedirs(self.cache_path, exist_ok=True)

            files_to_check = ["version_sdli.dll", "dlssg_sm86.ini", "version_tbone.dll"]
            for f_name in files_to_check:
                if not (self.cache_path / f_name).exists():
                    self.log_signal.emit(t["missing_cache"].format(name=f_name))
                    urls = {
                        "version_sdli.dll": "https://raw.githubusercontent.com/sdli1995/dlssg_for_sm86/main/version.dll",
                        "dlssg_sm86.ini": "https://raw.githubusercontent.com/sdli1995/dlssg_for_sm86/main/dlssg_sm86.ini",
                        "version_tbone.dll": "https://raw.githubusercontent.com/tB0nE/dlssg_for_sm86/main/linux-proton-fix/version.dll"
                    }
                    urllib.request.urlretrieve(urls[f_name], self.cache_path / f_name)

            game_dir = pathlib.Path(self.game_info['path'])
            self.log_signal.emit(t["copy_files"] + str(game_dir))

            if not game_dir.exists():
                raise FileNotFoundError(f"Game directory not found: {game_dir}" if self.lang == "en" else f"Le dossier du jeu est introuvable : {game_dir}")

            marker_file = game_dir / ".dlssg_installer_managed"
            version_dll_path = game_dir / "version.dll"
            is_ours = marker_file.exists() and version_dll_path.exists()

            if version_dll_path.exists() and not is_ours:
                self.log_signal.emit(t["dll_conflict"])
                target_dll_name = None
                for alt_name in ["winmm.dll", "dinput8.dll", "winhttp.dll", "dxgi.dll"]:
                    if not (game_dir / alt_name).exists():
                        target_dll_name = alt_name
                        break
                if not target_dll_name:
                    target_dll_name = "winmm.dll"
                self.log_signal.emit(t["conflict_avoided"].format(name=target_dll_name))
            else:
                target_dll_name = "version.dll"

            target_game_dll = game_dir / target_dll_name

            if (self.cache_path / "version_sdli.dll").exists():
                if target_game_dll.exists():
                    try:
                        os.chmod(target_game_dll, 0o666)
                    except Exception:
                        pass
                with open(self.cache_path / "version_sdli.dll", "rb") as f_src, open(target_game_dll, "wb") as f_dst:
                    f_dst.write(f_src.read())

            if (self.cache_path / "dlssg_sm86.ini").exists():
                target_ini = game_dir / "dlssg_sm86.ini"
                if target_ini.exists():
                    try:
                        os.chmod(target_ini, 0o666)
                    except Exception:
                        pass
                with open(self.cache_path / "dlssg_sm86.ini", "rb") as f_src, open(target_ini, "wb") as f_dst:
                    f_dst.write(f_src.read())

            try:
                marker_file.write_text("managed_by_dlssg_installer", encoding="utf-8")
            except Exception:
                pass

            pfx_dir = pathlib.Path(self.game_info['prefix'])
            sys32_dir = pfx_dir / "drive_c" / "windows" / "system32"

            if not sys32_dir.exists():
                raise NotADirectoryError(f"System32 directory not found in Proton prefix: {sys32_dir}")

            target_dll = sys32_dir / "version.dll"
            orig_dll = sys32_dir / "version_orig.dll"

            if target_dll.exists():
                try:
                    os.chmod(target_dll, 0o666)
                except Exception:
                    pass

            if target_dll.exists() and not orig_dll.exists():
                self.log_signal.emit(t["saving_orig"])
                with open(target_dll, "rb") as f_src, open(orig_dll, "wb") as f_dst:
                    f_dst.write(f_src.read())

            if target_dll.exists():
                try:
                    target_dll.unlink()
                    self.log_signal.emit(t["old_dll_removed"])
                except Exception as e:
                    self.log_signal.emit(t["warn_remove_dll"] + str(e))

            self.log_signal.emit(t["installing_tbone"])
            tbone_src = self.cache_path / "version_tbone.dll"
            if tbone_src.exists():
                with open(tbone_src, "rb") as f_src, open(target_dll, "wb") as f_dst:
                    f_dst.write(f_src.read())
            else:
                raise FileNotFoundError("tB0nE's version.dll not found in cache.")

            user_reg = pfx_dir / "user.reg"
            if user_reg.exists():
                self.log_signal.emit(t["wine_reg"])
                with open(user_reg, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                section_header = "[Software\\\\Wine\\\\DllOverrides]"
                override_line = '"version"="native,builtin"'

                if section_header in content:
                    if override_line not in content:
                        content = content.replace(section_header, f"{section_header}\n{override_line}")
                else:
                    content += f"\n\n{section_header}\n{override_line}\n"

                try:
                    os.chmod(user_reg, 0o666)
                except Exception:
                    pass

                with open(user_reg, "w", encoding="utf-8") as f:
                    f.write(content)

            self.log_signal.emit(t["install_done"])
            self.finished_signal.emit(True, t["mod_applied"])
        except Exception as e:
            self.log_signal.emit(t["error_prefix"] + str(e))
            self.finished_signal.emit(False, str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "en"  # English by default
        self.games = []
        self.init_ui()
        self.scan_steam_games()

    def init_ui(self):
        t = TRANSLATIONS[self.current_lang]
        self.setWindowTitle(t["window_title"])
        self.setMinimumSize(750, 680)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        top_bar = QHBoxLayout()
        self.title_label = QLabel(t["header"])
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        top_bar.addWidget(self.title_label)

        top_bar.addStretch()

        self.lang_btn = QPushButton(t["lang_btn"])
        self.lang_btn.setFixedWidth(100)
        self.lang_btn.setStyleSheet("background-color: #34495e; color: white; border-radius: 4px; padding: 4px;")
        self.lang_btn.clicked.connect(self.toggle_language)
        top_bar.addWidget(self.lang_btn)

        main_layout.addLayout(top_bar)

        self.game_group = QGroupBox(t["group_game"])
        game_layout = QVBoxLayout(self.game_group)

        self.games_label_desc = QLabel(t["games_detected"])
        game_layout.addWidget(self.games_label_desc)

        self.game_combo = QComboBox()
        self.game_combo.setMinimumHeight(30)
        game_layout.addWidget(self.game_combo)

        self.show_all_checkbox = QCheckBox(t["show_all"])
        self.show_all_checkbox.setChecked(False)
        self.show_all_checkbox.toggled.connect(self.update_game_list)
        game_layout.addWidget(self.show_all_checkbox)

        self.path_label = QLabel(t["game_path"])
        self.path_label.setStyleSheet("color: gray;")
        game_layout.addWidget(self.path_label)

        main_layout.addWidget(self.game_group)

        self.env_group = QGroupBox(t["group_env"])
        env_layout = QVBoxLayout(self.env_group)
        self.env_desc_label = QLabel(t["env_label"])
        env_layout.addWidget(self.env_desc_label)

        env_box_layout = QHBoxLayout()
        self.env_input = QLabel("PROTON_NVIDIA_NVCUDA=1 %command%")
        self.env_input.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.env_input.setStyleSheet("background-color: #2b2b2b; color: #a9b7c6; padding: 6px; border-radius: 4px; font-family: monospace;")
        env_box_layout.addWidget(self.env_input)

        self.copy_btn = QPushButton(t["copy_btn"])
        self.copy_btn.setMaximumWidth(80)
        self.copy_btn.clicked.connect(self.copy_env_variable)
        env_box_layout.addWidget(self.copy_btn)

        env_layout.addLayout(env_box_layout)
        main_layout.addWidget(self.env_group)

        self.log_group = QGroupBox(t["group_logs"])
        log_layout = QVBoxLayout(self.log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: monospace; font-size: 11px;")
        log_layout.addWidget(self.log_text)

        main_layout.addWidget(self.log_group)

        bottom_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        bottom_layout.addWidget(self.progress_bar)

        self.update_cache_btn = QPushButton(t["update_cache_btn"])
        self.update_cache_btn.setMinimumHeight(35)
        self.update_cache_btn.setStyleSheet("background-color: #7f8c8d; color: white; border-radius: 4px;")
        self.update_cache_btn.clicked.connect(self.clear_and_update_cache)
        bottom_layout.addWidget(self.update_cache_btn)

        self.apply_btn = QPushButton(t["apply_btn"])
        self.apply_btn.setMinimumHeight(35)
        self.apply_btn.setStyleSheet("font-weight: bold; background-color: #2980b9; color: white; border-radius: 4px;")
        self.apply_btn.clicked.connect(self.apply_mod)
        bottom_layout.addWidget(self.apply_btn)

        main_layout.addLayout(bottom_layout)

        self.game_combo.currentIndexChanged.connect(self.on_game_selected)

    def toggle_language(self):
        self.current_lang = "fr" if self.current_lang == "en" else "en"
        t = TRANSLATIONS[self.current_lang]

        self.setWindowTitle(t["window_title"])
        self.title_label.setText(t["header"])
        self.lang_btn.setText(t["lang_btn"])
        self.game_group.setTitle(t["group_game"])
        self.games_label_desc.setText(t["games_detected"])
        self.show_all_checkbox.setText(t["show_all"])
        self.env_group.setTitle(t["group_env"])
        self.env_desc_label.setText(t["env_label"])
        self.copy_btn.setText(t["copy_btn"])
        self.log_group.setTitle(t["group_logs"])
        self.update_cache_btn.setText(t["update_cache_btn"])
        self.apply_btn.setText(t["apply_btn"])

        self.update_game_list()

    def load_steam_shortcuts(self, steam_root):
        shortcuts_map = {}
        userdata_dir = steam_root / "userdata"
        if not userdata_dir.exists():
            return shortcuts_map

        try:
            import vdf
        except ImportError:
            return shortcuts_map

        for user_dir in userdata_dir.iterdir():
            shortcuts_file = user_dir / "config" / "shortcuts.vdf"
            if not shortcuts_file.exists():
                continue

            try:
                with open(shortcuts_file, "rb") as f:
                    data = vdf.binary_load(f)
                    shortcuts = data.get('shortcuts', {})
                    
                    for _, shortcut in shortcuts.items():
                        if isinstance(shortcut, dict):
                            app_name = shortcut.get('appname') or shortcut.get('AppName', '')
                            exe = shortcut.get('exe') or shortcut.get('Exe', '')
                            start_dir = shortcut.get('StartDir') or shortcut.get('startdir', '')
                            appid_val = shortcut.get('appid') or shortcut.get('AppID')
                            
                            if app_name:
                                exe_clean = exe.strip('"') if exe else ""
                                dir_clean = start_dir.strip('"') if start_dir else ""
                                
                                info = {
                                    "name": app_name,
                                    "exe": exe_clean,
                                    "dir": dir_clean
                                }

                                if appid_val is not None:
                                    unsigned_appid = appid_val & 0xFFFFFFFF
                                    shortcuts_map[str(unsigned_appid)] = info

                                if exe:
                                    unique_string = exe + app_name
                                    crc = binascii.crc32(unique_string.encode('utf-8')) & 0xFFFFFFFF
                                    compat_id = crc | 0x80000000
                                    shortcuts_map[str(compat_id)] = info
                                    shortcuts_map[str(crc)] = info
                                    
                                    unique_string_clean = exe_clean + app_name
                                    crc_clean = binascii.crc32(unique_string_clean.encode('utf-8')) & 0xFFFFFFFF
                                    shortcuts_map[str(crc_clean | 0x80000000)] = info
                                    shortcuts_map[str(crc_clean)] = info

                                    if exe_clean:
                                        p = pathlib.Path(exe_clean)
                                        shortcuts_map[p.name.lower()] = info
            except Exception:
                pass

        return shortcuts_map

    def scan_steam_games(self):
        t = TRANSLATIONS[self.current_lang]
        self.log_text.append(t["scan_start"])
        steam_paths = [
            pathlib.Path.home() / ".local" / "share" / "Steam",
            pathlib.Path.home() / ".steam" / "steam",
            pathlib.Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam"
        ]

        steam_root = None
        for path in steam_paths:
            if (path / "steamapps").exists():
                steam_root = path
                break

        if not steam_root:
            self.log_text.append(t["steam_error"])
            return

        self.log_text.append(t["steam_found"] + str(steam_root))
        
        non_steam_names = self.load_steam_shortcuts(steam_root)

        library_folders = [steam_root]
        vdf_path = steam_root / "steamapps" / "libraryfolders.vdf"
        if vdf_path.exists():
            try:
                with open(vdf_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    paths = re.findall(r'"path"\s+"([^"]+)"', content)
                    for p in paths:
                        lib_path = pathlib.Path(p.replace('\\\\', '\\'))
                        if lib_path not in library_folders and (lib_path / "steamapps").exists():
                            library_folders.append(lib_path)
            except Exception:
                pass

        self.games = []
        matched_appids = set()

        global_steam_manifests = {}
        for lib in library_folders:
            steamapps = lib / "steamapps"
            if not steamapps.exists():
                continue

            for manifest in steamapps.glob("appmanifest_*.acf"):
                try:
                    with open(manifest, "r", encoding="utf-8") as f:
                        content = f.read()
                        appid_match = re.search(r'"appid"\s+"(\d+)"', content)
                        name_match = re.search(r'"name"\s+"([^"]+)"', content)
                        install_dir_match = re.search(r'"installdir"\s+"([^"]+)"', content)

                        if appid_match and name_match and install_dir_match:
                            aid = appid_match.group(1)
                            global_steam_manifests[aid] = {
                                "name": name_match.group(1),
                                "path": steamapps / "common" / install_dir_match.group(1)
                            }
                except Exception:
                    continue

        for lib in library_folders:
            compatdata_dir = lib / "steamapps" / "compatdata"
            if not compatdata_dir.exists():
                continue

            for compat_folder in compatdata_dir.iterdir():
                if not compat_folder.is_dir():
                    continue
                
                appid_str = compat_folder.name
                if appid_str in matched_appids or appid_str == "0":
                    continue

                prefix_path = compat_folder / "pfx"
                if not prefix_path.exists():
                    continue

                is_steam_game = appid_str in global_steam_manifests
                has_dlssg = False
                actual_game_dir = None
                game_name = ""

                if is_steam_game:
                    game_path = global_steam_manifests[appid_str]["path"]
                    game_name = global_steam_manifests[appid_str]["name"]
                    actual_game_dir = game_path
                    if game_path.exists():
                        has_dlssg, found_dir = check_dlssg_in_path(game_path)
                        if has_dlssg:
                            actual_game_dir = found_dir
                else:
                    shortcut_info = non_steam_names.get(appid_str)
                    
                    paths_to_check = []
                    if shortcut_info:
                        if shortcut_info.get("dir"):
                            paths_to_check.append(pathlib.Path(shortcut_info["dir"]))
                        if shortcut_info.get("exe"):
                            paths_to_check.append(pathlib.Path(shortcut_info["exe"]).parent)
                    
                    paths_to_check.append(prefix_path / "drive_c")

                    dosdevices_dir = prefix_path / "dosdevices"
                    if dosdevices_dir.exists():
                        for link in dosdevices_dir.iterdir():
                            link_name = link.name.lower()
                            if link_name in ["c:", "z:", "c", "z"]:
                                continue
                            if link.is_symlink():
                                try:
                                    target = link.resolve()
                                    if target.exists() and not str(target).startswith(("/sys", "/proc", "/dev")):
                                        paths_to_check.append(target)
                                except Exception:
                                    pass

                    for p_check in paths_to_check:
                        if p_check and p_check.exists():
                            has_dlssg, found_dir = check_dlssg_in_path(p_check)
                            if has_dlssg:
                                actual_game_dir = found_dir
                                break

                    if shortcut_info and shortcut_info.get("name"):
                        game_name = f"[Non-Steam] {shortcut_info['name']}"
                    elif actual_game_dir:
                        exes = list(actual_game_dir.glob("*.exe"))
                        valid_exes = [e for e in exes if "uninstall" not in e.name.lower()]
                        if valid_exes:
                            game_name = f"[Non-Steam] {valid_exes[0].stem}"
                        else:
                            game_name = f"[Non-Steam] (ID: {appid_str})"
                    else:
                        game_name = f"[Non-Steam] (ID: {appid_str})"
                        actual_game_dir = prefix_path

                is_tool = is_known_tool(game_name, appid_str)
                matched_appids.add(appid_str)

                self.games.append({
                    "name": game_name,
                    "appid": appid_str,
                    "path": str(actual_game_dir or prefix_path),
                    "prefix": str(prefix_path),
                    "supports_dlssg": has_dlssg,
                    "is_tool": is_tool
                })

        self.update_game_list()

    def update_game_list(self):
        t = TRANSLATIONS[self.current_lang]
        show_all = self.show_all_checkbox.isChecked()
        self.game_combo.blockSignals(True)
        self.game_combo.clear()

        filtered_games = []
        for game in self.games:
            if show_all or (game['supports_dlssg'] and not game['is_tool']):
                filtered_games.append(game)

        for game in sorted(filtered_games, key=lambda x: x['name']):
            display_str = game['name']
            if game['appid'] and game['appid'] != "0":
                display_str += f" (AppID: {game['appid']})"
            if not game['supports_dlssg']:
                display_str += f" {t['unsupported']}"
            self.game_combo.addItem(display_str, game)

        self.game_combo.blockSignals(False)

        if self.game_combo.count() > 0:
            self.game_combo.setCurrentIndex(0)
            self.on_game_selected(0)
        else:
            self.path_label.setText(t["game_path"])

        self.log_text.append(t["display_count"].format(count=len(filtered_games), filter=not show_all))

    def on_game_selected(self, index):
        t = TRANSLATIONS[self.current_lang]
        if index >= 0 and index < self.game_combo.count():
            game_data = self.game_combo.itemData(index)
            if game_data:
                self.path_label.setText(t["game_path_prefix"] + game_data['path'])

    def copy_env_variable(self):
        t = TRANSLATIONS[self.current_lang]
        clipboard = QApplication.clipboard()
        clipboard.setText(self.env_input.text())
        QMessageBox.information(self.window(), t["copied_title"], t["copied_msg"])

    def clear_and_update_cache(self):
        self.update_cache_btn.setEnabled(False)
        self.apply_btn.setEnabled(False)
        self.progress_bar.show()

        self.cache_worker = CacheWorker(CACHE_DIR, self.current_lang)
        self.cache_worker.log_signal.connect(lambda msg: self.log_text.append(msg))
        self.cache_worker.finished_signal.connect(self.on_cache_update_finished)
        self.cache_worker.start()

    def on_cache_update_finished(self, success, message):
        t = TRANSLATIONS[self.current_lang]
        self.update_cache_btn.setEnabled(True)
        self.apply_btn.setEnabled(True)
        self.progress_bar.hide()
        if success:
            QMessageBox.information(self, t["cache_success_title"], t["cache_success_msg"])
        else:
            QMessageBox.critical(self, t["cache_error_title"], t["cache_error_msg"] + message)

    def apply_mod(self):
        t = TRANSLATIONS[self.current_lang]
        game_data = self.game_combo.currentData()
        if not game_data:
            QMessageBox.warning(self, "Warning" if self.current_lang == "en" else "Attention", "Please select a valid game." if self.current_lang == "en" else "Veuillez sélectionner un jeu valide.")
            return

        start_dir = game_data['path']
        exe_path, _ = QFileDialog.getOpenFileName(
            self,
            t["select_exe"] + game_data['name'],
            start_dir,
            t["exe_filter"],
            options=QFileDialog.Option.DontUseNativeDialog
        )

        if not exe_path:
            self.log_text.append(t["cancel_install"])
            return

        target_game_dir = str(pathlib.Path(exe_path).parent)
        game_data['path'] = target_game_dir
        self.path_label.setText(t["game_path_prefix"] + target_game_dir)
        self.log_text.append(t["exe_validated"] + exe_path)

        self.apply_btn.setEnabled(False)
        self.update_cache_btn.setEnabled(False)
        self.progress_bar.show()

        self.worker = InstallWorker(game_data, CACHE_DIR, self.current_lang)
        self.worker.log_signal.connect(lambda msg: self.log_text.append(msg))
        self.worker.finished_signal.connect(self.on_installation_finished)
        self.worker.start()

    def on_installation_finished(self, success, message):
        t = TRANSLATIONS[self.current_lang]
        self.apply_btn.setEnabled(True)
        self.update_cache_btn.setEnabled(True)
        self.progress_bar.hide()
        if success:
            QMessageBox.information(self, t["cache_success_title"], t["install_success_msg"])
        else:
            QMessageBox.critical(self, t["cache_error_title"], t["install_error_msg"] + message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())