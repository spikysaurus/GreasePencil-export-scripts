import bpy
import os
import zipfile
import xml.etree.ElementTree as ET
import shutil

# === CONFIG ===
output_path = bpy.path.abspath("//grease_to_openraster.ora")
DELETE_TEMP_FILES = True  # set to False if you want to keep temp files

# Temporary export directories
temp_dir = bpy.path.abspath("//ora_frames")
ora_temp = bpy.path.abspath("//ora_temp")
data_dir = os.path.join(ora_temp, "data")
thumb_dir = os.path.join(ora_temp, "Thumbnails")
os.makedirs(temp_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)
os.makedirs(thumb_dir, exist_ok=True)

gp = bpy.context.active_object
if gp is None or gp.type != 'GREASEPENCIL':
    raise RuntimeError("Select a Grease Pencil object before running.")

layer_images = {}

# === EXPORT ONLY KEYFRAMES PER GP LAYER ===
for layer in gp.data.layers:
    layer_images[layer.info] = []
    for frame in layer.frames:  # only actual GP keyframes
        f = frame.frame_number
        bpy.context.scene.frame_set(f)

        # Hide all other GP layers
        for l in gp.data.layers:
            l.hide = True
        layer.hide = False

        # Transparent background
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'

        filepath = os.path.join(temp_dir, f"{layer.info}_{f}.png")
        bpy.context.scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)  # full render
        if os.path.exists(filepath):
            layer_images[layer.info].append((f, filepath))

# === BUILD stack.xml ===
width = bpy.context.scene.render.resolution_x
height = bpy.context.scene.render.resolution_y

image_elem = ET.Element("image", attrib={
    "version": "0.0.3",
    "w": str(width),
    "h": str(height),
    "xres": "72",
    "yres": "72"
})

root_stack = ET.SubElement(image_elem, "stack")

# Each GP layer becomes a nested stack
for layer_name, frames in layer_images.items():
    group_stack = ET.SubElement(root_stack, "stack", attrib={
        "name": layer_name,
        "opacity": "1.0",
        "visibility": "visible"
    })
    for f, filepath in frames:
        dest = os.path.join(data_dir, f"{layer_name}_{f}.png")
        shutil.copy(filepath, dest)
        ET.SubElement(group_stack, "layer", attrib={
            "name": str(f),
            "src": f"data/{layer_name}_{f}.png",
            "x": "0",
            "y": "0",
            "opacity": "1.0",
            "visibility": "visible"
        })

# Write stack.xml
stack_xml_path = os.path.join(ora_temp, "stack.xml")
ET.ElementTree(image_elem).write(stack_xml_path, encoding="UTF-8", xml_declaration=True)

# === Thumbnail ===
first_frame = None
for frames in layer_images.values():
    for _, fp in frames:
        if os.path.exists(fp):
            first_frame = fp
            break
    if first_frame:
        break

thumb_out = os.path.join(thumb_dir, "thumbnail.png")
if first_frame:
    shutil.copy(first_frame, thumb_out)

# === mergedimage.png ===
merged_png_tmp = bpy.path.abspath("//ora_merged.png")
bpy.context.scene.render.filepath = merged_png_tmp
for l in gp.data.layers:
    l.hide = False
bpy.ops.render.render(write_still=True)
merged_out = os.path.join(ora_temp, "mergedimage.png")
if os.path.exists(merged_png_tmp):
    shutil.copy(merged_png_tmp, merged_out)

# === mimetype ===
mimetype_path = os.path.join(ora_temp, "mimetype")
with open(mimetype_path, "wb") as mf:
    mf.write(b"image/openraster")

# === ZIP INTO .ora ===
with zipfile.ZipFile(output_path, 'w') as zf:
    zf.write(mimetype_path, "mimetype", compress_type=zipfile.ZIP_STORED)
    if os.path.exists(stack_xml_path):
        zf.write(stack_xml_path, "stack.xml", compress_type=zipfile.ZIP_DEFLATED)
    if os.path.exists(merged_out):
        zf.write(merged_out, "mergedimage.png", compress_type=zipfile.ZIP_DEFLATED)
    for folder, _, files in os.walk(ora_temp):
        for file in files:
            full_path = os.path.join(folder, file)
            rel_path = os.path.relpath(full_path, ora_temp)
            if rel_path in ("mimetype", "stack.xml", "mergedimage.png"):
                continue
            zf.write(full_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)

print(f"Exported Grease Pencil keyframes to OpenRaster file: {output_path}")

# === CLEANUP OPTION ===
if DELETE_TEMP_FILES:
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(ora_temp):
            shutil.rmtree(ora_temp)
        if os.path.exists(merged_png_tmp):
            os.remove(merged_png_tmp)
        print("Temporary files deleted.")
    except Exception as e:
        print(f"Cleanup failed: {e}")
