from fastapi.responses import StreamingResponse
from nicegui.events import KeyEventArguments
from nicegui import Client, app, ui
import python_avatars as pa
from random import choice
from typing import List
from io import BytesIO
import os

def get_attrs(obj):
    return [attr for attr in dir(obj) if str(attr) == str(attr).upper()]

@ui.page("/download")
def download():
    buffer = BytesIO(initial_bytes=app.storage.user["avatar"].encode())
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/svg", headers={'Content-Disposition': 'attachment; filename="avatar.svg"'})

@ui.page("/")
def index():
    app.storage.user["avatar"] = "<pre>Avatar goes here as soon as you do some configuration</pre>"
    if not "dark" in app.storage.user:
        app.storage.user["dark"] = False
    def update_avatar():
        avatar = pa.Avatar(
            style=pa.AvatarStyle[style.value],
            background_color=pa.BackgroundColor[background_color.value],
            top=pa.HairType[top.value],
            eyebrows=pa.EyebrowType[eyebrows.value],
            eyes=pa.EyeType[eyes.value],
            nose=pa.NoseType[nose.value],
            mouth=pa.MouthType[mouth.value],
            facial_hair=pa.FacialHairType[facial_hair.value],
            skin_color=pa.SkinColor[skin_color.value],
            hair_color=pa.HairColor[hair_color.value],
            accessory=pa.AccessoryType[accessory.value],
            clothing=pa.ClothingType[clothing.value],
            clothing_color=pa.ClothingColor[clothing_color.value],
            shirt_graphic=pa.ClothingGraphic[shirt_graphic.value],
            # hat_color=pa.HatType[hat_type.value],
            shirt_text=shirt_text.value,
        )
        data = avatar.render()
        app.storage.user["avatar"] = avatar.render()

    def random_avatar():
        for obj in [style, background_color, top, eyebrows, eyes, nose, mouth, facial_hair, skin_color, hair_color, accessory, clothing, clothing_color, shirt_graphic]:
            obj.value = choice(obj.options)
        
        if shirt_graphic.value == "CUSTOM_TEXT":
            clothing.value = "GRAPHIC_SHIRT"
        if clothing.value == "GRAPHIC_SHIRT" and shirt_graphic.value == "CUSTOM_TEXT":
            shirt_text.value = choice(["r00t", "sud0", "us3r", "l33t", "y0l0", "0x00", "c0d3", "h4ck", "lgbz", "k3ys", "qu33r"])
        
    def enable_custom_text():
        clothing.value = "GRAPHIC_SHIRT"
        shirt_graphic.value = "CUSTOM_TEXT"
    
    def random_text():
        shirt_text.value = choice(["r00t", "sud0", "us3r", "l33t", "y0l0", "0x00", "c0d3", "h4ck", "lgbz", "k3ys", "qu33r"])
    
    def toggle_mode():
        if dark.value:
            dark.disable()
        else:
            dark.enable()
    
    def copy_svg():
        ui.run_javascript(f'navigator.clipboard.writeText(`{app.storage.user["avatar"]}`)')
        ui.notify(message="SVG copied to clipboard", type="info")

    class cSelect(ui.select):
        def __init__(self, target: any):
            options = get_attrs(target)
            label = f"Choose {target.__name__}"
            super().__init__(label=label, options=options, on_change=update_avatar, value=choice(options))
    
    def handle_key(e: KeyEventArguments):
        if e.key == 'r' and not e.action.repeat and e.action.keydown:
            random_avatar()
        elif e.key == 'd' and not e.action.repeat and e.action.keydown:
            ui.open("/download")
        elif e.key == 'm' and not e.action.repeat and e.action.keydown:
            toggle_mode()
        elif e.key == 'c' and not e.action.repeat and e.action.keydown:
            copy_svg()

    keyboard = ui.keyboard(on_key=handle_key)
    dark = ui.dark_mode()
    with ui.card().classes("w-10/12 ml-auto mr-auto"):
        ui.markdown(content="This page is using [python_avatars](https://github.com/ibonn/python_avatars) to generate cool avatars. Press `r` to generate a random one. Press `d` to download your avatar as svg. Or just press the below buttons. To have some custom text written on the tee, you need to set ClothingType to `GRAPHIC_SHIRT` and ClothingGraphic to `CUSTOM_TEXT`. Or press the green button to automatically set these fields. Darkmode can be enabled pressing `m` or the designated button in the top right corner. You can also copy the SVG by pressing the correct button or `c` on your keyboard. Have fun.")
    with ui.row().classes("w-full justify-center"):
        with ui.element("div").classes("w-5/12"):
            ui.label("Configure Avatar").classes("text-2xl")
            with ui.grid(columns=2).classes("w-full"):
                style = cSelect(target=pa.AvatarStyle)
                background_color = cSelect(target=pa.BackgroundColor)
                top = cSelect(target=pa.HairType)
                # hat_type = cSelect(target=pa.HatType).bind_visibility_from(target_object=top, target_name="value", value="HAT")
                hair_color = cSelect(target=pa.HairColor)
                facial_hair = cSelect(target=pa.FacialHairType)
                eyebrows = cSelect(target=pa.EyebrowType)
                eyes = cSelect(target=pa.EyeType)
                nose = cSelect(target=pa.NoseType)
                mouth = cSelect(target=pa.MouthType)
                skin_color = cSelect(target=pa.SkinColor)
                accessory = cSelect(target=pa.AccessoryType)
                clothing = cSelect(target=pa.ClothingType)
                clothing_color = cSelect(target=pa.ClothingColor)
                shirt_graphic = cSelect(target=pa.ClothingGraphic)
                with ui.input(label="Shirt text", on_change=update_avatar).bind_visibility_from(target_object=shirt_graphic, target_name="value", value="CUSTOM_TEXT") as shirt_text:
                    ui.tooltip("ClothingType must be \"GRAPHIC_SHIRT\" to make this work.\nClothingGraphic must be \"CUSTOM_TEXT\".")
                
            with ui.grid(columns=2).classes("w-full mt-4"):
                ui.button("Custom Text", icon="format_size", on_click=enable_custom_text, color="green")
                ui.button("Random Text", icon="shuffle", on_click=random_text, color="green")
                ui.button("Random Avatar (r)", icon="shuffle", on_click=random_avatar)
                ui.button("Download SVG (d)", icon="file_download", on_click=lambda: ui.open("/download"))
                ui.button("Copy SVG (c)", icon="content_copy", on_click=copy_svg, color="purple")

        with ui.element("div").classes("w-5/12") as preview:
            ui.label("Avatar").classes("text-2xl")
            svg = ui.html().classes("self-center").bind_content_from(target_object=app.storage.user, target_name="avatar")
    
    with ui.page_sticky(position="top-right").classes("p-4"):
        ui.button(icon="light_mode", on_click=toggle_mode).props("dense flat")


if __name__ in ("__main__", "__mp_main__"):
    ui.run(
        title="Avatar Generator",
        storage_secret=os.urandom(128),
        dark=False
    )