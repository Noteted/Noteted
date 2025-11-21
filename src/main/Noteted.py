import customtkinter as ctk
import tkinter as tk
import os
import sys
from PIL import Image, ImageColor
import src.backend.discord as dcPresence
import src.backend.getFromJSON as getJson
import src.main.NTDwindow as NTDwindow
import src.renderers.todo as tdRenderer
import src.renderers.markdown as markdownRenderer
import src.renderers.text as textRenderer
import src.handler.path as pathHandler
import src.handler.saving as savingHandler
import src.handler.theme as themeHandler
import src.handler.rightClickMenu as rightClickMenu
import src.handler.todoEditor as todoEditorHandler

# ===== guess by the definition =====
def initializeUI():
    root = ctk.CTk()
    root.title("Noteted")
    root.geometry("1280x720")
    root.minsize(800, 600)
    root.configure(fg_color=themeHandler.getThemePart("background"))
    ctk.set_appearance_mode(themeHandler.getThemePart("WPM"))
    ctk.set_default_color_theme(themeHandler.getThemePart("DCT"))

    baseDirectory = pathHandler.mainPath()
    if sys.platform == "win32":
        iconPath = os.path.join(baseDirectory, 'assets', 'NTD.ico')
        if os.path.exists(iconPath):
            root.iconbitmap(iconPath)
    else:
        iconPath = os.path.join(baseDirectory, 'assets', 'NTD.png')
        if os.path.exists(iconPath):
            root.iconphoto(False, tk.PhotoImage(file=iconPath))

    # meow this is for the opened file background :3
    openedFileButton = {"button": None}

    # say hi to sidebarFrame AND topbarFrame because it's here to fix the FUCKING aligment :333
    topbarFrame = topBar(root)
    sidebarFrame = sidebar(root)

    mainContentFrame = ctk.CTkFrame(root, fg_color="transparent")
    mainContentFrame.pack(pady=10, padx=(0, 10), expand=True, fill="both", side="left")

    writingBox2 = textbox(mainContentFrame)

    previewContainer = markdownRenderer.previewbox(mainContentFrame)
    previewBox2 = previewContainer.label # type: ignore
    TDrenderFrame = createTDrender(mainContentFrame)

    saver = savingHandler.Saver()

    if getJson.getSetting("EnableDiscordRPC"):
        print("Discord RPC is enabled in settings! Initializing...")
        dcRPC(root, saver)
    else:
        print("Discord RPC is disabled in settings")

    def closing():
        if pathHandler.getSetting("EnableDiscordRPC"):
            # hey dw about this it's just to make sure it stops properly
            # don't ask why it actually fuckign works
            for meow in range(15):
                break
        saver.stop()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", closing)

    def updatePreviewWrapper(event=None):
        markdownRenderer.updatePreview(writingBox2, previewBox2)

    def reloadCallback():
        reloadFileList(sidebarFrame, writingBox2, previewContainer, TDrenderFrame, updatePreviewWrapper, openedFileButton, saver, rightClickSidebar.popup)

    rightClickSidebar = rightClickMenu.RightClickMenu(root, reloadCallback)

    listFiles(sidebarFrame, writingBox2, previewContainer, TDrenderFrame, updatePreviewWrapper, openedFileButton, saver, rightClickSidebar.popup)
    writingBox2.bind("<KeyRelease>", updatePreviewWrapper)

    bindKeybinds(root, reloadCallback, updatePreviewWrapper, saver, None)

    buttons(topbarFrame, reloadCallback, root)
    topBarText(topbarFrame)
    root.mainloop()

if __name__ == "__main__":
    initializeUI()

# ===== button functions stuff =====
def funcOptionsButton(root):
    NTDwindow.settings(root)

def funcNewFileButton(reloadList):
    NTDwindow.newFile(reloadList)

def funcInfoButton():
    NTDwindow.info()

# ===== other ui stuff =====
# thanks gemini code assist! you're great :3
def recolorImage(image_path, color="#FFFFFF"):
    try:
        img = Image.open(image_path).convert("RGBA")
    except FileNotFoundError:
        return None

    color_img = Image.new("RGB", img.size, ImageColor.getrgb(color))
    img.paste(color_img, (0, 0), mask=img.split()[3])
    return img

def topBar(root):
    topbar = ctk.CTkFrame(root, height=50, width=400, corner_radius=0, fg_color=themeHandler.getThemePart("frame"))
    topbar.pack(side="top", fill="x")
    topbar.pack_propagate(False)

    return topbar

