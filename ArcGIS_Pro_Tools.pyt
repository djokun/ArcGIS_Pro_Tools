# -*- coding: utf-8 -*-

import arcpy
import os


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [
                changeSourceGDB,
                applySymbology
                ]


# class Tool:
#     def __init__(self):
#         """Define the tool (tool name is the name of the class)."""
#         self.label = "Tool"
#         self.description = ""
# 
#     def getParameterInfo(self):
#         """Define the tool parameters."""
#         params = None
#         return params
# 
#     def isLicensed(self):
#         """Set whether the tool is licensed to execute."""
#         return True
# 
#     def updateParameters(self, parameters):
#         """Modify the values and properties of parameters before internal
#         validation is performed.  This method is called whenever a parameter
#         has been changed."""
#         return
# 
#     def updateMessages(self, parameters):
#         """Modify the messages created by internal validation for each tool
#         parameter. This method is called after internal validation."""
#         return
# 
#     def execute(self, parameters, messages):
#         """The source code of the tool."""
#         return
# 
#     def postExecute(self, parameters):
#         """This method takes place after outputs are processed and
#         added to the display."""
#         return

class changeSourceGDB:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Update GDB Source"
        self.description = "This toolbox contains a tool that can change the source GDB of multiple layers in a map document"

    def getParameterInfo(self):
        """Define the tool parameters."""
        p0 = arcpy.Parameter(
                displayName = "Old Source GDB",
                name = "old_gdb",
                datatype = "DEWorkspace",
                parameterType = "Required",
                direction = "Input"
                )
        p1 = arcpy.Parameter(
                displayName = "New Source GDB",
                name = "new_gdb",
                datatype = "DEWorkspace",
                parameterType = "Required",
                direction = "Input"
                )
        params = [p0,p1]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        old_gdb = parameters[0].valueAsText
        new_gdb = parameters[1].valueAsText
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        map_name = aprx.activeMap.name
        m = aprx.listMaps(f"{map_name}")[0]
        for lyr in m.listLayers():
            if lyr.supports("DATASOURCE") and os.path.dirname(lyr.dataSource) == old_gdb:
                lyr.updateConnectionProperties(old_gdb, new_gdb, validate=False)
                arcpy.AddMessage(f"New Data Source for {lyr}: {lyr.dataSource}")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return

class applySymbology:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Apply Symbology To Multiple Layers"
        self.description = '''
            This tool can match symbology files to multiple layers in the active map document
        '''

    def getParameterInfo(self):
        """Define the tool parameters."""
        p0 = arcpy.Parameter(
                displayName = "Location of Layer Files",
                name = "sym_folder",
                datatype = "DEFolder",
                parameterType = "Required",
                direction = "Input"
                )
        # If p1 is left blank, the whole active map document will be used
        p1 = arcpy.Parameter(
                displayName = "Group Layer",
                name = "group_layer",
                datatype = "GPGroupLayer",
                parameterType = "Optional",
                direction = "Input"
                )

        params = [p0,p1]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        sym_folder = parameters[0].valueAsText
        group_layer = parameters[1].valueAsText
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        map_name = aprx.activeMap.name
        m = aprx.listMaps(f"{map_name}")[0]
        sym_list = []
        sym_names_list = []
        for dirpath, dirnames, filenames in arcpy.da.Walk(sym_folder):
            for filename in filenames:
                sym_list.append(os.path.join(dirpath, filename))
                sym_names_list.append(os.path.splitext(filename)[0])
        if group_layer:
            arcpy.AddMessage(f"Map layer selected, applying symbology to {group_layer}")
            list_of_lyrs = m.listLayers(os.path.basename(group_layer))[0]
        else:
            arcpy.AddMessage(f"No map layer chosen, applying symbology to Map: {map_name}")
            list_of_lyrs = m
        for lyr in list_of_lyrs.listLayers():
            for name, file in zip(sym_names_list, sym_list):
                if name == lyr.name[0:len(name)]:
                    # if the symbology layer is in the first part of the layer name
                    arcpy.AddMessage(f"Updating {lyr} symbology")
                    sym_lyr = m.addDataFromPath(file)
                    sym = sym_lyr.symbology
                    lyr.symbology = sym
                    m.removeLayer(sym_lyr)
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
