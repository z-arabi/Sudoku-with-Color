import math
from copy import deepcopy
# import time 

class Game():
    def __init__(self,n,colors):
        self.n = n
        self.m = len(colors)
        self.colors = colors
        self.mainBorad = None
        self.boards = [] # list of the Boads' object
        self.counter = 0
    
    def start(self,startString):
        board = Board(self.n,self.colors,[])
        self.mainBorad = board.createBoard(startString)
        self.boards.append(self.mainBorad)

    def checkFinish(self,blocksList):
        for block in blocksList:
            if block.number==None or block.color == None:
                return False
        return True 
       
    def solve(self):
        while(len(self.boards) > 0 or not self.checkFinish(self.boards[-1].getBoard())):
            print("-------------------------")
            # print(f"----------------------step:{self.counter} the lists of boards:{len(self.boards)}")
            print(self.boards[-1])
            oldBoard = self.boards[-1]
            blocksList = oldBoard.getBoard()

            blockCandidatesNumber = oldBoard.getMostConstraintInNumber()
            # print("the number candidates",[(x.id,x.constraintDegree) for x in blockCandidatesNumber])
            if len(blockCandidatesNumber) > 0:
                currentBlock = min(blockCandidatesNumber,key= lambda block:block.constraintDegree)
                currentBlock.candidatedForNumber = True
            elif len(blockCandidatesNumber) == 0:
                blockCandidatesColor = oldBoard.getMostConstraintInColor()
                # print("the color candiadates",[(x.id,x.constraintDegree) for x in blockCandidatesColor])
                if len(blockCandidatesColor) > 0:
                    currentBlock = min(blockCandidatesColor,key= lambda block:block.constraintDegree)
                    currentBlock.candidatedForColor = True
                elif len(blockCandidatesColor) == 0:
                    if self.checkFinish(oldBoard.getBoard()):
                        # print("checked\\\\")
                        print(oldBoard)
                        return oldBoard
                    self.boards.pop()
                    self.solve()                  
                    
            # print(currentBlock)
            # currentBlock.domainColor.reverse()

            if not currentBlock.number and not currentBlock.color:
                # print("set number and color")
                for num in currentBlock.domainNumber:
                    for color in currentBlock.domainColor:
                        newBoard = Board(self.n,self.colors,deepcopy(oldBoard.getBoard()))
                        newBoard.getBoard()[currentBlock.id[0]*self.n+currentBlock.id[1]].setNumber(num)
                        newBoard.getBoard()[currentBlock.id[0]*self.n+currentBlock.id[1]].setColor(color)
                        newBoard.updateConstraints()
                        checkFlag = newBoard.forwardChecking()
                        if checkFlag:
                            # print(f"{num} with {color} is set true")
                            currentBlock.candidatedForColor = True   
                            self.boards.append(newBoard)
                            self.counter +=1
                            result = self.solve()
                            if result:
                                return newBoard
                            self.boards.pop()
                            currentBlock.candidatedForNumber = False
            elif not currentBlock.number:
                # print("set number")
                for num in currentBlock.domainNumber:
                    newBoard = Board(self.n,self.colors,deepcopy(oldBoard.getBoard()))
                    newBoard.getBoard()[currentBlock.id[0]*self.n+currentBlock.id[1]].setNumber(num)
                    newBoard.updateConstraints()
                    checkFlag = newBoard.forwardChecking()
                    if checkFlag:
                        # print(f"{num} is set true")
                        self.boards.append(newBoard)
                        self.counter +=1
                        result = self.solve()
                        if result:
                            return newBoard
                        self.boards.pop()
                        currentBlock.candidatedForNumber = False
            elif not currentBlock.color:
                # print("set color")
                for color in currentBlock.domainColor:
                    newBoard = Board(self.n,self.colors,deepcopy(oldBoard.getBoard()))
                    newBoard.getBoard()[currentBlock.id[0]*self.n+currentBlock.id[1]].setColor(color)
                    newBoard.updateConstraints()
                    checkFlag = newBoard.forwardChecking()
                    if checkFlag:
                        # print(f"{color} is set true")
                        self.boards.append(newBoard)
                        self.counter +=1
                        result = self.solve()
                        if result:
                            return newBoard
                        self.boards.pop()
                        currentBlock.candidatedForColor = False
        print(self.boards[-1])
        return self.boards[-1]

    def showGameStatus(self):
        pass

   
