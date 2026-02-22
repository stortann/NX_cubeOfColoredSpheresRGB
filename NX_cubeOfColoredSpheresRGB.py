# NX 2412


import math
import NXOpen
import NXOpen.Features
import NXOpen.GeometricUtilities
import NXOpen.UF
import time


def main():

    theSession = NXOpen.Session.GetSession()
    theUFSession = NXOpen.UF.UFSession.GetUFSession()
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    theUI = NXOpen.UI.GetUI()
    theNxMessageBox = theUI.NXMessageBox

    delete_all(theSession, workPart)

    # sphereStep should be a positive integer in range from 1 to 255
    sphereStep = 25
    # sphereSize, preferrably, should be a positive integer less than sphereStep
    sphereSize = 10

    timeStart = time.time()

    create_spheres(workPart, sphereSize, sphereStep)

    for feature in workPart.Features:

        myColorIndex = get_closest_nx_color(theUFSession, feature)

        featureBodies = feature.GetBodies()

        for myBody in featureBodies:

            change_body_color(theSession, myColorIndex, myBody)

    # updating the Part Navigator so the cube will be seen
    markId1 = theSession.SetUndoMark(
        NXOpen.Session.MarkVisibility.Visible, "Update Model"
    )
    theSession.UpdateManager.UpdateModel(workPart, markId1)

    elapsedTime = time.time() - timeStart
    theNxMessageBox.Show(
        "How many seconds have passed:",
        NXOpen.NXMessageBox.DialogType.Information,
        str(elapsedTime),
    )


def create_spheres(workPart, sphereSize, sphereStep):

    for myR in range(0, 255, sphereStep):
        for myG in range(0, 255, sphereStep):
            for myB in range(0, 255, sphereStep):

                sphereBuilder1 = workPart.Features.CreateSphereBuilder(
                    NXOpen.Features.Sphere.Null
                )
                sphereBuilder1.Diameter.SetFormula(str(sphereSize))

                coordinates1 = NXOpen.Point3d(float(myR), float(myG), float(myB))
                point1 = workPart.Points.CreatePoint(coordinates1)
                sphereBuilder1.CenterPoint = point1

                nXObject1 = sphereBuilder1.Commit()

                sphereBuilder1.Destroy()
                workPart.Points.DeletePoint(point1)

                nXObject1.SetName(f"{myR}_{myG}_{myB}")


def get_closest_nx_color(theUFSession, feature):

    newColor = [int(i) / 255 for i in feature.Name.split("_")]
    myColorIndex = 0

    colorModel = NXOpen.UF.UFConstants.UF_DISP_rgb_model
    method = NXOpen.UF.UFConstants.UF_DISP_CCM_EUCLIDEAN_DISTANCE
    return theUFSession.Disp.AskClosestColor(colorModel, newColor, method)


def change_body_color(theSession, myColorIndex, myBody):

    displayModification1 = theSession.DisplayManager.NewDisplayModification()
    displayModification1.ApplyToAllFaces = True
    displayModification1.ApplyToOwningParts = False
    displayModification1.EndPointDisplayState = False

    displayModification1.NewColor = myColorIndex

    myObjects = [NXOpen.DisplayableObject.Null] * 1

    myObjects[0] = myBody

    displayModification1.Apply(myObjects)
    displayModification1.Dispose()


def delete_all(theSession, workPart):

    theSession.UpdateManager.ClearErrorList()

    objectsToDelete = []
    for myFeature in workPart.Features:
        objectsToDelete.append(myFeature)

    deleteObjects = theSession.UpdateManager.AddObjectsToDeleteList(objectsToDelete)
    id1 = theSession.NewestVisibleUndoMark
    nErrs2 = theSession.UpdateManager.DoUpdate(id1)


if __name__ == "__main__":
    main()
