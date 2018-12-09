#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

# <pep8 compliant>
bl_info = {
    "name": "Cork on Blender",
    "author": "Dalai Felinto, Cicero Moraes and Everton da Rosa",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Tool Shelf",
    "description": "Interface to use Cork library for advanced boolean operations",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"}


import bpy
import bpy
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        StringProperty,
        )

from bpy.types import (
        Operator,
        Panel,
        )

from bpy_extras.io_utils import (
        ImportHelper,
        )

import bmesh

from .exceptions import *

from .lib import (
        get_cork_filepath,
        validate_executable,
        )

from .cork import (
        slice_out,
        )

# Preferences
class CorkMeshSlicerPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    cork_filepath: StringProperty(
        name="Cork Executable",
        description="Location of cork binary file",
        subtype="FILE_PATH",
        default="",
        )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "cork_filepath")

# ############################################################
# User Interface
# ############################################################

class CorkMeshSlicerPanel(Panel):
    bl_label = "Cork Mesh Slice"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Boolean'

    @staticmethod
    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.operator("view3d.cork_mesh_union", text="Union")
        col.operator("view3d.cork_mesh_difference", text="Difference")
        col.operator("view3d.cork_mesh_intersect", text="Intersect")
        col.operator("view3d.cork_mesh_xor", text="XOR")
        col.operator("view3d.cork_mesh_resolve", text="Resolve")
        col.separator()
        col.operator("view3d.cork_mesh_help", text="", icon='QUESTION', emboss=False).show_help = True


# ############################################################
# Operators
# ############################################################
def check_errors(objects):
    """"""
    if len(objects) != 2:
       raise NumberSelectionException

    for obj in objects:
       if obj.type != 'MESH':
          raise NonMeshSelectedException(obj)

def help_draw(_self, context):
    layout = _self.layout
    col = layout.column()

    col.label(text="This operator works from the selected to the active objects")
    col.label(text="The active must be a single plane")

    col.separator()
    col.label(text="Union")
    col.label(text="Compute the Boolean union of in0 and in1, and output the result")

    col.separator()
    col.label(text="Difference")
    col.label(text="Compute the Boolean difference of in0 and in1, and output the result")

    col.separator()
    col.label(text="Intersect")
    col.label(text="Compute the Boolean intersection of in0 and in1, and output the result")

    col.separator()
    col.label(text="XOR")
    col.label(text="Compute the Boolean XOR of in0 and in1, and output the result")

    col.separator()
    col.label(text="Resolve")
    col.label(text="Intersect the two meshes in0 and in1, and output the connected mesh with those")
    col.label(text="intersections made explicit and connected")

class CorkMeshBooleanUnion(Operator):
    """Cork boolean union operation"""
    bl_idname = "view3d.cork_mesh_union"  # NOTE: bl_idname should be lower case letters, no upper case letter allowed!! otherwise cause errors!!
    bl_label = "cork boolean union"

    def execute(self, context):
        cork = get_cork_filepath(context)
        try:
            validate_executable(cork)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        try:
            check_errors(context.selected_objects)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self._cork = cork
        self._plane = context.active_object
        self._base = context.selected_objects[0] if context.selected_objects[0] != self._plane else context.selected_objects[1]
        self._method = '-union'

        return self.exec(context)
    
    def exec(self, context):
        #try:
        slice_out(context, self._cork, self._method, self._base, self._plane)
        #except Exception as e:
        #    self.report({'ERROR'}, str(e))
        #    return {'CANCELLED'}

        return {'FINISHED'}


class CorkMeshBooleanDifference(Operator):
    """Cork boolean difference operation"""
    bl_idname = "view3d.cork_mesh_difference"
    bl_label = "cork boolean difference"

    def execute(self, context):
        cork = get_cork_filepath(context)
        try:
            validate_executable(cork)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        try:
            check_errors(context.selected_objects)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self._cork = cork
        self._plane = context.active_object
        self._base = context.selected_objects[0] if context.selected_objects[0] != self._plane else context.selected_objects[1]
        self._method = '-diff'

        return self.exec(context)

    def exec(self, context):
        try:
            slice_out(context, self._cork, self._method, self._base, self._plane)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        return {'FINISHED'}

class CorkMeshBooleanIntersect(Operator):
    """Cork boolean intersect operation"""
    bl_idname = "view3d.cork_mesh_intersect"
    bl_label = "cork boolean intersect"

    def execute(self, context):
        cork = get_cork_filepath(context)
        try:
            validate_executable(cork)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        try:
            check_errors(context.selected_objects)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self._cork = cork
        self._plane = context.active_object
        self._base = context.selected_objects[0] if context.selected_objects[0] != self._plane else context.selected_objects[1]
        self._method = '-isct'

        return self.exec(context)

    def exec(self, context):
        try:
            slice_out(context, self._cork, self._method, self._base, self._plane)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        return {'FINISHED'}

class CorkMeshBooleanXOR(Operator):
    """Cork boolean XOR operation"""
    bl_idname = "view3d.cork_mesh_xor"
    bl_label = "cork boolean xor"

    def execute(self, context):
        cork = get_cork_filepath(context)
        try:
            validate_executable(cork)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        try:
            check_errors(context.selected_objects)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self._cork = cork
        self._plane = context.active_object
        self._base = context.selected_objects[0] if context.selected_objects[0] != self._plane else context.selected_objects[1]
        self._method = '-xor'

        return self.exec(context)

    def exec(self, context):
        try:
            slice_out(context, self._cork, self._method, self._base, self._plane)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        return {'FINISHED'}

class CorkMeshBooleanResolve(Operator):
    """Cork boolean Resolve operation"""
    bl_idname = "view3d.cork_mesh_resolve"
    bl_label = "cork boolean Resolve"

    def execute(self, context):
        cork = get_cork_filepath(context)
        try:
            validate_executable(cork)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        try:
            check_errors(context.selected_objects)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self._cork = cork
        self._plane = context.active_object
        self._base = context.selected_objects[0] if context.selected_objects[0] != self._plane else context.selected_objects[1]
        self._method = '-resolve'

        return self.exec(context)

    def exec(self, context):
        try:
            slice_out(context, self._cork, self._method, self._base, self._plane)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        return {'FINISHED'}

class CorkMeshHelp(Operator):
    """Cork boolean help operation"""
    bl_idname = "view3d.cork_mesh_help"
    bl_label = "cork boolean help"

    show_help: BoolProperty(
            name="Help",
            description="",
            default=False,
            options={'HIDDEN', 'SKIP_SAVE'},
            )

    def execute(self, context):
        if self.show_help:
            context.window_manager.popup_menu(help_draw, title='Help', icon='QUESTION')
            return {'CANCELLED'}

# ############################################################
# Registration
# ############################################################

classes = ( CorkMeshSlicerPreferences,
            CorkMeshSlicerPanel,
            CorkMeshBooleanUnion,
            CorkMeshBooleanDifference,
            CorkMeshBooleanIntersect,
            CorkMeshBooleanXOR,
            CorkMeshBooleanResolve,
            CorkMeshHelp )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)


if __name__ == '__main__':
    register()
