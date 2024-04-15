"""
Make Plans
Create Plans from Room List
Author: Tran Tien Thanh
--------------------------------------------------------
"""

__author__ ="Tran Tien Thanh"
__title__ = "Plan Views"

from rpw import revit, DB, db

from Autodesk.Revit.DB import (
    Transaction,
    View,
    FilteredElementCollector,
    BuiltInCategory,
    ViewType
)
from Autodesk.Revit.UI import TaskDialog
from pyrevit import forms

"""--------------------------------------------------"""
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
"""--------------------------------------------------"""
rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements()
new_views = []
viewlist = FilteredElementCollector(doc).OfClass(View).WhereElementIsNotElementType().ToElements()
vtemp = {}
for v in viewlist:
    if v.IsTemplate and 'master' not in v.Name.lower():
        vtemp[v.Name]=v.Id.IntegerValue
plan_templates=sorted([v.Name for v in viewlist if v.ViewType == ViewType.FloorPlan and v.Id.IntegerValue in vtemp.values()])
RCP_templates=sorted([v.Name for v in viewlist if v.ViewType == ViewType.CeilingPlan and v.Id.IntegerValue in vtemp.values()])
template_plan=None
template_RCP=None
list_rooms={}
rooms_type = [("{} | #{}".format(room.LookupParameter("Name").AsString(), room.LookupParameter("Number").AsString())) for room in rooms]
room_type_sorted = sorted(rooms_type, key=lambda x: x[0])  # Sort by room name
plan_types = db.Collector(of_class='ViewFamilyType', is_type=True).get_elements(wrapped=True)
plan_types_options = {t.name for t in plan_types
                      if t.view_family.name in ('FloorPlan', 'CeilingPlan')}
"""--------------------------------------------------"""
class NewView:
    def __init__(self, name, bbox, level_id):
        self.name = name
        self.bbox = bbox
        self.level_id = level_id
def get_room_info():
    for room in rooms:
        room_name = room.LookupParameter("Name").AsString()
        level = doc.GetElement(room.LevelId)
        level_name = level.Name
        room_type = doc.GetElement(room.GetTypeId())
        room_type_name = room_type.Name
        room_number = room.LookupParameter("Number").AsString()
        room_occpancy=room.LookupParameter("Occupancy").AsString()
        room_info_dict[room_name] = {
            "Level": level_name,
            "Number": room_number,
            "Room Type": room_type_name,
            "Occupancy": room_occpancy
        }
    return room_info_dict
def offset_bbox(bbox, offset=1):
    # if bbox:
    #     try:
    bboxMinX = bbox.Min.X - offset
    bboxMinY = bbox.Min.Y - offset
    bboxMinZ = bbox.Min.Z - offset
    bboxMaxX = bbox.Max.X + offset
    bboxMaxY = bbox.Max.Y + offset
    bboxMaxZ = bbox.Max.Z + offset
    newBbox = DB.BoundingBoxXYZ()
    newBbox.Min = DB.XYZ(bboxMinX, bboxMinY, bboxMinZ)
    newBbox.Max = DB.XYZ(bboxMaxX, bboxMaxY, bboxMaxZ)
    return newBbox
    #     except Exception as e:
    #         print("{}".format(e))
    #         raise e
    # else:
    #     TaskDialog.Show("Get Boundary","None Boundary was getted")

def create_plan(new_view, view_type_id, cropbox_visible=True, remove_underlay=True):
    t = Transaction(doc, "Create Plan View")
    t.Start()
    try:
        name = new_view.name
        bbox = new_view.bbox
        level_id = new_view.level_id
        viewplan = DB.ViewPlan.Create(doc, view_type_id, level_id)
        viewplan.CropBoxActive = True
        viewplan.CropBoxVisible = cropbox_visible

        if remove_underlay and revit.version.year == '2015':
            underlay_param = viewplan.get_Parameter(DB.BuiltInParameter.VIEW_UNDERLAY_ID)
            underlay_param.Set(DB.ElementId.InvalidElementId)

        viewplan.CropBox = bbox

        counter = 1
        while True:
            try:
                viewplan.Name = name
            except Exception:
                try:
                    viewplan.Name = '{} - Copy {}'.format(name, counter)
                except Exception as e:
                    counter += 1
                    if counter > 100:
                        raise Exception('Exceeded Maximum Loop')
                else:
                    break
            else:
                break
        t.Commit()

        return viewplan
    except Exception as e:
        print("{}".format(e))
        raise e
"""-----------------------------------"""
selected_rooms = forms.SelectFromList.show(
    room_type_sorted,
    title="Select Room",
    width=500,
    button_name="Run",
    multiselect=True)
if selected_rooms:
    for room in selected_rooms:
        a=room.split(" |")
        if "UNIT" in room:
            list_rooms[a[1].strip(" #")] = a[-1]
        else:
            list_rooms[a[1].strip(" #")] = a[0]
    print(list_rooms)
    for room_number in list_rooms:
        room_element = None
        room_name = ""
        for room in rooms:
            if room.LookupParameter("Number").AsString() == room_number:
                room_element = room
                room_name = list_rooms[room_number]
                break
        if room_element:
            if "UNIT" in room_element.LookupParameter("Name").AsString():
                unittype=room_element.LookupParameter("Room Type").AsString()
                name_planview = "ENLARGED PLAN - TYPE {} ({})".format(unittype,room_name)
            else:
                name_planview = "{} - ENLARGED PLAN - NUMBER {}".format(room_name,room_number)
            room_level_id = room_element.Level.Id
            room_bbox = room_element.get_BoundingBox(doc.ActiveView)
            new_bbox = offset_bbox(room_bbox)
            new_view = NewView(name=name_planview, bbox=new_bbox, level_id=room_level_id)
            new_views.append(new_view)
        else:
            print("Room '{}' not found in the project.".format(room_name))

    plan_type = forms.SelectFromList.show(
        plan_types_options,
        title="Type View",
        width=500,
        button_name="Run",
        multiselect=True)
    if plan_type:
        if "Floor Plan" in plan_type:
            template_plan = forms.SelectFromList.show(
                plan_templates,
                title="View templates (Plan)",
                width=500,
                button_name="Run",
                multiselect=False)

        if "Ceiling Plan" in plan_type:
            template_RCP = forms.SelectFromList.show(
                RCP_templates,
                title="View templates (RCP)",
                width=500,
                button_name="Run",
                multiselect=False)
        view_type_ids = {t.Id for t in plan_types if t.name in plan_type}
        """-----------------------------------"""
        for view_type_id in view_type_ids:
            for new_view in new_views:
                view = create_plan(new_view= new_view, view_type_id=view_type_id)
                if template_RCP or template_plan:
                    if view.ViewType == ViewType.FloorPlan:
                        template_name = template_plan
                    elif view.ViewType == ViewType.CeilingPlan:
                        template_name = template_RCP
                    template_id = next((v.Id for v in viewlist if v.Name == template_name), None)

                    t = Transaction(doc, "Assign Template")
                    t.Start()

                    try:
                        if template_id:
                            view.ViewTemplateId = template_id
                        else:
                            raise ValueError("No template found with name '{}'".format(template_name))
                        t.Commit()

                    except Exception as e:
                        t.RollBack()
                        print("Error: {}".format(e))
                else:
                    TaskDialog.Show("Create Plan", "Plan {} was create without template".format(view.Name))
    else:
        TaskDialog.Show("Create Plan", "Please proceed")
else:
    TaskDialog.Show("Create Plan", "Please proceed")
