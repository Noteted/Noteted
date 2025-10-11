import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os
import sys
import webbrowser
import datetime
import src.backend.getFromJSON as getJson
import src.backend.settings as Nsettings
import src.handler.path as pathHandler
import src.handler.theme as themeHandler
import src.main.Noteted as NotetedMain

def topLevelIcon(toplevel_window):
    baseDirectory = pathHandler.mainPath()
    if sys.platform == "win32":
        iconPath = os.path.join(baseDirectory, 'assets', 'NTD.ico')
        if os.path.exists(iconPath):
            toplevel_window.after(200, lambda: toplevel_window.iconbitmap(iconPath))
    else:
        iconPath = os.path.join(baseDirectory, 'assets', 'NTD.png')
        if os.path.exists(iconPath):
            photo = tk.PhotoImage(file=iconPath)
            toplevel_window.iconphoto(False, photo)

def delete(filePath, reload_callback):
    deleteWindow = ctk.CTkToplevel()
    deleteWindow.title("Noteted - Delete")
    deleteWindow.geometry("400x100")
    deleteWindow.resizable(False, False)

    deleteWindow.configure(fg_color=themeHandler.getThemePart("background"))
    ctk.set_appearance_mode(themeHandler.getThemePart("WPM"))
    ctk.set_default_color_theme(themeHandler.getThemePart("DCT"))

    deleteWindow.transient()
    deleteWindow.after(10, deleteWindow.grab_set)
    topLevelIcon(deleteWindow)

    def proceedOperation():
        try:
            os.remove(filePath)
            if reload_callback:
                reload_callback()
        except Exception as e:
            messageBox("Error", f"Failed to delete file: {e}")
        finally:
            deleteWindow.destroy()

    def cancelOperation():
        deleteWindow.destroy()

    container = ctk.CTkFrame(deleteWindow, fg_color=themeHandler.getThemePart("frame"))
    container.pack(pady=10, padx=10, expand=True, fill="both")

    label = ctk.CTkLabel(container, text=f"Are you sure you want to delete ''' {os.path.basename(filePath)} '''?", wraplength=380, text_color=themeHandler.getThemePart("text"))
    label.pack(pady=(3, 0), padx=5, expand=True, fill="both")

    buttonFrame = ctk.CTkFrame(container, fg_color="transparent")
    buttonFrame.pack(pady=10, padx=10, fill="x")

    yesButton = ctk.CTkButton(buttonFrame, text="Yes", command=proceedOperation, text_color=themeHandler.getThemePart("text"), fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
    yesButton.pack(side="left", expand=True, fill="x", padx=(0, 5))

    noButton = ctk.CTkButton(buttonFrame, text="No", command=cancelOperation, text_color=themeHandler.getThemePart("text"), fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
    noButton.pack(side="right", expand=True, fill="x", padx=(5, 0))

def rename(filePath, reload_callback):
    renameWindow = ctk.CTkToplevel()
    renameWindow.title("Noteted - Rename")
    renameWindow.geometry("350x150")
    renameWindow.resizable(False, False)

    renameWindow.configure(fg_color=themeHandler.getThemePart("background"))
    ctk.set_appearance_mode(themeHandler.getThemePart("WPM"))
    ctk.set_default_color_theme(themeHandler.getThemePart("DCT"))

    renameWindow.transient()
    renameWindow.after(10, renameWindow.grab_set)
    topLevelIcon(renameWindow)

    def intializeRename():
        newName = entry.get()
        if newName:
            try:
                directory = os.path.dirname(filePath)
                _, currentExt = os.path.splitext(filePath)
                _, newExt = os.path.splitext(newName)

                if not newExt:
                    newName += currentExt
                
                newFilePath = os.path.join(directory, newName)

                if os.path.exists(newFilePath):
                    messageBox("Error", "File already exists!")
                    return

                os.rename(filePath, newFilePath)
                if reload_callback:
                    reload_callback()
                renameWindow.destroy()
            except Exception as e:
                messageBox("Error", f"Failed to rename file: {e}")

    def do_cancel():
        renameWindow.destroy()

    container = ctk.CTkFrame(renameWindow, fg_color=themeHandler.getThemePart("frame"))
    container.pack(pady=10, padx=10, expand=True, fill="both")

    label = ctk.CTkLabel(container, text="Enter new name:", text_color=themeHandler.getThemePart("text"))
    label.pack(pady=(10,0), padx=10)

    entry = ctk.CTkEntry(container)
    entry.insert(0, os.path.basename(filePath))
    entry.pack(pady=5, padx=10, fill="x")

    buttonFrame = ctk.CTkFrame(container, fg_color="transparent")
    buttonFrame.pack(pady=10, padx=10, fill="x")

    renameButton = ctk.CTkButton(buttonFrame, text="Rename", command=intializeRename, text_color=themeHandler.getThemePart("text"), fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
    renameButton.pack(side="left", expand=True, fill="x", padx=(0, 5))

    cancelButton = ctk.CTkButton(buttonFrame, text="Cancel", command=do_cancel, text_color=themeHandler.getThemePart("text"), fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
    cancelButton.pack(side="right", expand=True, fill="x", padx=(5, 0))

def settings(root):
    currentSettings = Nsettings.loadSettings()
    settingsDefinitions = Nsettings.getSettingsDef(currentSettings)
    
    # --- calculate window height based on number of settings ---
    baseHeight = 120  # base height for padding, title bar, and buttons
    heightPerSetting = 40  # approximate height for each setting row
    newHeight = baseHeight + (len(settingsDefinitions) * heightPerSetting)

    settingsWindow = ctk.CTkToplevel()
    settingsWindow.title("Noteted - Settings")
    settingsWindow.geometry(f"450x{newHeight}")
    settingsWindow.resizable(False, True)

    settingsWindow.configure(fg_color=themeHandler.getThemePart("background"))
    ctk.set_appearance_mode(themeHandler.getThemePart("WPM"))
    ctk.set_default_color_theme(themeHandler.getThemePart("DCT"))

    settingsWindow.transient()
    settingsWindow.after(10, settingsWindow.grab_set)

    topLevelIcon(settingsWindow)

    settingContainer = ctk.CTkFrame(settingsWindow, corner_radius=10, fg_color=themeHandler.getThemePart("frame"))
    settingContainer.pack(pady=10, padx=10, expand=True, fill="both")

    Nsettings.listAllSettings(settingContainer, currentSettings)

    buttonFrame = ctk.CTkFrame(settingsWindow, fg_color="transparent")
    buttonFrame.pack(pady=10, padx=10, expand=True, fill="x")

    def saveSettings():
        print("Settings window closed!")
        Nsettings.saveSettings(currentSettings)
        NotetedMain.refreshUI(root)
        settingsWindow.destroy()

    saveButton = ctk.CTkButton(buttonFrame, text="Save & Close", command=saveSettings, width=100, text_color=themeHandler.getThemePart("text"), fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
    saveButton.pack(side="left", expand=True, fill="x", padx=(10, 5))

    cancelButton = ctk.CTkButton(buttonFrame, text="Cancel", command=settingsWindow.destroy, width=100, text_color=themeHandler.getThemePart("text"), fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
    cancelButton.pack(side="right", expand=True, fill="x", padx=(5, 10))

def newFile(reloadCallback=None):
    newFileWindow = ctk.CTkToplevel()
    newFileWindow.title("Noteted - New File")
    newFileWindow.geometry("450x150")
    newFileWindow.resizable(False, False)

    newFileWindow.configure(fg_color=themeHandler.getThemePart("background"))
    ctk.set_appearance_mode(themeHandler.getThemePart("WPM"))
    ctk.set_default_color_theme(themeHandler.getThemePart("DCT"))

    newFileWindow.transient()
    newFileWindow.after(10, newFileWindow.grab_set)

    topLevelIcon(newFileWindow)

    def createFileWithExtension(extension):
        baseName = fileNameEntry.get()
        if not baseName:
            messageBox("Error", "File name cannot be empty.")
            return

        fileName = f"{baseName}{extension}"
        notesDirectory = getJson.getSetting("NotesDirectory")
        filePath = os.path.join(notesDirectory, fileName) # type: ignore

        if os.path.exists(filePath):
            messageBox("Error", "File already exists.")
            return

        try:
            with open(filePath, 'w') as f:
                f.write("")
            print(f"File '''{fileName}''' created successfully.")
            if reloadCallback:
                reloadCallback()
            newFileWindow.destroy()
        except Exception as e:
            messageBox("Error", f"Error creating file: {e}")

    container = ctk.CTkFrame(newFileWindow, fg_color=themeHandler.getThemePart("frame"))
    container.pack(pady=10, padx=10, expand=True, fill="both")

    titleLabel = ctk.CTkLabel(container, text="Cookin' up a new file...", font=ctk.CTkFont(size=24, weight="bold"), text_color=themeHandler.getThemePart("text"))
    titleLabel.pack(pady=10, padx=10)

    fileNameEntry = ctk.CTkEntry(container, placeholder_text="Enter filename here..." , text_color=themeHandler.getThemePart("text"))
    now = datetime.datetime.now()
    defaultFileName = now.strftime("%Y-%m-%d")
    fileNameEntry.insert(0, defaultFileName)
    fileNameEntry.pack(fill="x", padx=10)

    # --- Button Container ---
    buttonFrame = ctk.CTkFrame(container, fg_color="transparent")
    buttonFrame.pack(pady=10, padx=10, expand=True, fill="x")
    
    mdButton = ctk.CTkButton(buttonFrame, text="Markdown", command=lambda: createFileWithExtension(".md"), width=100, text_color=themeHandler.getThemePart("text"), fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
    mdButton.pack(side="left", expand=True, fill="x", padx=10)

    tdButton = ctk.CTkButton(buttonFrame, text="TODO", command=lambda: createFileWithExtension(".td"), width=100, text_color=themeHandler.getThemePart("text"), fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
    tdButton.pack(side="left", expand=True, fill="x", padx=10)

    txtButton = ctk.CTkButton(buttonFrame, text="Text", command=lambda: createFileWithExtension(".txt"), width=100, text_color=themeHandler.getThemePart("text"), fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
    txtButton.pack(side="left", expand=True, fill="x", padx=10)

    newFileWindow.protocol("WM_DELETE_WINDOW", newFileWindow.destroy)

def info():
    infoWindow = ctk.CTkToplevel()
    infoWindow.title("Noteted - Info")
    infoWindow.geometry("400x325")
    infoWindow.resizable(False, False)

    infoWindow.configure(fg_color=themeHandler.getThemePart("background"))
    ctk.set_appearance_mode(themeHandler.getThemePart("WPM"))
    ctk.set_default_color_theme(themeHandler.getThemePart("DCT"))

    infoWindow.transient()
    infoWindow.after(10, infoWindow.grab_set)
    
    topLevelIcon(infoWindow)

    def redirectGithub():
        webbrowser.open_new_tab("https://github.com/Noteted/Noteted")
    def redirectWebsite():
        webbrowser.open_new_tab("https://noteted.netlify.app/")

    container = ctk.CTkFrame(infoWindow, fg_color=themeHandler.getThemePart("frame"))
    container.pack(pady=10, padx=10, expand=True, fill="both")

    # --- Image ---
    logoPath = os.path.join(pathHandler.assetsPath(), 'NTD.png')
    if os.path.exists(logoPath):
        pilImage = Image.open(logoPath)
        ctkImage = ctk.CTkImage(pilImage, size=(100, 100))
        
        imageLabel = ctk.CTkLabel(container, image=ctkImage, text="", text_color=themeHandler.getThemePart("text"))
        imageLabel.image = ctkImage # type: ignore
        imageLabel.pack(pady=10)

    # --- Text ---
    versionContent = ""
    versionPath = os.path.join(pathHandler.mainPath(), 'gitver.txt')
    if os.path.exists(versionPath):
        with open(versionPath, 'r') as f:
            versionContent = f.read().strip()
    
    titleText = ctk.CTkLabel(container, text="Noteted", font=ctk.CTkFont(size=24, weight="bold"))
    infoText = ctk.CTkLabel(container, text="A simple, free and open source note taking app.", wraplength=340)
    maintainerText = ctk.CTkLabel(container, text="Maintained by Daveberry Blueson.", wraplength=340)
    versionText = ctk.CTkLabel(container, text=versionContent, wraplength=340)
    
    titleText.pack(pady=(0, 10))
    infoText.pack()
    maintainerText.pack()
    versionText.pack()

    titleText.configure(text_color=themeHandler.getThemePart("text"))
    infoText.configure(text_color=themeHandler.getThemePart("text"))
    maintainerText.configure(text_color=themeHandler.getThemePart("text"))
    versionText.configure(text_color=themeHandler.getThemePart("text"))

    # --- Buttons ---
    buttonContainer = ctk.CTkFrame(container, fg_color="transparent")
    buttonContainer.pack(pady=10, padx=10, expand=True, fill="x")

    githubButton = ctk.CTkButton(buttonContainer, text="Github", command=redirectGithub, fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
    githubButton.pack(side="left", expand=True, fill="x", padx=(10, 5))

    websiteButton = ctk.CTkButton(buttonContainer, text="Website", command=redirectWebsite, fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
    websiteButton.pack(side="left", expand=True, fill="x", padx=(5, 10))

    infoWindow.protocol("WM_DELETE_WINDOW", infoWindow.destroy)

def messageBox(title, message):
    _messageBox = ctk.CTkToplevel()
    _messageBox.title("Noteted - " + title)
    _messageBox.geometry("300x75")
    _messageBox.resizable(False, False)

    _messageBox.configure(fg_color=themeHandler.getThemePart("background"))
    ctk.set_appearance_mode(themeHandler.getThemePart("WPM"))
    ctk.set_default_color_theme(themeHandler.getThemePart("DCT"))

    _messageBox.transient()
    _messageBox.after(10, _messageBox.grab_set)
    topLevelIcon(_messageBox)
    
    messageBoxContainer = ctk.CTkFrame(_messageBox, fg_color=themeHandler.getThemePart("frame"))
    messageBoxContainer.pack(pady=10, padx=10, expand=True, fill="both")

    messageLabel = ctk.CTkLabel(messageBoxContainer, text=message, text_color=themeHandler.getThemePart("text"))
    messageLabel.pack(pady=10, padx=10, fill="both")

    _messageBox.protocol("WM_DELETE_WINDOW", _messageBox.destroy)
    _messageBox.mainloop()