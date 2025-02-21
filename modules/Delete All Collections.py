import bpy

# Get the scene
scene = bpy.context.scene

# Collect all collections except the Scene Collection
collections_to_delete = [coll for coll in bpy.data.collections if coll != scene.collection]

# Delete all user-created collections
for coll in collections_to_delete:
    bpy.data.collections.remove(coll)

print("All user-created collections deleted from the scene!")