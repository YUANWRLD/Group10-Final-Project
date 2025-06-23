import flet as ft
from flet import AlertDialog, FilePicker, FilePickerResultEvent, Image, ElevatedButton, Dropdown, Row, Column, Text, alignment, Container
import uuid

def main(page: ft.Page):
    page.title = "Image Generator APP"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.padding = 20     

    # 狀態變數
    has_selection = False
    has_upload = False
    has_generate = False
    upload_image = None
    generated_image = None

    # 選擇欄
    selection = ft.Dropdown(
        width=525,
        options=[
            ft.dropdown.Option(text="--請選擇--", disabled=True),
            ft.dropdown.Option("Beauty Filter Style"),
            ft.dropdown.Option("Comic (Western Cartoon) Style"),
            ft.dropdown.Option("3D Rendered Cartoon Style"),
        ],
        value="",
        autofocus=True,
        hint_text="--請選擇--"
    )

    # 上傳區（預設顯示文字）
    upload_text = ft.Text("上傳區", size=16, color="grey")
    upload_container = ft.Container(
        content=upload_text,
        width=250,
        height=250,
        border=ft.border.all(1, "black"),
        alignment=alignment.center,
    )

    # 生成區（預設顯示文字）
    generated_text = ft.Text("生成圖片區", size=16, color="grey")
    generated_container = ft.Container(
        content=generated_text,
        width=250,
        height=250,
        border=ft.border.all(1, "black"),
        alignment=alignment.center,
    )

    # 按鈕（生成按鈕初始disabled）
    upload_btn = ElevatedButton(text="上傳圖片", width=120)
    generate_btn = ElevatedButton(text="生成圖片", width=120, disabled=True)
    save_btn = ElevatedButton(text="保存圖片", width=260, disabled=True)

    # 更新生成按鈕狀態
    def update_generate_btn():
        generate_btn.disabled = not (has_selection and has_upload)
        page.update()
    
    # 更新保存按鈕狀態
    def update_save_btn():
        save_btn.disabled = not (has_generate)
        page.update()

    # 選擇欄改變事件
    def selection_changed(e):
        nonlocal has_selection
        #has_selection = bool(e.control.value)
        if e.control.value == '--請選擇--':
            has_selection = False
        else:
            has_selection = True
        print(has_selection)
        print(selection.value)
        update_generate_btn()

    selection.on_change = selection_changed

    # 重置
    def reset_gen_img():
        nonlocal generated_image
        generated_image = None
        generated_container.content = ft.Text("生成圖片區", size=16, color="grey")

    def reset_up_img():
        nonlocal upload_image
        upload_image = None
        upload_container.content = ft.Text("上傳區", size=16, color="grey")
        
    # FilePicker回調
    def on_file_picked(e: FilePickerResultEvent):
        nonlocal selection, upload_image, generated_image, has_upload, has_selection, has_generate, common_dialog
        if e.files:
            f = e.files[0]
            ext = f.name.lower().split(".")[-1]
            if ext not in ("jpg", "jpeg", "png"):
                # 顯示對話框
                show_dialog("格式錯誤", "只能上傳 jpg、jpeg、png 格式的圖片。")

                reset_up_img()
                reset_gen_img()
                has_upload = False
                selection.value = "--請選擇--"
                #has_selection = False
                class DummyEvent:
                    def __init__(self, control):
                        self.control = control

                dummy_event = DummyEvent(selection)
                selection_changed(dummy_event)

                update_generate_btn()
                has_generate = False
                update_save_btn()
                page.update()
                return
            if upload_image == None:
                upload_image = Image(src=f.path, width=250, height=250, fit="contain")
                upload_container.content = upload_image
                has_upload = True
                update_generate_btn()
                update_save_btn()
                page.update()
            else:
                reset_up_img()
                reset_gen_img()
                has_upload = False
                selection.value = "--請選擇--"
                #has_selection = False
                class DummyEvent:
                    def __init__(self, control):
                        self.control = control

                dummy_event = DummyEvent(selection)
                selection_changed(dummy_event)

                update_generate_btn()
                has_generate = False
                update_save_btn()
                upload_image = Image(src=f.path, width=250, height=250, fit="contain")
                upload_container.content = upload_image
                has_upload = True
                page.update()


    # 上傳按鈕點擊
    def upload_clicked(e):
        file_picker.pick_files(allow_multiple=False)

    # 生成圖片函式
    def generate_image():
        nonlocal has_generate
        '''
        time.sleep(10) # simulate processing
        TODO:
        1. load model / image
        2. image preprocess
        3. generate style image accoring to style --> style is selection.value
        4. save image
        '''
        import os
        img_path = "demo.jpg" # it should be generated image path
        if os.path.exists(img_path):
            return Image(src=img_path, width=250, height=250, fit="contain") # display generated iamge
        
        #else:
        #    return ft.Text("未找到生成圖片", color="red")

    # 生成按鈕點擊
    def generate_clicked(e):
        nonlocal generated_image, has_generate

        # all components need to be freezed during generating image
        upload_btn.disabled = True
        selection.disabled = True
        generate_btn.disabled = True
        save_btn.disabled = True
        page.update()

        generated_image = generate_image()
        generated_container.content = generated_image

        # restore state of components
        upload_btn.disabled = False
        selection.disabled = False

        has_generate = True
        update_save_btn()
        page.update()

    # 保存按鈕點擊
    def save_clicked(e):
        nonlocal has_upload, has_selection, has_generate
        if generated_image is None or not isinstance(generated_image, Image):
            show_dialog("Error", "圖片丟失，請重試。")
            return

        try:
            src = generated_image.src
            import shutil
            uuid_str = uuid.uuid4().hex
            
            save_path = f"{uuid_str}.jpg"
            shutil.copyfile(src, save_path)
            # 顯示對話框
            show_dialog("保存成功", "圖片成功保存。")

            reset_up_img()
            reset_gen_img()
            has_upload = False
            selection.value = "--請選擇--"
            #has_selection = False
            class DummyEvent:
                def __init__(self, control):
                    self.control = control

            dummy_event = DummyEvent(selection)
            selection_changed(dummy_event)
            
            update_generate_btn()
            has_generate = False
            update_save_btn()
            page.update()
        except Exception as ex:
            show_dialog("保存失敗", "保存圖片時發生錯誤，請重試。")

            reset_up_img()
            reset_gen_img()
            has_upload = False
            selection.value = "--請選擇--"
            #has_selection = False
            class DummyEvent:
                def __init__(self, control):
                    self.control = control

            dummy_event = DummyEvent(selection)
            selection_changed(dummy_event)

            update_generate_btn()
            has_generate = False
            update_save_btn()
            page.update()

    # FilePicker物件
    file_picker = FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    upload_btn.on_click = upload_clicked
    generate_btn.on_click = generate_clicked
    save_btn.on_click = save_clicked

    common_dialog = ft.AlertDialog(
        title=ft.Text(""),
        content=ft.Text(""),
        actions=[
            ft.TextButton("確定", on_click=lambda e: close_dialog())
        ],
        actions_alignment="end",
    )

    # 指定為 page 對話框
    page.dialog = common_dialog

    # 關閉對話框函式
    def close_dialog():
        common_dialog.open = False
        page.update()

    # 彈出對話框函式
    def show_dialog(title: str, message: str):
        common_dialog.title.value = title
        common_dialog.content.value = message
        common_dialog.open = True
        page.update()

    def get_border_color():
        return "white" if page.theme_mode == ft.ThemeMode.DARK else "black"
    
    # 切換日夜模式
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
        upload_container.border = ft.border.all(1, get_border_color())
        generated_container.border = ft.border.all(1, get_border_color())
        selection.border_color = get_border_color()
        page.update()

    page.appbar = ft.AppBar(
        title=ft.Text(""),
        actions=[
            ft.IconButton(
                icon= "dark_mode", #ft.Icons.DARK_MODE,
                on_click=toggle_theme,
                tooltip="切換日夜模式"
            )
        ],
    )

    # 預設主題
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme()

    # 佈局
    page.add(
        Column(
            [
                common_dialog,
                Row(
                    [selection],
                    alignment="center",
                    
                ),
                ft.Container(height=20),
                Row(
                    [upload_container, generated_container],
                    alignment="center",
                    spacing=30,
                ),
                ft.Container(height=20),
                Row(
                    [upload_btn, generate_btn],
                    alignment="center",
                    spacing=150,
                ),
                ft.Container(height=20),
                Row(
                    [save_btn],
                    alignment="center",
                )
            ],
            alignment="center",
            spacing=10,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)

