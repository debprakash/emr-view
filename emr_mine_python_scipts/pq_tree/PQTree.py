#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gc
import time
from PQNode import PQNode
from Queue import Queue

SHOW_DEBUG_OUTPUT = False

class PQTree(object):
    """ generated source for PQTree

    """
    root = PQNode()
    leaves = None
    queue = None
    drawWidth = 0
    drawHeight = 0
    hasChanged = bool()
    templateMatchString = ""
    templateTimeString = ""
    reduceString = ""
    pauseInSeconds = 0
    doneReduction = bool()
    cleared = bool()
    constraints = None
    flaggedAsNull = bool()
    
    def __init__(self, param):
        self.init(True)
        if getattr(param, '__iter__', False):
            self.construct_list(param)
        elif type(param) == int:
            self.construct_int(param)
            

    def construct_int(self, universeSize):
        self.init(True)
        aNode = None
        self.leaves = []
        i = 0
        while i < universeSize:
            aNode = PQNode(i)
            self.root.addChild(aNode)
            self.leaves.append(aNode)
            i += 1
    

    def construct_list(self, data = None):
        self.init(True)
        if data:
            save_memory = False
            run_fast = True
            aNode = None
            self.leaves = []
            if save_memory:
                iter = data.iterator()
                count = 0
                while iter.hasNext():
                    aNode = PQNode(iter.next())
                    self.root.addChild(aNode)
                    self.leaves.append(aNode)
                    iter.remove()
                    count += 1
            else:
                if run_fast:
                    i = 0
                    while i < len(data):
                        aNode = PQNode(data[i])
                        self.root.addChild(aNode)
                        self.leaves.append(aNode)
                        i += 1

    def init(self, initLeaves):
        self.hasChanged = True
        self.templateMatchString = ""
        self.templateTimeString = ""
        self.reduceString = ""
        self.doneReduction = True
        self.flaggedAsNull = False
        if self.constraints is not None:
            self.clear()
            self.constraints = None
        self.cleared = True
        self.queue = None
        self.root = PQNode()
        if initLeaves:
            self.leaves = []

    def getRoot(self):
        return self.root

    def setRoot(self, rootNode):
        self.root = rootNode

    def getLeaves(self):
        return self.leaves

    def isNullTree(self):
        return not self.root.hasChildren()

    def getTemplateMatchString(self):
        return self.templateMatchString

    def setTemplateMatchString(self, newString):
        self.templateMatchString = newString

    def getTemplateTimeString(self):
        return self.templateTimeString

    def setTemplateTimeString(self, newString):
        self.templateTimeString = newString

    def getReduceString(self):
        return self.reduceString

    def setConstraints(self, c):
        self.constraints = c

    def getConstraints(self):
        return self.constraints

    def isDoneReduction(self):
        return self.doneReduction and self.cleared

    def isReduced(self):
        return self.doneReduction

    def getLeafAt(self, index):
        return self.leaves[index]

    def resetTree(self):
        self.init(False)
        ## for-while
        i = 0
        while i < len(self.leaves):
            aNode = self.leaves[i]
            aNode.clear(False)
            self.root.addChild(aNode)
            i += 1
        gc.collect()

    def reductionByValue(self, data):
        s = []
        ## for-while
        i = 0
        while i < len(self.leaves):
            if self.leaves[i].getData() in data:
                s.append(self.leaves[i])
            i += 1
        self.reduction(s, 0)


    def reduction(self, s):
        numSteps = 0
        self.constraints = [self.leaves[i] for i in xrange(s[0], s[1] + 1)]
        timeTaken = time.clock()
        previouslyDoneReduction = self.doneReduction
        if self.queue is None:
            self.queue = Queue()
            self.reduceString = "Reduced: { "
            for obj in self.constraints:
                self.queue.enqueue(obj)
                self.reduceString = self.reduceString + str(obj) + " "
            self.reduceString = self.reduceString + "}\n"
            self.bubble(self.queue)
            if SHOW_DEBUG_OUTPUT:
                self.printTree()
            self.queue = None
        if not self.flaggedAsNull:
            if self.doneReduction and self.cleared:
                self.queue = Queue(self.constraints)
                self.reduce(self.queue, len(self.constraints), numSteps)
                if self.queue is None or (len(self.queue) == 0):
                    self.doneReduction = True
                    self.queue = None
                self.cleared = False
                if SHOW_DEBUG_OUTPUT:
                    self.printTree()
            else:
                if self.doneReduction and not self.cleared:
                    self.templateMatchString = ""
                else:
                    if not self.doneReduction:
                        self.reduce(self.queue, len(self.constraints), numSteps)
                        if self.queue is None or (len(self.queue) == 0):
                            self.doneReduction = True
                            self.queue = None
                        if SHOW_DEBUG_OUTPUT:
                            self.printTree()
        if previouslyDoneReduction and self.doneReduction and not self.cleared or (numSteps == 0) or self.flaggedAsNull:
            if self.flaggedAsNull:
                rString = "Could Not Reduce: " + self.reduceString
                tString = self.templateMatchString
                self.init(False)
                self.reduceString = rString
                self.templateMatchString = tString
            if SHOW_DEBUG_OUTPUT:
                print "$$$ Cleaning up $$$"
            self.clear()
        self.hasChanged = True
        if SHOW_DEBUG_OUTPUT:
            self.printTree()
        self.setTemplateTimeString("Time taken in seconds: %.2f\n" % (time.clock() - timeTaken))

    def bubble(self, queue):
        if SHOW_DEBUG_OUTPUT:
            print "$$$ Bubble start $$$"
        blockedNodeVector = []
        blockedSiblings = []
        unblockedSiblings = []
        blockCount = 0
        blockedNodes = 0
        offTheTop = 0
        currentNode = PQNode()
        while len(self.queue) + blockCount + offTheTop > 1:
            if (len(self.queue) == 0):
                break
            currentNode = self.queue.dequeue()
            if not currentNode.isQueued():
                currentNode.setPertinentLeafCount(1)
            if SHOW_DEBUG_OUTPUT:
                print "Checking Bubble for: " + currentNode.infoString()
            currentNode.setBlocked()
            blockedSiblings = currentNode.getBlockedSiblings()
            unblockedSiblings = currentNode.getUnblockedSiblings()
            if len(unblockedSiblings) > 0:
                currentNode.setParent(unblockedSiblings[0].getParent())
                currentNode.setUnblocked()
            else:
                if currentNode.getSiblings() is None or currentNode.getSiblings().size() < 2:
                    currentNode.setUnblocked()
            if not currentNode.isBlocked():
                parentNode = currentNode.getParent()
                list = []
                if len(blockedSiblings) > 0:
                    list = currentNode.getMaximalConsecutiveBlockedSiblings()
                    iterator = list.iterator()
                    while iterator.hasNext():
                        blockedSibling = iterator.next()
                        blockedSibling.setUnblocked()
                        blockedSibling.setParent(parentNode)
                        parentNode.setPertinentChildCount(parentNode.getPertinentChildCount() + 1)
                if parentNode is None:
                    offTheTop = 1
                else:
                    parentNode.setPertinentChildCount(parentNode.getPertinentChildCount() + 1)
                    if not parentNode.isBlocked() and not parentNode.isQueued():
                        self.queue.enqueue(parentNode)
                        parentNode.setQueued()
                        if SHOW_DEBUG_OUTPUT:
                            print "  Adding this to the end of queue: " + parentNode.infoString()
                blockCount -= len(blockedSiblings)
                blockedNodes -= len(list)
            else:
                blockedNodeVector.append(currentNode)
                blockCount -= len(blockedSiblings) - 1
                blockedNodes += 1
        if (blockCount == 1) and blockedNodes > 1:
            pseudoNode = PQNode()
            pseudoNode.convertToQNode()
            pseudoNode.setPertinentChildCount(blockedNodes)
            pseudoNode.pseudoNode()
            aBlockedNode = None
            ## for-while
            i = 0
            while i < len(blockedNodeVector):
                aBlockedNode = blockedNodeVector[i]
                if aBlockedNode.isBlocked() and not aBlockedNode.isDeleted():
                    pseudoNode.addChild(aBlockedNode, False)
                i += 1
        else:
            if blockCount > 1:
                self.flaggedAsNull = True
                self.templateMatchString = "Templates Matched: {NONE}\n"
                self.reduceString = "Could Not educed: {"
        self.hasChanged = True
        if SHOW_DEBUG_OUTPUT:
            print "$$$ Bubble end $$$"

    def reduce(self, queue, pertinentCount, numSteps):
        if SHOW_DEBUG_OUTPUT:
            print "$$$ Reduce start $$$"
        currentNode = PQNode()
        count = 0
        if self.doneReduction:
            self.templateMatchString = "Templates Matched: {"
            self.doneReduction = False
        else:
            self.templateMatchString = ""
        while len(self.queue) > 0:
            if (numSteps != 0):
                if (numSteps == count):
                    break
                count += 1
            currentNode = self.queue.dequeue()
            if SHOW_DEBUG_OUTPUT:
                print "  Checking Template matches for: " + currentNode.infoString()
            if currentNode.getPertinentLeafCount() < pertinentCount and (pertinentCount != 1):
                parentNode = currentNode.getParent()
                parentNode.setPertinentLeafCount(parentNode.getPertinentLeafCount() + currentNode.getPertinentLeafCount())
                parentNode.setPertinentChildCount(parentNode.getPertinentChildCount() - 1)
                if (parentNode.getPertinentChildCount() == 0):
                    self.queue.enqueue(parentNode)
                    if SHOW_DEBUG_OUTPUT:
                        print "  Adding this to the end of queue: " + parentNode.infoString()
                if not self.templateL1(currentNode):
                    if not self.templateP1(currentNode):
                        if not self.templateP3(currentNode):
                            if not self.templateP5(currentNode):
                                if not self.templateQ1(currentNode):
                                    if not self.templateQ2(currentNode):
                                        if SHOW_DEBUG_OUTPUT:
                                            print "    *** NO MATCH FOUND1 ***"
                                        tempString = self.templateMatchString
                                        self.flaggedAsNull = True
                                        self.templateMatchString = tempString + "NONE"
                                        break
                                    else:
                                        self.templateMatchString = self.templateMatchString + "Q2, "
                                else:
                                    self.templateMatchString = self.templateMatchString + "Q1, "
                            else:
                                self.templateMatchString = self.templateMatchString + "P5, "
                        else:
                            self.templateMatchString = self.templateMatchString + "P3, "
                    else:
                        self.templateMatchString = self.templateMatchString + "P1, "
                else:
                    self.templateMatchString = self.templateMatchString + "L1, "
            else:
                if not self.templateL1(currentNode):
                    if not self.templateP1(currentNode):
                        if not self.templateP2(currentNode):
                            if not self.templateP4(currentNode):
                                if not self.templateP6(currentNode):
                                    if not self.templateQ1(currentNode):
                                        if not self.templateQ2(currentNode):
                                            if not self.templateQ3(currentNode):
                                                if SHOW_DEBUG_OUTPUT:
                                                    print "    *** NO MATCH FOUND2 ***"
                                                tempString = self.templateMatchString
                                                self.flaggedAsNull = True
                                                self.templateMatchString = tempString + "NONE"
                                                break
                                            else:
                                                self.templateMatchString = self.templateMatchString + "Q3"
                                        else:
                                            self.templateMatchString = self.templateMatchString + "Q2"
                                    else:
                                        self.templateMatchString = self.templateMatchString + "Q1"
                                else:
                                    self.templateMatchString = self.templateMatchString + "P6"
                            else:
                                self.templateMatchString = self.templateMatchString + "P4"
                        else:
                            self.templateMatchString = self.templateMatchString + "P2"
                    else:
                        self.templateMatchString = self.templateMatchString + "P1"
                else:
                    self.templateMatchString = self.templateMatchString + "L1"
            self.hasChanged = True
            if SHOW_DEBUG_OUTPUT:
                self.printTree()
        if SHOW_DEBUG_OUTPUT:
            print "$$$ Reduce end $$$"
        if (len(self.queue) == 0) or self.flaggedAsNull:
            self.templateMatchString = self.templateMatchString + "}\n"

    def templateL1(self, currentNode):
        if SHOW_DEBUG_OUTPUT:
            print "Trying Template L1"
        if not currentNode.hasChildren():
            currentNode.labelAsFull()
            if SHOW_DEBUG_OUTPUT:
                print "    Matched Template L1"
            return True
        return False

    def templateP1(self, currentNode):
        if SHOW_DEBUG_OUTPUT:
            print "Trying Template P1"
        if currentNode.isPNode():
            if (currentNode.getNumChildren() == currentNode.getNumFullChildren()):
                currentNode.labelAsFull()
                if SHOW_DEBUG_OUTPUT:
                    print "    Matched Template P1"
                return True
        return False

    def templateP2(self, currentNode):
        if SHOW_DEBUG_OUTPUT:
            print "Trying Template P2"
        if currentNode.isPNode() and (currentNode.getNumPartialChildren() == 0) and currentNode.getNumFullChildren() > 0:
            if currentNode.getNumFullChildren() > 1 and currentNode.getNumEmptyChildren() > 0:
                newNode = PQNode()
                newNode.labelAsFull()
                currentNode.moveFullChildrenTo(newNode)
                currentNode.addChild(newNode)
            if SHOW_DEBUG_OUTPUT:
                print "    Matched Template P2"
            return True
        return False

    def templateP3(self, currentNode):
        if SHOW_DEBUG_OUTPUT:
            print "Trying Template P3"
        if currentNode.isPNode() and (currentNode.getNumPartialChildren() == 0) and currentNode.getNumFullChildren() > 0:
            newNode = PQNode()
            newNode = PQNode()
            newNode.convertToQNode()
            newNode.labelAsPartial()
            if currentNode.getNumFullChildren() > 1:
                groupNode = PQNode()
                groupNode.labelAsFull()
                currentNode.moveFullChildrenTo(groupNode)
                newNode.addChild(groupNode)
            else:
                newNode.addChild(currentNode.removeOnlyFullChild())
            currentNode.getParent().replaceChild(currentNode, newNode)
            if currentNode.getNumEmptyChildren() > 1:
                currentNode.clear(False)
                newNode.addChild(currentNode)
            else:
                newNode.addChild(currentNode.removeOnlyEmptyChild())
            if SHOW_DEBUG_OUTPUT:
                print "    Matched Template P3"
            return True
        return False

    def templateP4(self, currentNode):
        if SHOW_DEBUG_OUTPUT:
            print "Trying Template P4"
        if currentNode.isPNode() and (currentNode.getNumPartialChildren() == 1):
            partialChild = currentNode.getPartialChild(0)
            if currentNode.getNumFullChildren() > 0:
                newNode = PQNode()
                if currentNode.getNumFullChildren() > 1:
                    newNode = PQNode()
                    newNode.labelAsFull()
                    currentNode.moveFullChildrenTo(newNode)
                else:
                    newNode = currentNode.removeOnlyFullChild()
                partialChild.addChild(newNode)
            if currentNode.hasOnlyOneChild():
                if currentNode.getParent() is not None:
                    if currentNode.getParent().isDeleted():
                        currentNode.becomeChild(partialChild)
                    else:
                        currentNode.getParent().replaceChild(currentNode, partialChild)
                        currentNode.delete()
                else:
                    partialChild.becomeRoot()
                    self.setRoot(partialChild)
            if SHOW_DEBUG_OUTPUT:
                print "    Matched Template P4"
            return True
        return False

    def templateP5(self, currentNode):
        if SHOW_DEBUG_OUTPUT:
            print "Trying Template P5"
        if currentNode.isPNode() and (currentNode.getNumPartialChildren() == 1):
            partialChild = currentNode.getPartialChild(0)
            currentNode.removeChild(partialChild)
            if currentNode.getNumFullChildren() > 0:
                newNode = PQNode()
                if currentNode.getNumFullChildren() > 1:
                    newNode = PQNode()
                    newNode.labelAsFull()
                    currentNode.moveFullChildrenTo(newNode)
                else:
                    newNode = currentNode.removeOnlyFullChild()
                partialChild.addChild(newNode)
            if currentNode.getNumEmptyChildren() > 0:
                newNode = PQNode()
                if (currentNode.getNumEmptyChildren() == 1):
                    newNode = currentNode.removeOnlyEmptyChild()
                    currentNode.getParent().replaceChild(currentNode, partialChild)
                    currentNode.delete()
                else:
                    currentNode.getParent().replaceChild(currentNode, partialChild)
                    currentNode.clear(False)
                    newNode = currentNode
                partialChild.addChild(newNode)
            else:
                currentNode.getParent().replaceChild(currentNode, partialChild)
                currentNode.delete()
            if SHOW_DEBUG_OUTPUT:
                print "    Matched Template P5"
            return True
        return False

    def templateP6(self, currentNode):
        if SHOW_DEBUG_OUTPUT:
            print "Trying Template P6"
        if currentNode.isPNode() and (currentNode.getNumPartialChildren() == 2):
            partialChild1 = currentNode.getPartialChild(0)
            partialChild2 = currentNode.getPartialChild(1)
            if not partialChild1.checkFullAreEndMost() and partialChild2.checkFullAreEndMost():
                return False
            partialChild1.setPertinentLeafCount(currentNode.getPertinentLeafCount())
            if currentNode.getNumFullChildren() > 0:
                newNode = None
                if currentNode.getNumFullChildren() > 1:
                    newNode = PQNode()
                    newNode.labelAsFull()
                    currentNode.moveFullChildrenTo(newNode)
                else:
                    newNode = currentNode.removeOnlyFullChild()
                partialChild1.addChild(newNode)
            currentNode.mergePartialChildren(partialChild2, partialChild1)
            partialChild2.delete()
            if currentNode.hasOnlyOneChild():
                if currentNode.getParent() is not None:
                    if currentNode.getParent().isDeleted():
                        currentNode.becomeChild(partialChild1)
                    else:
                        currentNode.getParent().replaceChild(currentNode, partialChild1)
                        currentNode.delete()
                else:
                    partialChild1.becomeRoot()
                    self.setRoot(partialChild1)
            if SHOW_DEBUG_OUTPUT:
                print "    Matched Template P6"
            return True
        return False

    def templateQ1(self, currentNode):
        if SHOW_DEBUG_OUTPUT:
            print "Trying Template Q1"
        if currentNode.isQNode() and not currentNode.isPseudoNode():
            if currentNode.childrenAreFull():
                currentNode.labelAsFull()
                if SHOW_DEBUG_OUTPUT:
                    print "    Matched Template Q1"
                return True
        return False

    def templateQ2(self, currentNode):
        if SHOW_DEBUG_OUTPUT:
            print "Trying Template Q2"
        if currentNode.isQNode() and currentNode.getNumPartialChildren() <= 1 and not currentNode.isPseudoNode():
            if not currentNode.checkFullAreAdjacent():
                return False
            if currentNode.checkEndMostAreEmptyOrPartial() and (currentNode.getNumFullChildren() != 0):
                return False
            currentNode.labelAsPartial()
            if (currentNode.getNumPartialChildren() == 1):
                endMostChildren = currentNode.getEndMostChildren()
                partialChild = currentNode.getPartialChild(0)
                if not currentNode.checkFullAreAdjacentTo(partialChild):
                    return False
                if (currentNode.getNumFullChildren() == 0) and (partialChild not in endMostChildren):
                    return False
                if not partialChild.checkFullAreEndMost():
                    return False
                currentNode.absorbPartialChild(partialChild)
            if SHOW_DEBUG_OUTPUT:
                print "    Matched Template Q2"
            return True
        return False

    def templateQ3(self, currentNode):
        if SHOW_DEBUG_OUTPUT:
            print "Trying Template Q3"
        if currentNode.isQNode() and currentNode.getNumPartialChildren() <= 2:
            if not currentNode.isPseudoNode() and not currentNode.checkEndMostAreEmptyOrPartial():
                return False
            currentNode.labelAsPartial()
            if (currentNode.getNumPartialChildren() == 1):
                partialChild = currentNode.getPartialChild(0)
                if not currentNode.checkFullAreAdjacentTo(partialChild):
                    return False
                if not partialChild.checkFullAreEndMost():
                    return False
                if currentNode.isPseudoNode() and not currentNode.checkPartialAreAtEnds():
                    return False
                currentNode.absorbPartialChild(partialChild)
            else:
                if (currentNode.getNumPartialChildren() == 2):
                    partialChild1 = currentNode.getPartialChild(0)
                    partialChild2 = currentNode.getPartialChild(1)
                    if (currentNode.getNumFullChildren() == 0) and (partialChild2 not in partialChild1.getSiblings()) and (partialChild1 in partialChild2.getSiblings()):
                        return False
                    if not partialChild1.checkFullAreEndMost() or not partialChild2.checkFullAreEndMost():
                        return False
                    if not currentNode.checkFullAreAdjacentTo(partialChild1) and currentNode.checkFullAreAdjacentTo(partialChild2):
                        return False
                    if currentNode.isPseudoNode() and not currentNode.checkPartialAreAtEnds():
                        return False
                    currentNode.absorbPartialChild(partialChild1)
                    currentNode.absorbPartialChild(partialChild2)
            if currentNode.isPseudoNode():
                currentNode.delete()
            if SHOW_DEBUG_OUTPUT:
                print "    Matched Template Q3"
            return True
        return False

    def printFrontier(self):
        self.leaves = self.getLeaves()
        ## for-while
        i = 0
        while i < len(self.leaves):
            print self.leaves[i]
            i += 1

    def printTree(self):
        print "$$$ PRINT TREE START $$$"
        self.root.printStructure()
        print "$$$ PRINT TREE END $$$"

    def getNumNodes(self):
        return self.root.countSubNodes()

    def getNumDeletedNodes(self):
        return self.root.countSubDeletedNodes()


    def clear(self, s = None):
        self.cleared = True
        if s == None: s = self.constraints 
        if s is not None:
            ## for-while
            j = 0
            while j < len(s):
                s[j].clear()
                j += 1




