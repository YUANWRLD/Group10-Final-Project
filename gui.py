import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model
import h5py
from UI import *

class ImagePredictionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("圖像預測工具")
        self.root.geometry("650x300")
        self.model = None

        # 模型路徑對應
        self.model_paths = {
            "3D": "3D_unet_model.keras",
            "Comic": "comic_unet_model.keras",
            "Beauty": "Beauty_unet_model.keras"
        }

        self.selected_model = tk.StringVar(value="3D")
        self.selected_folder = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="選擇模型：").grid(row=0, column=0, sticky=tk.W)
        ttk.Combobox(frame, textvariable=self.selected_model,
                     values=list(self.model_paths.keys()),
                     state="readonly").grid(row=0, column=1, sticky=tk.W)

        ttk.Label(frame, text="圖像資料夾 (3d, beauty, comic)：")\
            .grid(row=1, column=0, sticky=tk.W, pady=10)
        ttk.Entry(frame, textvariable=self.selected_folder, width=40)\
            .grid(row=1, column=1, sticky=tk.W)
        ttk.Button(frame, text="瀏覽", command=self._browse_folder)\
            .grid(row=1, column=2, sticky=tk.W)

        ttk.Button(frame, text="產生", command=self._run_prediction)\
            .grid(row=2, column=1, pady=20)

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)

    def _run_prediction(self):
        folder = self.selected_folder.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("錯誤", "請先選擇有效的資料夾！")
            return

        model_name = self.selected_model.get()
        model_file = self.model_paths[model_name]
        try:
            self.model = load_model(model_file)
        except Exception as e:
            messagebox.showerror("錯誤", f"載入模型失敗：{e}")
            return

        # 把 output 資料夾放在程式執行路徑下
        base_dir = os.getcwd()
        out_dir = os.path.join(base_dir, f"output({model_name.lower()})")
        os.makedirs(out_dir, exist_ok=True)

        # 讀取模型輸入尺寸 (NHWC)
        _, h, w, _ = self.model.input_shape
        for fname in os.listdir(folder):
            if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            try:
                img = Image.open(os.path.join(folder, fname)).convert("RGB")
                img_resized = img.resize((w, h))
                x = np.expand_dims(np.array(img_resized)/255.0, axis=0)

                y = self.model.predict(x)[0]
                y_img = Image.fromarray((y*255).astype(np.uint8))\
                              .resize(img.size)
                y_img.save(os.path.join(out_dir, fname))
            except Exception as e:
                print(f"處理 {fname} 失敗：{e}")

        messagebox.showinfo("完成", f"預測完成，結果儲存在：\n{out_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ui(root) #ImagePredictionGUI(root)
    root.mainloop()
