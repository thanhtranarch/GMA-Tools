"""
Workset
Assign Workset to Project
Author: Tran Tien Thanh
Mail: trantienthanh.arch@gmail.com
--------------------------------------------------------
Click to Create Workset(s)
Shift + Click to Create Central File
"""

__author__ ="Tran Tien Thanh"
__title__ = "Workset \n  & Central File"

# Import necessary modules
from Autodesk.Revit.DB import (
    FilteredWorksetCollector,
    Workset,
    WorksetKind,
    Transaction,
    SaveAsOptions,
    WorksharingSaveAsOptions,
)
from Autodesk.Revit.UI import TaskDialog
from pyrevit import forms

# Get active document and its UIDocument
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# Dictionary of worksets with their descriptions
workset_dict = {
    "_ARCHITECT": "Elements in building (except structural)",
    "_CIVIL": "Civil elements",
    "_FACADE": "Facade elements (except structure)",
    "_LANDSCAPE": "Landscape elements",
    "_UNIT": "Unit, group unit, and furniture in unit",
    "_SHARED LEVELS & GRIDS": "Grid and level",
    "_STRUCTURE": "Structural elements",
    "INVISIBLE": "Invisible elements",
}

# Set of existing workset names
existing_workset_names = set(ws.Name for ws in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset))

# List to store newly created workset names
new_cre_worksets = []

# Function to enable worksharing
def enable_worksharing():
    try:
        doc.EnableWorksharing("_SHARED LEVELS & GRIDS", "_ARCHITECT")
    except Exception as e:
        print("Failed to enable worksharing:", e)

# Function to create worksets
def create_worksets():
    for workset_name, description in workset_dict.items():
        if workset_name not in existing_workset_names:
            t = Transaction(doc, "Create workset: " + workset_name)
            t.Start()
            new_workset = Workset.Create(doc, workset_name)
            t.Commit()
            new_cre_worksets.append(workset_name)

# Function to create central file
def create_central():
    file_name = forms.save_file()
    if file_name:
        file_name_without_extension = file_name.rsplit(".", 1)[0]
        central_file_path = file_name_without_extension + ".rvt"
        try:
            options = WorksharingSaveAsOptions()
            options.SaveAsCentral = True
            saveas_option = SaveAsOptions()
            saveas_option.MaximumBackups = 10
            saveas_option.OverwriteExistingFile = True
            saveas_option.SetWorksharingOptions(options)
            doc.SaveAs(central_file_path, saveas_option)
            TaskDialog.Show("Central Created", "Central File was created")
        except Exception as e:
            print("Failed to create Central File:", e)
    else:
        TaskDialog.Show("Central Created", "Please set path")

# Main logic
if __shiftclick__:
    create_central()  # If Shift + Click, create central file
else:
    if not doc.IsWorkshared:
        enable_worksharing()  # If not workshared, enable worksharing
    if not set(workset_dict.keys()) in existing_workset_names:
        create_worksets()  # If worksets don't exist, create them
        if new_cre_worksets:
            TaskDialog.Show(
                "Worksets Created",
                "The following worksets were successfully created:\n" + "\n".join(new_cre_worksets),
            )
        else:
            TaskDialog.Show("Worksets", "Worksets already exist")  # Inform if worksets exist
