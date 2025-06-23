import os
import uuid
import shutil
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model

import flet as ft
from flet import (
    FilePicker,
    FilePickerResultEvent,
    Image as FletImage,
    Dropdown,
    ElevatedButton,
    Row,
    Column,
    Container,
    Text,
    AlertDialog,
    TextButton,
    alignment,
    border,
)


class ImagePredictionApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Image Generator APP"
        self.page.horizontal_alignment = "center"
        self.page.vertical_alignment = "center"
        self.page.padding = 20

        self.model_paths = {
            "3D Rendered Cartoon Style": "3D_unet_model.keras",
            "Comic (Western Cartoon) Style": "comic_unet_model.keras",
            "Beauty Filter Style": "Beauty_unet_model.keras",
        }

        self.model = None
        self.upload_image: FletImage | None = None
        self.generated_image: FletImage | None = None
        self.preview_image_path: str | None = None
        self.output_folder: str | None = None

        self.has_selection = False
        self.has_upload = False
        self.has_generate = False
        self.has_outdir = False

        self._build_ui()

    def _build_ui(self):
        self.selection = Dropdown(
            width=525,
            options=[ft.dropdown.Option(text="--請選擇--", disabled=True)] + [ft.dropdown.Option(k) for k in self.model_paths],
            value="",
            autofocus=True,
            hint_text="--請選擇--",
        )
        self.selection.on_change = self._on_model_changed

        self.output_dir_text = Text("輸出資料夾未設定", size=14, color="grey")
        self.output_dir_container = Container(
            content=self.output_dir_text,
            width=250,
            height=40,
            border=border.all(1, "black"),
            alignment=alignment.center_left,
            padding=8,
        )
        self.choose_outdir_btn = ElevatedButton("選擇輸出資料夾", on_click=self._pick_output_dir)

        self.upload_container = self._placeholder_box("上傳區")
        self.generated_container = self._placeholder_box("生成圖片區")

        self.upload_btn = ElevatedButton("上傳圖片", width=120, on_click=self._upload_clicked)
        self.generate_btn = ElevatedButton("生成圖片", width=120, on_click=self._generate_clicked, disabled=True)
        self.save_btn = ElevatedButton("保存圖片", width=260, on_click=self._save_clicked, disabled=True)

        self.file_picker_img = FilePicker(on_result=self._on_file_picked)
        self.file_picker_out = FilePicker(on_result=self._on_outdir_picked)
        self.page.overlay.extend([self.file_picker_img, self.file_picker_out])

        self.dialog = AlertDialog(
            title=Text(""),
            content=Text(""),
            actions=[TextButton("確定", on_click=lambda _: self._close_dialog())],
            actions_alignment="end",
        )
        self.page.dialog = self.dialog

        self.page.appbar = ft.AppBar(
            title=Text(""),
            actions=[ft.IconButton(icon="dark_mode", on_click=self._toggle_theme, tooltip="切換日夜模式")],
        )
        self.page.theme_mode = ft.ThemeMode.LIGHT

        self.page.add(
            Column(
                [
                    Row([self.selection], alignment="center"),
                    Container(height=15),
                    Row([self.output_dir_container, self.choose_outdir_btn], alignment="center", spacing=10),
                    Container(height=20),
                    Row([self.upload_container, self.generated_container], alignment="center", spacing=30),
                    Container(height=20),
                    Row([self.upload_btn, self.generate_btn], alignment="center", spacing=150),
                    Container(height=20),
                    Row([self.save_btn], alignment="center"),
                ],
                alignment="center",
                spacing=10,
            )
        )

    def _placeholder_box(self, text: str):
        return Container(
            content=Text(text, size=16, color="grey"),
            width=250,
            height=250,
            border=border.all(1, "black"),
            alignment=alignment.center,
        )

    def _toggle_theme(self, _):
        self.page.theme_mode = ft.ThemeMode.DARK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        self.page.update()

    def _on_model_changed(self, e):
        self.has_selection = e.control.value not in ("", "--請選擇--")
        self._update_control_states()

    def _pick_output_dir(self, _):
        self.file_picker_out.get_directory_path(dialog_title="選擇輸出資料夾")

    def _on_outdir_picked(self, e: FilePickerResultEvent):
        if e.path:
            self.output_folder = e.path
            self.output_dir_container.content = Text(self.output_folder, size=14)
            self.has_outdir = True
        else:
            self.output_folder = None
            self.output_dir_container.content = Text("輸出資料夾未設定", size=14, color="grey")
            self.has_outdir = False
        self._update_control_states()
        self.page.update()

    def _upload_clicked(self, _):
        self.file_picker_img.pick_files(allow_multiple=False)

    def _on_file_picked(self, e: FilePickerResultEvent):
        if e.files:
            f = e.files[0]
            if not f.name.lower().endswith(("jpg", "jpeg", "png")):
                self._show_dialog("格式錯誤", "只能上傳 jpg、jpeg、png 格式的圖片。")
                return
            self.upload_image = FletImage(src=f.path, width=250, height=250, fit="contain")
            self.upload_container.content = self.upload_image
            self.has_upload = True
            self.generated_container.content = Text("生成圖片區", size=16, color="grey")
            self.generated_image = None
            self.preview_image_path = None
            self.has_generate = False
        else:
            self.has_upload = False
        self._update_control_states()
        self.page.update()

    def _generate_clicked(self, _):
        if not (self.has_selection and self.has_upload and self.has_outdir):
            return

        model_name = self.selection.value
        model_file = self.model_paths[model_name]
        if not os.path.exists(model_file):
            self._show_dialog("錯誤", f"找不到模型檔案：{model_file}")
            return

        try:
            self.model = load_model(model_file)
        except Exception as ex:
            self._show_dialog("載入錯誤", str(ex))
            return

        img_path = self.upload_image.src
        img = Image.open(img_path).convert("RGB")
        _, h, w, _ = self.model.input_shape
        x = np.expand_dims(np.array(img.resize((w, h))) / 255.0, axis=0)
        y = self.model.predict(x, verbose=0)[0]
        y_img = Image.fromarray((y * 255).astype(np.uint8)).resize(img.size)

        preview_name = f"preview_{uuid.uuid4().hex}.jpg"
        self.preview_image_path = os.path.join(self.output_folder, preview_name)
        y_img.save(self.preview_image_path)

        self.generated_image = FletImage(src=self.preview_image_path, width=250, height=250, fit="contain")
        self.generated_container.content = self.generated_image
        self.has_generate = True
        self._update_control_states()
        self.page.update()

    def _save_clicked(self, _):
        if not self.preview_image_path or not os.path.exists(self.preview_image_path):
            self._show_dialog("錯誤", "無生成圖片可儲存。")
            return
        try:
            target_name = f"generated_{uuid.uuid4().hex}.jpg"
            final_path = os.path.join(self.output_folder, target_name)
            shutil.move(self.preview_image_path, final_path)
            self._show_dialog("成功", f"圖片已保存至 {final_path}")
            self.preview_image_path = None
            self._reset_state()
        except Exception as ex:
            self._show_dialog("保存錯誤", str(ex))

    def _update_control_states(self):
        self.generate_btn.disabled = not (self.has_selection and self.has_upload and self.has_outdir)
        self.save_btn.disabled = not self.has_generate
        self.page.update()

    def _reset_state(self):
        if self.preview_image_path and os.path.exists(self.preview_image_path):
            os.remove(self.preview_image_path)
        self.upload_container.content = Text("上傳區", size=16, color="grey")
        self.generated_container.content = Text("生成圖片區", size=16, color="grey")
        self.upload_image = None
        self.generated_image = None
        self.preview_image_path = None
        self.has_upload = False
        self.has_generate = False
        self._update_control_states()

    def _show_dialog(self, title: str, msg: str):
        self.dialog.title.value = title
        self.dialog.content.value = msg
        self.dialog.open = True
        self.page.update()

    def _close_dialog(self):
        self.dialog.open = False
        self.page.update()


if __name__ == "__main__":
    ft.app(target=ImagePredictionApp)
