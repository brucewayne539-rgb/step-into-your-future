from pathlib import Path
import os, json

def config_file():
    base = os.environ.get("LOCALAPPDATA")
    if base:
        folder = Path(base) / "StepIntoYourFuture"
    else:
        folder = Path.home() / ".step_into_your_future"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "config.json"

try:
    import tkinter as tk
    from tkinter import simpledialog, messagebox
    root = tk.Tk()
    root.withdraw()
    key = simpledialog.askstring("STEP INTO YOUR FUTURE — TODAY!", "Paste your OpenAI API key:", show="*", parent=root)
    key = (key or "").strip()
    if not key.startswith("sk-"):
        messagebox.showerror("API key not saved", "That does not look like an OpenAI API key.")
    else:
        config_file().write_text(json.dumps({"openai_api_key": key}, indent=2), encoding="utf-8")
        messagebox.showinfo("Setup complete", "API key saved safely in your local Windows profile. You can now run START_APP.bat.")
    root.destroy()
except Exception as e:
    print("Could not open the setup window:", e)
    input("Press Enter to close...")