class Board():
    def __init__(self,n,colors,blocksList):
        self.blocksList = blocksList
        self.colors = colors
        self.n = n
    
    def createBoard(self,startString):
        lines = startString.split("\n")
        lines = lines[:-1]
        
        for i, line in enumerate(lines):

            blockProperties = line.split(" ")
            
            for j,blockProperty in enumerate(blockProperties):
                block = Block()
                
                number = blockProperty[0]
                color = blockProperty[1]

                if number!="*":
                    block.setNumber(number)
                    block.primaryNumber=True
                if color!="#":
                    block.setColor(color)
                    block.primaryColor=True

                block.setId(i,j)
                block.startContraints(self.colors,self.n)
                self.blocksList.append(block)

        self.updateConstraints(firstUpdate=True)

        return self

    def updateConstraints(self,firstUpdate=None):
        counterDegree = 0
        for mainBlock in self.blocksList:
            i,j = mainBlock.id

            # constraint in color and number:
            for compareBlock in self.blocksList:
                iCompBlock,jCompBlock = compareBlock.id

                # NUMBER
                if i == iCompBlock or j == jCompBlock:
                    numberCompBlock = compareBlock.number
                    if numberCompBlock in mainBlock.domainNumber and mainBlock.id != compareBlock.id:
                        mainBlock.domainNumber.remove(numberCompBlock)

                # COLOR
                if (i == iCompBlock+1 and j == jCompBlock) or (i == iCompBlock-1 and j == jCompBlock) or (i == iCompBlock and j == jCompBlock + 1) or (i == iCompBlock and j == jCompBlock - 1):
                    colorCompBlock = compareBlock.color
                    if colorCompBlock in mainBlock.domainColor:
                        mainBlock.domainColor.remove(colorCompBlock)

                    if compareBlock.number and compareBlock.color:
                        counterDegree += 1

            currentDegree = mainBlock.primaryDegree
            mainBlock.setConstraintDegree(currentDegree-counterDegree)
            counterDegree = 0

    def getMostConstraintInNumber(self):
        minBlock = None
        minLen = math.inf
        for block in self.blocksList:
            if 0 < len(block.domainNumber) < minLen and not block.primaryNumber and not block.number and not block.candidatedForNumber:
                minBlock = block
                minLen = len(block.domainNumber)
        minBlocksList = [block for block in self.blocksList if len(block.domainNumber) == minLen and not block.primaryNumber and not block.number and not block.candidatedForNumber]
        return minBlocksList

    def getMostConstraintInColor(self):
        minBlock = None
        minLen = math.inf
        for block in self.blocksList:
            if 0 < len(block.domainColor) < minLen and not block.primaryColor and not block.color and not block.candidatedForColor:
                minBlock = block
                minLen = len(block.domainColor)
        blocksListColor = [block for block in self.blocksList if len(block.domainColor) == minLen and not block.primaryColor and not block.color and not block.candidatedForColor]
        return blocksListColor
    
    def forwardChecking(self):
        for block in self.blocksList:
            if block.domainNumber==[] or block.domainColor==[]:
                return False

            i,j = block.id
            for compareBlock in self.blocksList:
                iCompBlock,jCompBlock = compareBlock.id
                if (i == iCompBlock+1 and j == jCompBlock) or (i == iCompBlock-1 and j == jCompBlock) or (i == iCompBlock and j == jCompBlock + 1) or (i == iCompBlock and j == jCompBlock - 1):
                    if block.number and compareBlock.number and block.color and compareBlock.color:
                        if block.number>compareBlock.number:
                            if self.colors.index(block.color) > self.colors.index(compareBlock.color):
                                return False
                        elif block.number<compareBlock.number:
                            if self.colors.index(block.color) < self.colors.index(compareBlock.color):
                                return False
        return True

    def getBoard(self):
        return self.blocksList

    def __str__(self):
        for block in self.blocksList:
            i,j = block.id
            if j==n-1:
                print(str(block.number) + str(block.color))
            else:    
                print(str(block.number) + str(block.color),end =" ")

        # print('*******')
        # for mainBlock in self.blocksList:
        #     print(mainBlock.id , '***' , mainBlock.domainNumber , '***' , mainBlock.domainColor , '***' , mainBlock.constraintDegree)
        # print('*******')
        return ""


class Block():
    def __init__(self):
        self.id = []
        self.color = None
        self.number = 0
        self.domainNumber = []
        self.domainColor = []
        self.constraintDegree = None
        self.primaryDegree = None
        self.primaryColor = False
        self.primaryNumber = False
        self.candidatedForNumber = False
        self.candidatedForColor = False

    def setId(self,i,j):
        self.id.append(i)
        self.id.append(j)
    def setNumber(self,number):
        self.number = int(number)
    def setColor(self,color):
        self.color = color
    def setDomainNumber(self,c):
        self.domainNumber = c
    def setDomainColor(self,c):
        self.domainColor = c
    def setConstraintDegree(self,c):
        self.constraintDegree = c
    def startContraints(self,colors,n):
        self.domainColor = colors[:]
        self.domainNumber = [x+1 for x in range(n)]
        i,j = self.id
        if i==0 or i==n-1 or j==0 or j==n-1:
            if i==j or (i==0 and j==n-1) or (j==0 and i == n-1):
                self.constraintDegree = 2
            else:    
                self.constraintDegree = 3
        else:
            self.constraintDegree = 4
        self.primaryDegree = self.constraintDegree

    def __str__(self):
        print(self.id,self.number,self.color,self.primaryNumber,self.primaryColor)
        return ""


if __name__ == "__main__":
#     n = 3
#     colors = 'r g b y p'
#     colors = colors.split(" ")
#     startString = '''*# *# *#
# *# 3r *#
# *g *# *#
# '''
#     startString = '''*# *# *#
# *# 3r *#
# *# *# *#
# '''
#     startString = '''*# *# *#
# *# *# *#
# *# *# *#
# '''
#     startString = '''1# *# *# *# *#
# *# *# *# 5# *#
# *# 4# *# *# *#
# *# 5# *# *# *#
# 3# *# *# *# 2#
# '''
#     startString = '''1# *# *# 3#
# *# 3# *# *#
# *# 1# *# 4#
# *# *# *# 1#
# '''
#     startString = '''*# *# *# *#
# *# *# *# *#
# *# *# *# *#
# *# *# *# *#
# '''

    firstLine = input()
    m = int(firstLine.split(" ")[0])
    n = int(firstLine.split(" ")[1])

    colors = input()
    colors = colors.split(" ")

    startString = ""
    for i in range(n):
        startString += input() + "\n"

    myGame = Game(n,colors)
    myGame.start(startString)
    myGame.showGameStatus()
    myGame.solve()