def buttons(frame, reloadList, root):
    iconSize = (20, 20)
    buttonSize = 30

    buttonFrame = ctk.CTkFrame(frame, fg_color="transparent")
    buttonFrame.pack(pady=10, padx=10, fill="x")

    initializeButtons = [
        {
            "iconPath": "tool",
            "command": lambda: funcOptionsButton(root),
            "text": "Options"
        },
        {
            "iconPath": "file-plus",
            "command": lambda: funcNewFileButton(reloadList),
            "text": "New File"
        },
        {
            "iconPath": "info",
            "command": funcInfoButton,
            "text": "Info"
        }
    ]

    for button_info in initializeButtons:
        buttonIcon = button_info["iconPath"]
        buttonCommand = button_info["command"]
        buttonText = button_info["text"]

        _iconPath = pathHandler.iconsPath("buttons", buttonIcon + ".png")
        if os.path.exists(_iconPath): # type: ignore
            _buttonIcon = ctk.CTkImage(recolorImage(_iconPath, color=themeHandler.getThemePart("button")), size=iconSize) # type: ignore
            _button = ctk.CTkButton(buttonFrame, image=_buttonIcon, text="", command=buttonCommand, width=buttonSize, height=buttonSize, fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
        else:
            _button = ctk.CTkButton(buttonFrame, text=buttonText, command=buttonCommand, width=85, text_color=themeHandler.getThemePart("text"), fg_color=themeHandler.getThemePart("accent"), hover_color=themeHandler.getThemePart("hover"))
        _button.pack(side="left", expand=False, padx=(20, 0))

def topBarText(parent):
    workspaceLabel = ctk.CTkLabel(parent, text="Test", text_color=themeHandler.getThemePart("text"))
    workspaceLabel.pack(padx=10, side="left")

def sidebar(root):
    sidebarContainer = ctk.CTkFrame(root, fg_color="transparent")
    sidebarContainer.pack(pady=10, padx=(10, 0), side="left", fill="y")

    sidebarFrame = ctk.CTkScrollableFrame(sidebarContainer, width=200, corner_radius=10,
                                         fg_color=themeHandler.getThemePart("frame"))
    sidebarFrame.pack(side="left", fill="both", expand=True)

    # funny dragging things because some people (like me) like to name our files with long names :3c
    # also because gemini code assist helped me with this :3 (I'M TOO DUMB TO FIGURE IT OUT MYSELF)
    resizer = ctk.CTkFrame(sidebarContainer, width=4, cursor="sb_h_double_arrow")
    resizer.pack(side="left", fill="y", padx=2)

    dragState = {"x": 0}

    def onDrag(event):
        dx = event.x_root - dragState["x"]
        currentWidth = sidebarFrame.winfo_width()
        newWidth = currentWidth + dx
        if 150 <= newWidth <= 600:
            sidebarFrame.configure(width=newWidth)
        dragState["x"] = event.x_root

    def onButtonRelease(event):
        root.unbind("<B1-Motion>")
        root.unbind("<ButtonRelease-1>")

    def onButtonPress(event):
        dragState["x"] = event.x_root
        root.bind("<B1-Motion>", onDrag)
        root.bind("<ButtonRelease-1>", onButtonRelease)

    resizer.bind("<ButtonPress-1>", onButtonPress)

    return sidebarFrame

def textbox(parent):
    writingbox = ctk.CTkTextbox(parent, width=400, height=300, corner_radius=10, wrap="word",
                                fg_color=themeHandler.getThemePart("frame"), font=("Arial", 14))
    writingbox.pack(padx=(0, 10), side="left", fill="both", expand=True)
    return writingbox

def createTDrender(parent):
    tdRendererContainer = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
    return tdRendererContainer

def reloadFileList(sidebarFrame, writingBox, previewContainer, TDrenderFrame, updatePreview, openedFileButton, saver, popupMenu):
    for widget in sidebarFrame.winfo_children():
        widget.destroy()
    listFiles(sidebarFrame, writingBox, previewContainer, TDrenderFrame, updatePreview, openedFileButton, saver, popupMenu)

# again, gemini because I don't feel like figuring out how to do this myself :3
def listFiles(part, writingBox, previewContainer, TDrenderFrame, updatePreview, openedFileButton, saver, popupMenu):
    notesDirectory = getJson.getSetting("NotesDirectory")
    if not os.path.exists(notesDirectory): # type: ignore
        print("Notes directory not found, creating one...")
        os.makedirs(notesDirectory) # type: ignore

    for fileName in os.listdir(notesDirectory):
        if fileName.endswith((".md", ".td", ".txt")):
            filePath = os.path.join(notesDirectory, fileName) # type: ignore
            button = ctk.CTkButton(part, text=fileName, fg_color="transparent", hover_color=themeHandler.getThemePart("frameHover"), text_color=themeHandler.getThemePart("frameText"))
            button.bind("<Button-3>", lambda event, path=filePath: popupMenu(event, path))

            def loadFileContent(path=filePath, btn=button):
                previousOpenedButton = openedFileButton["button"]

                openedFileButton["button"] = btn
                btn.configure(fg_color=themeHandler.getThemePart("selected"))

                if previousOpenedButton and previousOpenedButton.winfo_exists():
                    previousOpenedButton.configure(fg_color="transparent")

                bindKeybinds(writingBox.master.master, lambda: reloadFileList(part, writingBox, previewContainer, TDrenderFrame, updatePreview, openedFileButton, saver, popupMenu), lambda: markdownRenderer.updatePreview(writingBox, previewContainer.label), saver, path)

                with open(path, "r", encoding='utf-8') as file:
                    content = file.read()

                writingBox.delete("1.0", tk.END)
                writingBox.insert("1.0", content)

                saver.start(path, lambda: writingBox.get("1.0", tk.END))

                writingBox.pack_forget()
                previewContainer.pack_forget()
                TDrenderFrame.pack_forget()

                if path.endswith(".md"):
                    markdownRenderer.renderMarkdown(writingBox, previewContainer, updatePreview)
                elif path.endswith(".txt"):
                    textRenderer.renderText(writingBox)
                elif path.endswith(".td"):
                    saver.stop()
                    for widget in TDrenderFrame.winfo_children():
                        widget.destroy()

                    # -- Frame for Raw File Editor --
                    textEditorFrame = ctk.CTkFrame(TDrenderFrame, fg_color="transparent")
                    textEditorFrame.pack(fill="both", padx=0, pady=0, side="bottom")

                    rawTextEditor = ctk.CTkTextbox(textEditorFrame, fg_color=themeHandler.getThemePart("frame"))
                    rawTextEditor.pack(fill="both", padx=(0, 10), pady=(10, 0), side="left", expand=True)
                    rawTextEditor.insert("1.0", content)

                    # -- Frame for Todo Renderer --
                    renderer = tdRenderer.TodoRenderer(TDrenderFrame, content, path)
                    renderer.pack(expand=True, fill="both")
                    TDrenderFrame.pack(pady=0, padx=(0, 10), expand=True, fill="both", side="top")

                    renderer.tkraise()
                    todoEditorHandler.refreshAll(rawTextEditor, TDrenderFrame, path, sys.modules[__name__])
                    # ^ full ui initialization!

            button.configure(command=loadFileContent)
            button.pack(pady=5, padx=10, fill="x")
            print(f"Loaded file: {fileName}")

# ===== el funny discord rpc =====
def dcRPC(root, saver):
    RPCclientID = "1415709453898092692"
    RPCmanager = dcPresence.startRPC(RPCclientID)

    def closing():
        if RPCmanager:
            RPCmanager.stop()
        saver.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", closing)

# ===== cool funny keybinds =====
def bindKeybinds(widget, reloadList, updatePreview, saver, filePath=None):
    widget.unbind("<Control-s>")
    widget.unbind("<Control-S>")

    if not filePath or not filePath.endswith(".td"):
        widget.bind("<Control-s>", lambda event: saver.save())
        widget.bind("<Control-S>", lambda event: saver.save())

    widget.bind("<Control-n>", lambda event: NTDwindow.newFile(reloadList))
    widget.bind("<Control-N>", lambda event: NTDwindow.newFile(reloadList))
    widget.bind("<Control-q>", lambda event: widget.destroy())
    widget.bind("<Control-Q>", lambda event: widget.destroy())
    widget.bind("<Control-r>", lambda event: reloadList())
    widget.bind("<Control-R>", lambda event: reloadList())

# ===== refresh ui for theme! =====
def refreshUI(root):
    root.destroy()
    initializeUI()

    if getJson.getSetting("EnableDiscordRPC"):
        RPCclientID = "1415709453898092692"
        RPCmanager = dcPresence.startRPC(RPCclientID)
        if RPCmanager:
            RPCmanager.stop()
        root.destroy()
