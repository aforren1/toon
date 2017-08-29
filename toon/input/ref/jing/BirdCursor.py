import fobird
import fov

import os
# Pick the most precise clock function (this varies by Operating System)
if os.name == 'nt': # are we running Windows?
    from time import clock as CurrentTime
else: # Probably Linux (but maybe Mac; untested on Mac)
    from time import time as CurrentTime
from time import sleep as Pause

# Bird Calibration File
BIRD_CALIBRATION_FILE = os.path.join('Cursor','FOV_CALFILE.txt') #'BirdCalFile'

class BirdCursor:
    
    sampleRate = 138
    lastSample = -1
    currentHand = 1
    fobSet = False

    def __init__(self,Res=[800,600],Mode='POSITION',BirdCalFile = BIRD_CALIBRATION_FILE):
        #print "Please RESET Birds and switch to FLY..."
        #raw_input()
        self.calFile = BirdCalFile
        #self.loadCalibration()
        self.Streaming = False
        self.myFOV = fov.FieldOfView(Res,BirdCalFile)
        self.pixPerMM = self.myFOV.pixPerMM()
        
        print "Initializing Flock of Birds..."
        self._resetFOB_()
        print "...Flying."
        self.Yshift = 0
        self.Xshift = 0
        self.lastSample = None

    def shiftY(self,Yshift):
        self.Yshift = Yshift

    def shiftX(self,Xshift):
        self.Xshift = Xshift

    def _resetFOB_(self):
        # reset FOB if necessary...
        if self.fobSet == True:
            self._closeFOB_()

        self.myFOB = fobird.FOB()
        self.myFOB.groupSetup()
        self.myFOB.SetSampleRate(self.sampleRate)
        self.myFOB.run()
        Pause(0.5)
        self.fobSet = True

    def _closeFOB_(self):
        self.myFOB.sleep()
        self.myFOB.close()
        self.fobSet = False

    def Close(self):
        self._closeFOB()
        print "BIRDS should be closed."

    def StartStream(self):
        #self.myFOB.run()
        #Pause(0.5)
        print "Starting Stream..."
        self.myFOB.StartStream()
        self.Streaming = True
        self.FOBCoords = self.myFOB.Sample()
        self.lastSample = CurrentTime()
        self.ScreenCoords = self.myFOV.screenCoords(self.FOBCoords)

    def StopStream(self):
        print "Stopping Stream..."
        self.myFOB.StopStream()
        #self.myFOB.sleep()
        #print self.myFOB._readAll()
        self.lastSample = None

    def Update(self):
        self.FOBCoords = self.myFOB.Sample()
        if self.FOBCoords == None:
            self._resetFOB_()
            print "ERROR; Birds needed to be reset!"
            self.FOBCoords = self.myFOB.Sample()
        #if self.lastSample: # streaming
        #    if (CurrentTime()-self.lastSample) > 2/self.sampleRate:
                # We might have missed a sample...
                # clean up to avoid buffer overrun problems
        #        self.lastSample = CurrentTime()
        #        self.Update()
        #    else:
        #        self.lastSample = CurrentTime()
        #self.ScreenCoords = self.myFOV.screenCoords(self.FOBCoords)
        self.ScreenCoords = [self.myFOV.screenCoords_onehand(self.FOBCoords[0]),
                             self.myFOV.screenCoords_onehand(self.FOBCoords[1])]
        self.ScreenCoords = [(self.ScreenCoords[0][0]+self.Xshift,
                              self.ScreenCoords[0][1]+self.Yshift),
                             (self.ScreenCoords[1][0]+self.Xshift,
                              self.ScreenCoords[1][1]+self.Yshift)]
        
        #self.ScreenCoords[0][0] += self.Xshift
        #self.ScreenCoords[1][0] += self.Xshift
        #self.ScreenCoords[0][1] += self.Yshift
        #self.ScreenCoords[1][1] += self.Yshift

    def setDefault(self,hand=None):
        if hand:
            self.currentHand = hand

    def __getitem__(self,i=None):
        if i:
            return self.ScreenCoords[i]
        else:
            return self.ScreenCoords[self.currentHand]

