"""
Workset
Assign Workset to Project
Author: Tran Tien Thanh
--------------------------------------------------------
Click to Create Workset(s)
Shift + Click to Create Central File
"""

__author__ ="Tran Tien Thanh"
__title__ = "Workset \n  & Central File"

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

"""--------------------------------------------------"""
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
"""--------------------------------------------------"""
# The workset_dict can be adjusted to meet company standards
workset_dict= \
    {"_ARCHITECT": "USE FOR ELEMENTS IN BUILDING (EXCEPT STRUCTURAL)",
     "_CIVIL":"USE FOR CIVIL",
     "_FACADE":"USE FOR FACADE (EXCEPT STRUCTURE)",
     "_LANDSCAPE":"USE FOR LANDSCAPE",
     "_UNIT":"USE FOR UNIT, GROUP UNIT, AND FURNITURE IN UNIT",
     "_SHARED LEVELS & GRIDS":"USE FOR GRID & LEVEL",
     "_STRUCTURE":"USE FOR STRUCTURE",
     "INVISIBLE":"USE FOR INVISIBLE ELEMENT"
    }
"""--------------------------------------------------"""
existing_workset_names = set(ws.Name for ws in FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset))
new_cre_worksets=[]
"""--------------------------------------------------"""
def enable_worksharing():
    try:
        doc.EnableWorksharing("_SHARED LEVELS & GRIDS","_ARCHITECT")
    except Exception as e:
        print("Failed to enable worksharing:", e)

def create_worksets():
    for workset_name, description in workset_dict.items():
        if workset_name not in existing_workset_names:
            t=Transaction(doc,"Create workset: " + workset_name)
            t.Start()
            new_workse=Workset.Create(doc,workset_name)
            t.Commit()
            new_cre_worksets.append(workset_name)

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

if __shiftclick__:
    create_central()
else:
    if not doc.IsWorkshared:
        enable_worksharing()
    if not set(workset_dict.keys()) in existing_workset_names:
        create_worksets()
        if new_cre_worksets:
            TaskDialog.Show("Worksets Created",
                    "The following worksets were successfully created:\n" + "\n".join(new_cre_worksets))
        else:
            TaskDialog.Show("Worksets", "Worksets Existing")
