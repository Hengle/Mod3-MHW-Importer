# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 00:14:32 2019

@author: AsteriskAmpersand
"""

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import EnumProperty, BoolProperty, StringProperty
from bpy.types import Operator

from ..mod3 import Mod3ExporterLayer as Mod3EL
from ..blender import BlenderMod3Exporter as Api

class Context():
    def __init__(self, path, meshes, armature):
        self.path = path

class ExportMOD3(Operator, ExportHelper):
    bl_idname = "custom_export.export_mhw_mod3"
    bl_label = "Save MHW MOD3 file (.mod3)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
 
    # ImportHelper mixin class uses this
    filename_ext = ".mod3"
    filter_glob = StringProperty(default="*.mod3", options={'HIDDEN'}, maxlen=255)

    split_normals = BoolProperty(
        name = "Use Custom Normals",
        description = "Use split/custom normals instead of Blender autogenerated normals.",
        default = True)
    highest_lod = BoolProperty(
        name = "Set Meshparts to Highest LOD",
        description = "Overwrites all meshparts' explicit LODs to the highest LOD.",
        default = True)
    coerce_fourth = BoolProperty(
        name = "Coerce 4th Negative Weight",
        description = "Forces non-explicit 4 weight vertices into a 4 weight blocktype.",
        default = True)
    
    errorItems = [("Ignore","Ignore","Will not log warnings. Catastrophical errors will still break the process.",0),
                  ("Warning","Warning","Will be logged as a warning. This are displayed in the console. (Window > Toggle_System_Console)",1),
                  ("Error","Error","Will stop the exporting process. An error will be displayed and the log will show details. (Window > Toggle_System_Console)",2),
                  ]
    levelProperties = ["propertyLevel","blocktypeLevel","loopLevel","uvLevel","colourLevel","weightLevel","weightCountLevel","facesLevel"]
    levelNames = ["Property Error Level", "Blocktype Error Level", "Loops Error Level", "UV Error Level", "Colour Error Level", "Weighting Error Level", "Weight Count Error Level", "Faces Error Level"]
    levelDescription = ["Missing and Duplicated Header Properties",
                        "Conflicting Blocktype Declarations",
                        "Redundant, Mismatched and Missing Normals",
                        "UV Map Incompatibilities",
                        "Colour Map Incompatibilities",
                        "Vertex Weight Groups Irregularities",
                        "Weight Count Errors",
                        "Non Triangular Faces"]
    levelDefaults = ["Warning","Error","Ignore","Error","Ignore","Warning","Warning","Error"]
    propString = """EnumProperty(
                    name = name,
                    description = desc,
                    items = errorItems,
                    default = pred,                
                    )"""
    for prop,name,desc,pred in zip(levelProperties, levelNames, levelDescription, levelDefaults):
        exec("%s = %s"%(prop, propString))

    def execute(self,context):
        BApi = Api.BlenderExporterAPI()
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            obj.select = obj.type == "MESH"
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.select_all(action='DESELECT')
            
        options = self.parseOptions()
        Mod3EL.ModelToMod3(BApi, options).execute(self.properties.filepath)
        bpy.ops.object.select_all(action='DESELECT')
        #bpy.ops.object.mode_set(mode='OBJECT')
        #bpy.context.area.type = 'INFO'
        return {'FINISHED'}
    
    def parseOptions(self):
        options = {
                "lod":self.highest_lod,
                "levels":{prop:self.__getattribute__(prop) for prop in self.levelProperties},
                "splitnormals":self.split_normals,
                "coerce":self.coerce_fourth,
                }        
        return options
    
def menu_func_export(self, context):
    self.layout.operator(ExportMOD3.bl_idname, text="MHW MOD3 (.mod3)")