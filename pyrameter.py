# ##### BEGIN GPL LICENSE BLOCK #####
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
# ##### END GPL LICENSE BLOCK #####
#
# Copyright (C) Milovann Yanatchkov 2020 
#

import bpy
import bmesh
from bpy_extras.object_utils import object_data_add

from bpy.props import (
		BoolProperty,
		EnumProperty,
		FloatProperty,
		IntProperty,
		StringProperty,
		CollectionProperty,
		)


# Find script object
def pyrameter_find_script(name):
	for text in bpy.data.texts:
		if text.name == name:
			return text
	return None

# Find a pyrameter entry 
def pyrameter_find_entry(obj,name):

	ref = None
	for item in obj.pyrameter:
		if item.name == name:
			ref = item
	return ref


# Pyrameter Object
class PyrameterObject(bpy.types.PropertyGroup):

	name: StringProperty(name="Name")
	type: StringProperty(name="type")
	id: StringProperty(name="id")
	val_int: IntProperty(name="val_int")
	val_float: FloatProperty(name="val_float")

	# vertices
	vertices = [[-1,-1,-1]]
	faces = [[0, 1, 2, 3]]

	def show(self):
		print("pyrameter show [" + self.name + "]")
		for v in self.vertices:
			print(v)
		for f in self.faces:
			print(f)

	def get_vertices(self):
		return self.vertices

	def get_faces(self):
		return self.faces

# Set vertices
def pyrameter_vertices(vertices):

	obj = bpy.context.object
	ref = pyrameter_find_entry(obj,"vertices")

	# Add vertices entry
	if ref == None:
		ref = obj.pyrameter.add()
		ref.type = 'vertices'
		ref.name = 'vertices'

	# Cleanup
	ref.vertices.clear()
	
	# Add vertices
	for vert in vertices:
		ref.vertices.append(vert)

# Set faces
def pyrameter_faces(faces):

	obj = bpy.context.object
	ref = pyrameter_find_entry(obj,"faces")

	# Add faces entry
	if ref == None:
		ref = obj.pyrameter.add()
		ref.type = 'faces'
		ref.name = 'faces'

	# Cleanup
	ref.faces.clear()
	
	# Add vertices
	for face in faces:
		ref.faces.append(face)

# Add float parameter
def pyrameter_float(name):

	obj = bpy.context.object
	ref = pyrameter_find_entry(obj,name)
	
	# Return
	if ref != None:
		return ref.val_float

	# Create
	button = obj.pyrameter.add()
	button.type = "float"
	button.name = name
	button.val_int = 1
	button.val_float = 1
	button.id = obj.name + '_float'

	# Default value
	return 0

# Add int parameter
def pyrameter_int(name):

	obj = bpy.context.object
	ref = pyrameter_find_entry(obj,name)
	
	# Return
	if ref != None:
		return ref.val_int

	# Create
	button = obj.pyrameter.add()
	button.type = "int"
	button.name = name
	button.val_int = 1
	button.val_float = 1
	button.id = obj.name + '_int'

	# Default value
	return 0

def pyrameter_build(self,context,obj):

	scale_x = 1 
	scale_y = 1

	pyverts = pyrameter_find_entry(obj,"vertices")
	verts = pyverts.get_vertices()

	pyfaces = pyrameter_find_entry(obj,"faces")
	faces = pyfaces.get_faces()

	edges = []

	mesh = bpy.data.meshes.new(name="New Object Mesh")
	mesh.from_pydata(verts, edges, faces)

	me = obj.data
	bm = bmesh.new()
	bm.from_mesh(mesh)
	bm.to_mesh(me)
	bm.free()  


pyrameter_script = """

def plane():
	s = pyrameter_float("size")
	pyrameter_vertices([[-1*s,-1*s,0],[-1*s,1*s,0],[1*s,1*s,0],[1*s,-1*s,0]])
	pyrameter_faces([[0, 1, 2, 3]])

def box():
	l = pyrameter_float("length")
	w = pyrameter_float("width")
	h = pyrameter_float("height")
	pyrameter_vertices([
		[0,0,0],
		[l,0,0],
		[l,w,0],
		[0,w,0],
		[0,0,h],
		[l,0,h],
		[l,w,h],
		[0,w,h],
	])
	pyrameter_faces([
		[0, 1, 2, 3],
		[4, 5, 6, 7],
		[0, 1, 5, 4],
		[1, 2, 6, 5],
		[2, 3, 7, 6],
		[3, 0, 4, 7],
		])

plane()
"""

