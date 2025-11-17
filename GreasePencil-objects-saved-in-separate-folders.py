import bpy,os

#Works in Blender v4.5

GPData = "A,B,C" #Name of Grease Pencil Objects
str_filename = "Counting Numbers" #Image keyframes naming

filepath = "//"
abs_filepath = bpy.path.abspath(filepath) # returns the absolute path
if not os.path.isdir(str(abs_filepath+"export")): # checks whether the directory exists
    os.mkdir(str(abs_filepath+"export")) # if it does not yet exist, makes it
    
layers = GPData.split(',');

for l in layers:
    
    for a in bpy.data.objects:
        for b in layers:    
            bpy.data.objects[str(b)].hide_render = True
        
        
        bpy.data.objects[str(l)].hide_render = False
        print(bpy.data.objects[str(a.name)].name,' = ',bpy.data.objects[str(a.name)].hide_render)
        
        
        
        scene = bpy.context.scene
        
        if str_filename == 'Counting Numbers' or str_filename == 'Frame Numbers' :
            filename = ''
        elif str_filename == 'Layer name + Counting Numbers' or str_filename == 'Layer name + Frame Numbers' : 
            filename = str(l)
            
            
        fp = abs_filepath+"export"+"/"+str(l)+"/"+filename  # Get existing output path
        
        frmt = scene.render.image_settings.file_format
        scene.render.image_settings.file_format = frmt #PNG
        if scene.render.film_transparent == True:
            scene.render.image_settings.color_mode = 'RGBA'
        else:
            scene.render.image_settings.color_mode = 'RGB'
            
    for b in bpy.data.objects:  
        frames = [] 
        obj = bpy.data.objects[str(b.name)]
        
        if obj.type == 'GREASEPENCIL':
            
        #    print(obj.data.layers.active)
            for i in obj.data.layers.active.frames:
                
                path = bpy.context.blend_data.filepath
                frames.append(int(i.frame_number))
            if obj.hide_render == False:
                print(frames)
                filename_number = 0
                
                for frame_nr in frames:
                    if not os.path.isdir(str(abs_filepath+"export"+"/"+str(l))): # checks whether the directory exists
                        os.mkdir(str(abs_filepath+"export"+"/"+str(l))) # if it does not yet exist, makes it
                        
                    scene.frame_set(frame_nr)  # Set current frame to the desired frame

                    if str_filename == 'Counting Numbers':
                        filename_number += 1
                        scene.render.filepath = abs_filepath+"export"+"/"+str(l)+"/"+str(filename_number)
                        
                    elif str_filename == 'Layer name + Counting Numbers':
                        filename_number += 1
                        scene.render.filepath = fp + "_" + str(filename_number).zfill(4)
                        
                    elif str_filename == 'Frame Numbers':
                        scene.render.filepath = abs_filepath+"export"+"/"+str(l)+"/"+str(frame_nr)
                        
                    elif str_filename == 'Layer name + Frame Numbers':
                        scene.render.filepath = fp + "_" + str(frame_nr).zfill(4)
                    
                    bpy.ops.render.render(write_still=True)  # Render still image

                # Restore the original filepath
                scene.render.filepath = fp

            else:
                pass
            
    print('----')
    
    

