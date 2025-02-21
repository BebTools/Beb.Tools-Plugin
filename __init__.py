bl_info = {
    "name": "Beb.Tools",
    "author": "Beb",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "N-Panel",
    "description": "A modular toolset for Blender",
    "category": "Tools",
}

import bpy
import os
from bpy.types import Operator, Panel, PropertyGroup, UIList
from bpy.props import StringProperty, IntProperty, CollectionProperty

MODULES_DIR = os.path.join(os.path.dirname(__file__), "modules")

class BebToolsScriptItem(bpy.types.PropertyGroup):
    name: StringProperty(name="Script Name")

class BEBTOOLS_OT_InitScripts(Operator):
    bl_idname = "bebtools.init_scripts"
    bl_label = "Initialize Script List"
    bl_description = "Populate the script list"

    def execute(self, context):
        wm = context.window_manager
        wm.bebtools_scripts.clear()
        for script in get_scripts():
            item = wm.bebtools_scripts.add()
            item.name = script
        wm.bebtools_active_index = 0 if wm.bebtools_scripts else -1
        return {'FINISHED'}

class BEBTOOLS_UL_ScriptList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name)
        row.operator("bebtools.show_script_info", text="", icon="QUESTION", emboss=False).script_name = item.name

class BEBTOOLS_OT_ShowScriptInfo(Operator):
    bl_idname = "bebtools.show_script_info"
    bl_label = "Show Script Info"
    bl_description = "Display instructions for the selected script"
    script_name: StringProperty()

    def execute(self, context):
        info_file = os.path.join(MODULES_DIR, f"{self.script_name}.txt")
        if os.path.exists(info_file):
            text_name = f"{self.script_name}_info"
            if text_name not in bpy.data.texts:
                text_block = bpy.data.texts.new(text_name)
                with open(info_file, "r") as f:
                    text_block.from_string(f.read())
            else:
                text_block = bpy.data.texts[text_name]
            for area in context.screen.areas:
                if area.type == 'TEXT_EDITOR':
                    area.spaces.active.text = text_block
                    return {'FINISHED'}
            bpy.ops.screen.area_split(direction='VERTICAL', factor=0.3)
            new_area = context.screen.areas[-1]
            new_area.type = 'TEXT_EDITOR'
            new_area.spaces.active.text = text_block
        else:
            def draw_popup(self, context):
                self.layout.label(text=f"No instructions found for '{self.script_name}'.")
            bpy.context.window_manager.popup_menu(draw_popup, title="Script Info", icon='INFO')
        return {'FINISHED'}

class BEBTOOLS_OT_Apply(Operator):
    bl_idname = "bebtools.apply"
    bl_label = "Apply"
    bl_description = "Run the selected script"

    def execute(self, context):
        wm = context.window_manager
        if wm.bebtools_active_index >= 0 and wm.bebtools_active_index < len(wm.bebtools_scripts):
            script_name = wm.bebtools_scripts[wm.bebtools_active_index].name
            script_path = os.path.join(MODULES_DIR, f"{script_name}.py")
            try:
                with open(script_path, "r") as file:
                    exec(file.read(), globals())
                self.report({'INFO'}, f"Executed script: {script_name}")
            except Exception as e:
                self.report({'ERROR'}, f"Error running {script_name}: {str(e)}")
        else:
            self.report({'WARNING'}, "No script selected")
        return {'FINISHED'}

class BEBTOOLS_PT_Panel(Panel):
    bl_label = "Beb.Tools"
    bl_idname = "BEBTOOLS_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Beb.Tools"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        if not wm.bebtools_scripts:
            layout.operator("bebtools.init_scripts", text="Load Scripts")
        else:
            layout.template_list(
                "BEBTOOLS_UL_ScriptList",
                "bebtools_script_list",
                wm,
                "bebtools_scripts",
                wm,
                "bebtools_active_index",
                rows=5,
            )
            layout.operator("bebtools.apply", text="Apply")

def get_scripts():
    scripts = []
    if os.path.exists(MODULES_DIR):
        for filename in os.listdir(MODULES_DIR):
            if filename.endswith(".py") and not filename.startswith("__"):
                script_name = filename[:-3]
                scripts.append(script_name)
    return scripts

classes = (
    BebToolsScriptItem,  # Must be registered first
    BEBTOOLS_OT_InitScripts,
    BEBTOOLS_UL_ScriptList,
    BEBTOOLS_OT_ShowScriptInfo,
    BEBTOOLS_OT_Apply,
    BEBTOOLS_PT_Panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.bebtools_scripts = CollectionProperty(type=BebToolsScriptItem)
    bpy.types.WindowManager.bebtools_active_index = IntProperty(
        name="Active Script Index",
        default=0,
    )
    bpy.app.timers.register(
        lambda: bpy.ops.bebtools.init_scripts('INVOKE_DEFAULT'),
        first_interval=0.1
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.WindowManager.bebtools_scripts
    del bpy.types.WindowManager.bebtools_active_index

if __name__ == "__main__":
    register()