class Update_OT_Pyrameter(bpy.types.Operator):

	"""Update"""
	bl_idname = "pyrameter.update"
	bl_label = 'Update'
	bl_options = {'UNDO'}

	def execute(self, context):

		obj = bpy.context.object

		if not hasattr(obj, 'pyrameter'):
			bpy.types.Object.pyrameter = bpy.props.CollectionProperty(type=PyrameterObject)

		# Name
		script_name = obj.name + ".py"

		# Check script
		text = pyrameter_find_script(script_name)

		# Create Script
		if text == None:
			# New text
			bpy.ops.text.new()
			text = bpy.data.texts[0]
			text.name = script_name
			# Add text data
			text.write(pyrameter_script)

		# Select script
		text = pyrameter_find_script(script_name)
		if text != None:
			text.use_module = True
			bpy.data.texts[script_name].use_module = True 

			# Cleanup: remove all buttons
			obj.pyrameter.clear()

			# Exec
			exec(text.as_string())
		else:
			print("pyrameter: can't find script:" + script_name)

		return {'FINISHED'}

class Build_OT_Pyrameter(bpy.types.Operator):
	"""Build Mesh"""
	bl_idname = "pyrameter.build"
	bl_label = 'Build'
	bl_options = {'UNDO'}

	def execute(self, context):

		obj = bpy.context.object

		# Name
		script_name = obj.name + ".py"

		text = pyrameter_find_script(script_name)
		if text != None:
			text.use_module = True
			bpy.data.texts[script_name].use_module = True 

			# Exec
			exec(text.as_string())

		# Build
		pyrameter_build(self,context,obj)

		return {'FINISHED'}

class Main_PT_Pyrameter(bpy.types.Panel):

	bl_space_type='PROPERTIES'
	bl_region_type='WINDOW'
	bl_context="object"
	bl_label="Pyrameter"

	# Props
	bpy.types.Scene.pyrameter_int = bpy.props.IntProperty("pyrameter_int", default=1)
	bpy.types.Scene.pyrameter_float = bpy.props.FloatProperty("pyrameter_float", default=1.0)
	bpy.types.Object.pyrameter_vertices = bpy.props.FloatVectorProperty("pyrameter_vertices")

	@classmethod
	def poll(cls,context):
		return context.scene


	def draw(self,context):

		scene = bpy.context.scene

		# Check selection
		selected = bpy.context.selected_objects
		obj = bpy.context.object

		if len(selected) == 1 and obj.type == "MESH":

			data = obj.data
			layout=self.layout

			col=layout.column(align=True)


			# Controls
			if hasattr(obj,'pyrameter'):

				# Update
				col.operator(Update_OT_Pyrameter.bl_idname,text="Update")

				# Parameters
				col=layout.column(align=True)
				for item in obj.pyrameter:
					if item.type == "int":
						col.prop(item,"val_int",text=item.name)
					elif item.type == "float":
						col.prop(item,"val_float",text=item.name)

				# Build
				col=layout.column(align=True)
				col.operator(Build_OT_Pyrameter.bl_idname,text="Build")
			else:
				# Init
				col=layout.column(align=True)
				# Update
				col.operator(Update_OT_Pyrameter.bl_idname,text="Init")


 
def register():
	bpy.utils.register_class(PyrameterObject)
	bpy.utils.register_class(Main_PT_Pyrameter)
	bpy.utils.register_class(Update_OT_Pyrameter)
	bpy.utils.register_class(Build_OT_Pyrameter)

def unregister():
	bpy.utils.unregister_class(PyrameterObject)
	bpy.utils.unregister_class(Main_PT_Pyrameter)
	bpy.utils.unregister_class(Update_OT_Pyrameter)
	bpy.utils.register_class(Build_OT_Pyrameter)

# vim: set noet sts=8 sw=8 :
