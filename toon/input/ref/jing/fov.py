from time import sleep
from fobird import FOB
from vector import Vector3

class FieldOfView:
    """
    Maps a physical FOV onto a screen with discrete resolution. Can
    convert a point within the physical FOV to a point on the screen.
    """
    def __init__(self, res=[800,600], LL=[0,0,0]  , LR=[800,0,0],
                                      UL=[0,0,600], UR=[800,0,600]):
        """
        Sets up our field of view with a resolution and 4 corners.

        @param res: a 2-tuple representing the screen resolution.
        """

        # John's hack to store a file
        if str(LL) == LL:
            myFile = open(LL,'r')
            Lines = myFile.readlines()
            myFile.close()
            for line in Lines:
                if 'LL' in line:
                    LL = eval(line.split(':')[1])
                    print LL
                if 'LR' in line:
                    LR = eval(line.split(':')[1])
                    print LR
                if 'UL' in line:
                    UL = eval(line.split(':')[1])
                    print UL
                if 'UR' in line:
                    UR = eval(line.split(':')[1])
                    print UR

        self.__res_X = res[0]
        self.__res_Y = res[1]
        self.__LL = LL
        print self.__LL
        self.__LR = LR
        print self.__LR
        self.__UL = UL
        print self.__UL
        self.__UR = UR
        print self.__UR
        # Vishal's code:
        #self.__W_vec = Vector3(LL, LR)
        #self.__H_vec = Vector3(LL, UL)
        #self.__scale_X = self.__res_X / self.__W_vec.length()
        #self.__scale_Y = self.__res_Y / self.__H_vec.length()
        # Below is John's hack:
        self.__W1_vec = Vector3(LL, LR)
        self.__W2_vec = Vector3(UL, UR)
        self.__W_vec = self.__W1_vec+self.__W2_vec
        self.__H1_vec = Vector3(LL, UL) 
        self.__H2_vec = Vector3(LR, UR)
        self.__H_vec = self.__H1_vec+self.__H2_vec
        self.__scale_X = 2*self.__res_X / self.__W_vec.length()
        self.__scale_Y = 2*self.__res_Y / self.__H_vec.length()

    def pixPerMM(self):
        #return (self.__res_X / 10*self.__W1_vec.length())
        return (self.__scale_X + self.__scale_Y)/20.0

    def isWithinFOV(self, position):
        """
        This is probably unnecessary; the pygame code I've been working
        with handles offscreen points exactly as you would hope.
           -- John
        """
        return True

    def screenCoords(self, position):
        """
        I want to grab both hands with one call, so I'm making this change.
        """
        screenHands = []
        for hand in position:
            screenHands.append(self.screenCoords_onehand(hand))
        return screenHands

    def screenCoords_onehand(self, position):
        """
        Returns a tuple representing the screen coordinates of the input
        position. If the position is outside the FOV, returns None.

        The mapping is found by projecting the position vector onto
        the width and height vectors to find the x and y coordinates
        w.r.t. the LL corner of the FOV. These values can be scaled to
        determine the x and y coordinates in screen space.

        @return: 2-tuple with x and y screen coordinates (assumes
                 origin is at LL corner of screen).
        """
        P_vec = Vector3(self.__LL, position)
        x = (P_vec.project(self.__W_vec) * self.__scale_X)
        y = (P_vec.project(self.__H_vec) * self.__scale_Y)
        return (x,y)
        
if __name__ == "__main__":

    g_FileName = 'FOV_CALFILE.txt'

    def get_affirmative(msg):
        while (not affirmative(msg)):
            pass
    def affirmative(msg):
        input = raw_input(msg).strip()
        return input == 'y' or input == 'yes'

    def save_to_file(filename,LL,LR,UL,UR):
        myFile = open(filename,'w')
        myFile.write('LL: ' + str(LL) + '\n');
        myFile.write('LR: ' + str(LR) + '\n');
        myFile.write('UL: ' + str(UL) + '\n');
        myFile.write('UR: ' + str(UR) + '\n');
        myFile.close()
        
    # init birds
    fob = FOB()
    #fob.open()
    #fob.fbbAutoConfig(numbirds=1)
    #fob.fbbReset()
    #fob.position(1)
    fob.groupSetup()
    fob.run()
    sleeptime = 5

    # capture corners
    get_affirmative('begin? (y/n): ')
    
    get_affirmative('capture LL corner? (y/n): ')
    LL = fob.point(1)
    get_affirmative('capture LR corner? (y/n): ')
    LR = fob.point(1)
    get_affirmative('capture UL corner? (y/n): ')
    UL = fob.point(1)
    get_affirmative('capture UR corner? (y/n): ')
    UR = fob.point(1)

    # init FOV object
    fov = FieldOfView([800,600], LL[0], LR[0], UL[0], UR[0])
    
    # capture position and print screen coords until terminated
    ###!!! HASN'T BEEN TESTED WITH ACTUAL BIRDS, SO POSSIBLY BUGGY
    while(affirmative('capture point? (y/n): ')):
        print 'capturing Point'
        P = fob.point(1)
        print P, '->', fov.screenCoords(P)

    get_affirmative('Saving to config file... press y to proceed.')
    save_to_file(g_FileName,LL[0],LR[0],UL[0],UR[0])
    fob.sleep()
    fob.close()
