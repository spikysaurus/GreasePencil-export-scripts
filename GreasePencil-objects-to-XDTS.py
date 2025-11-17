import bpy
import json
import os

    # WORKS FOR BLENDER v4.5
    # Scans all Grease Pencils object's bottom layers
    # Exported in "export" folder in the same path as your .blend file
    # Limitations : - No Camera Data export - No Instanced Drawing/Duplicate Cell Number

GPData = "A,B,C" #Grease Pencil oject's name

header = "" 
layers = GPData.split(',');
layers_id = []

dict = {}
duration = bpy.context.scene.frame_end # total duration (frames)
fieldIds = [0,3,5]

_tracks = {}
_trackNo = layers_id
timetables_data = []
        
for i in enumerate(layers):
    layers_id.append(i[0])

dict["header"] = {"cut":0,"scene":0}
dict["timeTables"] = []

_df = {"duration":duration}
dict["timeTables"].append(_df)

_fields = []
_df["fields"] = _fields

_ft = {"fieldId":fieldIds[0]}
_fields.append(_ft)

_tracks = []
_ft["tracks"]= _tracks

_tf={}
frames_list= []
gg = -1
for l in layers:
    gg += 1
    for g in bpy.data.grease_pencils_v3:
        if g.name == str(l):
            _tf = {"trackNo":int(gg)}
            _tf["frames"] = []
            _tracks.append(_tf)
            tt = 0
            k = {str(g.name) : []}
            frames_list.append(k)
            for e in g.layers[0].frames:
                
                if e.keyframe_type == "KEYFRAME":
                    tt += 1
                    _frames = { "data": [{ "id": 0,"values": [str(tt)] }]}
                    
                elif e.keyframe_type == "BREAKDOWN":
                    _frames = { "data": [{ "id": 0,"values": ["SYMBOL_TICK_1"] }]}
                    
                elif e.keyframe_type == "JITTER":
                    _frames = { "data": [{ "id": 0,"values": ["SYMBOL_TICK_2"] }]}
                    
                elif e.keyframe_type == "MOVING_HOLD":
                    _frames = { "data": [{ "id": 0,"values": ["SYMBOL_HYPHEN"] }]}
                    
                elif e.keyframe_type == "EXTREME":
                    _frames = { "data": [{ "id": 0,"values": ["SYMBOL_NULL_CELL"] }]}
                
                kk = e.frame_number
                _frames["frame"] = int(kk) - 1
                _tf["frames"].append(_frames)
        
            _frames = { "data": [{ "id": 0,"values": ["SYMBOL_NULL_CELL"] }]}    
            _frames["frame"] = bpy.context.scene.frame_end
            _tf["frames"].append(_frames)
    
_df["name"] = header
_df["timeTableHeaders"] = []

_fn = {"fieldId":0}

_fn["names"] = layers
_df["timeTableHeaders"].append(_fn)
dict["version"] = 5
js = json.dumps(dict)


filename = "Timesheet"
filepath = "//"
abs_filepath = bpy.path.abspath(filepath) # returns the absolute path
if not os.path.isdir(str(abs_filepath+"export")): # checks whether the directory exists
    os.mkdir(str(abs_filepath+"export")) # if it does not yet exist, makes it
    
    
fp = open(bpy.path.abspath("//"+"export/"+str(filename)+".xdts"), 'w')
fp.write("exchangeDigitalTimeSheet Save Data"+js)
fp.close()
