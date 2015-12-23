#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
from SiblingVector import SiblingVector

pq_counter = 0

class PQNode(object):
    """ generated source for PQNode

    """
    LABEL_EMPTY = 0
    LABEL_PARTIAL = 1
    LABEL_FULL = 2
    TYPE_PNODE = 0
    TYPE_QNODE = 1
    label = 0
    blocked = bool()
    queued = bool()
    type = 0
    pertinentChildCount = 0
    pertinentLeafCount = 0
    parent = None
    left = None
    right = None
    fullLeft = None
    fullRight = None
    partialLeft = None
    partialRight = None
    childCount = 0
    fullChildCount = 0
    partialChildCount = 0
    data = None
    deleted = bool()
    pseudoNode = bool()
    endMostChildren = None
    siblings = None
    childAccessNode = None
    fullChildAccessNode = None
    partialChildAccessNode = None
    subLeafCount = 0
    depth = 0
    childBounds = 0
    leftBound = 0


    def init(self, pNode = True):
        self.childAccessNode = None
        self.fullChildAccessNode = None
        self.partialChildAccessNode = None
        self.endMostChildren = None
        self.siblings = None
        self.childCount = 0
        self.fullChildCount = 0
        self.partialChildCount = 0
        self.label = self.LABEL_EMPTY
        self.pertinentChildCount = 0
        self.pertinentLeafCount = 0
        self.queued = False
        self.parent = None
        self.left = None
        self.right = None
        self.fullLeft = None
        self.fullRight = None
        self.partialLeft = None
        self.partialRight = None
        if pNode:
            self.type = self.TYPE_PNODE
        else:
            self.type = self.TYPE_QNODE
        self.data = None
        self.deleted = False
        self.pseudoNode = False
        
        global pq_counter
        self.internal_id = pq_counter
        pq_counter += 1

    def __init__(self, data = None):
        self.init(True)
        if data != None:
            self.data = data

    def getPertinentChildCount(self):
        return self.pertinentChildCount

    def setPertinentChildCount(self, value):
        self.pertinentChildCount = value

    def getPertinentLeafCount(self):
        return self.pertinentLeafCount

    def setPertinentLeafCount(self, value):
        self.pertinentLeafCount = value

    def isPseudoNode(self):
        return self.pseudoNode

    def pseudoNode(self):
        self.pseudoNode = True
        self.childBounds = 0
        self.leftBound = sys.maxint
        self.subLeafCount = self.pertinentChildCount

    def isDeleted(self):
        return self.deleted

    def delete(self):
        self.init(False)
        self.deleted = True

    def getParent(self):
        return self.parent

    def setParent(self, theParent):
        self.parent = theParent

    def getSiblings(self):
        return self.siblings

    def getNumFullChildren(self):
        return self.fullChildCount

    def getNumPartialChildren(self):
        return self.partialChildCount

    def isQNode(self):
        return (self.type == self.TYPE_QNODE)

    def isPNode(self):
        return (self.type == self.TYPE_PNODE)

    def isFull(self):
        return (self.label == self.LABEL_FULL)

    def isPartial(self):
        return (self.label == self.LABEL_PARTIAL)

    def isEmpty(self):
        return (self.label == self.LABEL_EMPTY)

    def isBlocked(self):
        return self.blocked

    def setBlocked(self):
        self.blocked = True

    def setUnblocked(self):
        self.blocked = False

    def setQueued(self):
        self.queued = True

    def isQueued(self):
        return self.queued

    def getData(self):
        return self.data

    def getLabel(self):
        return self.label

    def getEndMostChildren(self):
        return self.endMostChildren

    def becomeRoot(self):
        self.parent = None

    def getDepth(self):
        return self.depth

    def getNumChildren(self):
        if self.isQNode():
            raise Exception("*** Warning, Qnodes do not store num children")
        return self.childCount

    def getNumEmptyChildren(self):
        if self.isQNode():
            raise Exception("*** Warning, Qnodes do not store num (empty) children")
        return self.childCount - self.fullChildCount - self.partialChildCount

    def convertToQNode(self):
        self.type = self.TYPE_QNODE
        self.endMostChildren = []
        if self.childCount > 0:
            raise Exception("*** ERROR cannot convert to qnode unless no children present!")


    def convertToPNode(self):
        self.type = self.TYPE_PNODE
        self.endMostChildren = None

    def labelAsFull(self):
        if not self.isFull():
            if self.parent is not None:
                self.parent.removeChild(self, False)
            self.label = self.LABEL_FULL
            if self.parent is not None:
                self.parent.addChild(self, False)

    def labelAsPartial(self):
        if not self.isPartial():
            if self.parent is not None:
                self.parent.removeChild(self, False)
            self.label = self.LABEL_PARTIAL
            if self.parent is not None:
                self.parent.addChild(self, False)

    def labelAsEmpty(self):
        if not self.isEmpty():
            if self.parent is not None:
                self.parent.removeChild(self, False)
            self.label = self.LABEL_EMPTY
            if self.parent is not None:
                self.parent.addChild(self, False)

    def hasChildren(self):
        if self.isPNode():
            return self.childCount > 0
        else:
            if self.isQNode():
                return len(self.endMostChildren) > 0
            else:
                return False

    def getAllChildren(self):
        allVector = []
        if self.isPNode():
            if self.hasChildren():
                currentNode = self.childAccessNode
                while True:
                    allVector.append(currentNode)
                    if currentNode is None:
                        print "parent of crap: " + self.infoString()
                    currentNode = currentNode.right
                    if (currentNode == self.childAccessNode):
                        break
        else:
            if self.isQNode():
                if self.hasChildren():
                    previousNode = None
                    currentNode = self.endMostChildren[0]
                    nextNode = PQNode()
                    lastNode = None
                    if self.isPseudoNode():
                        if currentNode.siblings.siblingAt(0) is not None and (currentNode.siblings.siblingAt(0).parent != self):
                            previousNode = currentNode.siblings.siblingAt(0)
                        else:
                            if currentNode.siblings.siblingAt(1) is not None and (currentNode.siblings.siblingAt(1).parent != self):
                                previousNode = currentNode.siblings.siblingAt(1)
                        if len(self.endMostChildren) > 1:
                            tempNode = self.endMostChildren[1]
                            if tempNode.siblings.siblingAt(0) is not None and (tempNode.siblings.siblingAt(0).parent != self):
                                lastNode = tempNode.siblings.siblingAt(0)
                            else:
                                if tempNode.siblings.siblingAt(1) is not None and (tempNode.siblings.siblingAt(1).parent != self):
                                    lastNode = tempNode.siblings.siblingAt(1)
                    while True:
                        allVector.append(currentNode)
                        nextNode = currentNode.siblings.nextSibling(previousNode)
                        previousNode = currentNode
                        currentNode = nextNode
                        if (currentNode == lastNode):
                            break
        return allVector

    def moveFullChildrenTo(self, newNode):
        if self.isPNode():
            if self.fullChildCount > 0:
                currentNode = self.fullChildAccessNode
                nextNode = PQNode()
                while True:
                    nextNode = currentNode.fullRight
                    self.removeChild(currentNode)
                    newNode.addChild(currentNode)
                    currentNode = nextNode
                    if self.fullChildAccessNode is None:
                        break
        else:
            raise Exception("*** ERROR move full children method not meant for children of q nodes!")


    def getPartialChild(self, index):
        if index + 1 > self.partialChildCount:
            raise Exception("*** ERROR tried to get a partial child that does not exist! [" + index + "]")

        if (index == 0):
            return self.partialChildAccessNode
        else:
            if (index == 1):
                return self.partialChildAccessNode.partialRight
            else:
                raise Exception("*** ERROR tried to get a partial child that does not exist! [" + index + "]")


    def removeOnlyFullChild(self):
        if self.isPNode():
            if (self.fullChildCount != 1):
                raise Exception("*** ERROR not exactly one full child to remove! " + self.fullChildCount)

            returnNode = self.fullChildAccessNode
            self.removeChild(returnNode)
            return returnNode
        else:
            raise Exception("*** ERROR remove only full child is only meant for p nodes!")


    def removeOnlyEmptyChild(self):
        if self.isPNode():
            if (self.getNumEmptyChildren() != 1):
                raise Exception("*** ERROR not exactly one empty child to remove! " + self.getNumEmptyChildren())

            returnNode = self.childAccessNode
            while True:
                if returnNode.isEmpty():
                    break
                returnNode = returnNode.right
                if (returnNode == self.childAccessNode):
                    break
            self.removeChild(returnNode)
            return returnNode
        else:
            raise Exception("*** ERROR remove only empty child is only meant for p nodes!")


    def addChild(self, pq, modify = True):
        if pq.isFull():
            self.fullChildCount += 1
            pq.fullLeft = None
            pq.fullRight = None
            if self.fullChildAccessNode is None:
                self.fullChildAccessNode = pq
                self.fullChildAccessNode.fullLeft = self.fullChildAccessNode
                self.fullChildAccessNode.fullRight = self.fullChildAccessNode
            else:
                pq.fullLeft = self.fullChildAccessNode.fullLeft
                pq.fullLeft.fullRight = pq
                self.fullChildAccessNode.fullLeft = pq
                pq.fullRight = self.fullChildAccessNode
                self.fullChildAccessNode = pq
        else:
            if pq.isPartial():
                self.partialChildCount += 1
                pq.partialLeft = None
                pq.partialRight = None
                if self.partialChildAccessNode is None:
                    self.partialChildAccessNode = pq
                    self.partialChildAccessNode.partialLeft = self.partialChildAccessNode
                    self.partialChildAccessNode.partialRight = self.partialChildAccessNode
                else:
                    pq.partialLeft = self.partialChildAccessNode.partialLeft
                    pq.partialLeft.partialRight = pq
                    self.partialChildAccessNode.partialLeft = pq
                    pq.partialRight = self.partialChildAccessNode
                    self.partialChildAccessNode = pq
        if self.isPNode() and modify:
            pq.parent = self
            self.childCount += 1
            pq.left = None
            pq.right = None
            pq.siblings = None
            if self.childAccessNode is None:
                self.childAccessNode = pq
                self.childAccessNode.left = self.childAccessNode
                self.childAccessNode.right = self.childAccessNode
            else:
                pq.left = self.childAccessNode.left
                pq.left.right = pq
                self.childAccessNode.left = pq
                pq.right = self.childAccessNode
                self.childAccessNode = pq
        else:
            if self.isQNode() and modify:
                pq.parent = self
                sibling = None
                if pq.siblings is not None:
                    if pq.siblings.siblingAt(0) is not None and self.endMostChildren.contains(pq.siblings.siblingAt(0)):
                        sibling = pq.siblings.siblingAt(0)
                    else:
                        if pq.siblings.siblingAt(1) is not None and self.endMostChildren.contains(pq.siblings.siblingAt(1)):
                            sibling = pq.siblings.siblingAt(1)
                else:
                    pq.siblings = SiblingVector()
                if sibling is None:
                    ## for-while
                    i = 0
                    while i < len(self.endMostChildren):
                        if (self.endMostChildren[i].label == pq.label):
                            sibling = self.endMostChildren[i]
                            break
                        else:
                            if self.endMostChildren[i].isFull() and pq.isPartial():
                                sibling = self.endMostChildren[i]
                                break
                            else:
                                if self.endMostChildren[i].isPartial() and pq.isFull():
                                    sibling = self.endMostChildren[i]
                                    break
                        i += 1
                if sibling is None and len(self.endMostChildren) > 0:
                    sibling = self.endMostChildren[0]
                if sibling is not None:
                    if len(self.endMostChildren) > 1:
                        self.endMostChildren.remove(sibling)
                    self.endMostChildren.append(pq)
                    sibling.siblings.addSibling(pq)
                    pq.siblings.addSibling(sibling)
                else:
                    self.endMostChildren.append(pq)
            else:
                if self.isQNode() and self.isPseudoNode():
                    pq.parent = self
                    if self.childAccessNode is None:
                        self.childAccessNode = pq
                    if pq.siblings is not None and (len(pq.siblings) == 2):
                        if not pq.siblings.siblingAt(0).parent.isPseudoNode() and pq.siblings.siblingAt(1).parent.isPseudoNode():
                            self.endMostChildren.append(pq)
                    else:
                        raise Exception("*** ERROR invalid child being added to pseudonode!")


    def absorbPartialChild(self, partialChild):
        if self.isQNode() and partialChild.isQNode() and partialChild.isPartial():
            fullConnectChild = partialChild.siblings.siblingAt(0)
            if not fullConnectChild.isFull() and not fullConnectChild.isPartial():
                fullConnectChild = partialChild.siblings.siblingAt(1)
                if fullConnectChild is not None and not fullConnectChild.isFull() and not fullConnectChild.isPartial():
                    fullConnectChild = None
            emptyConnectChild = partialChild.siblings.siblingAt(0)
            if not emptyConnectChild.isEmpty():
                emptyConnectChild = partialChild.siblings.siblingAt(1)
                if emptyConnectChild is not None and not emptyConnectChild.isEmpty():
                    emptyConnectChild = None
            fullJoinChild = partialChild.endMostChildren[0]
            if not fullJoinChild.isFull():
                fullJoinChild = None
                if len(partialChild.endMostChildren) > 1:
                    fullJoinChild = partialChild.endMostChildren[1]
                    if not fullJoinChild.isFull():
                        fullJoinChild = None
            emptyJoinChild = partialChild.endMostChildren[0]
            if not emptyJoinChild.isEmpty():
                emptyJoinChild = None
                if len(partialChild.endMostChildren) > 1:
                    emptyJoinChild = partialChild.endMostChildren[1]
                    if not emptyJoinChild.isEmpty():
                        emptyJoinChild = None
            if fullJoinChild is None or emptyJoinChild is None:
                raise Exception("*** ERROR invalid partial child in absorb partial child!")

            if fullConnectChild is not None:
                fullJoinChild.siblings.addSibling(fullConnectChild)
                fullConnectChild.siblings.removeSibling(partialChild)
                fullConnectChild.siblings.addSibling(fullJoinChild)
            else:
                if not self.endMostChildren.remove(partialChild):
                    raise Exception("*** ERROR could not absorb partial child!")

                fullJoinChild.parent = self
                self.endMostChildren.append(fullJoinChild)
            if emptyConnectChild is not None:
                emptyJoinChild.siblings.addSibling(emptyConnectChild)
                emptyConnectChild.siblings.removeSibling(partialChild)
                emptyConnectChild.siblings.addSibling(emptyJoinChild)
            else:
                if not self.endMostChildren.remove(partialChild):
                    raise Exception("*** ERROR could not absorb partial child!")

                emptyJoinChild.parent = self
                self.endMostChildren.append(emptyJoinChild)
            if partialChild.fullChildCount > 0:
                currentNode = partialChild.fullChildAccessNode
                nextNode = PQNode()
                while True:
                    nextNode = currentNode.fullRight
                    partialChild.removeChild(currentNode, False)
                    self.addChild(currentNode, False)
                    currentNode.parent = self
                    if (nextNode != currentNode):
                        currentNode = nextNode
                    else:
                        break
                    if partialChild.fullChildAccessNode is None:
                        break
            self.removeChild(partialChild, False)
            partialChild.delete()


    def removeChild(self, pq, modify = True):
        if pq.isFull():
            self.fullChildCount -= 1
            if (pq.fullRight == pq):
                pq.fullRight = None
                pq.fullLeft = None
                self.fullChildAccessNode = None
            else:
                if (pq == self.fullChildAccessNode):
                    self.fullChildAccessNode = self.fullChildAccessNode.fullRight
                pq.fullRight.fullLeft = pq.fullLeft
                pq.fullLeft.fullRight = pq.fullRight
                pq.fullLeft = None
                pq.fullRight = None
        else:
            if pq.isPartial():
                self.partialChildCount -= 1
                if (pq.partialRight == pq):
                    pq.partialRight = None
                    pq.partialLeft = None
                    self.partialChildAccessNode = None
                else:
                    if (pq == self.partialChildAccessNode):
                        self.partialChildAccessNode = self.partialChildAccessNode.partialRight
                    pq.partialRight.partialLeft = pq.partialLeft
                    pq.partialLeft.partialRight = pq.partialRight
                    pq.partialLeft = None
                    pq.partialRight = None
        if self.isPNode() and modify:
            pq.parent = None
            self.childCount -= 1
            if (pq == self.childAccessNode):
                if (pq.right == pq):
                    pq.right = None
                    pq.left = None
                    self.childAccessNode = None
                else:
                    self.childAccessNode = self.childAccessNode.right
                    pq.right.left = pq.left
                    pq.left.right = pq.right
                    pq.left = None
                    pq.right = None
            else:
                pq.right.left = pq.left
                pq.left.right = pq.right
                pq.left = None
                pq.right = None
        else:
            if self.isQNode() and modify:
                pq.parent = None
                if pq.siblings.siblingAt(1) is None:
                    self.endMostChildren.remove(pq)
                    if pq.siblings.siblingAt(0) is not None:
                        if not self.endMostChildren.contains(pq.siblings.siblingAt(0)):
                            self.endMostChildren.append(pq.siblings.siblingAt(0))
                        pq.siblings.siblingAt(0).siblings.removeSibling(pq)
                        pq.siblings = None
                else:
                    pq.siblings.siblingAt(0).siblings.removeSibling(pq)
                    pq.siblings.siblingAt(1).siblings.removeSibling(pq)
                    pq.siblings = None


    def replaceChild(self, oldPQNode, newPQNode, modify = True):
        if self.isQNode():
            newPQNode.siblings = oldPQNode.siblings
            if oldPQNode.siblings.siblingAt(0) is not None:
                oldPQNode.siblings.siblingAt(0).siblings.replaceSibling(oldPQNode, newPQNode)
            if oldPQNode.siblings.siblingAt(1) is not None:
                oldPQNode.siblings.siblingAt(1).siblings.replaceSibling(oldPQNode, newPQNode)
            if self.endMostChildren.remove(oldPQNode):
                self.endMostChildren.append(newPQNode)
        else:
            newPQNode.left = oldPQNode.left
            if oldPQNode.left is not None:
                oldPQNode.left.right = newPQNode
            newPQNode.right = oldPQNode.right
            if oldPQNode.right is not None:
                oldPQNode.right.left = newPQNode
        newPQNode.parent = self
        self.removeChild(oldPQNode, False)
        self.addChild(newPQNode, False)
        if (self.childAccessNode == oldPQNode):
            self.childAccessNode = newPQNode
        if modify:
            oldPQNode.fullLeft = None
            oldPQNode.fullRight = None
            oldPQNode.partialLeft = None
            oldPQNode.partialRight = None
            oldPQNode.parent = None
            if self.isQNode():
                oldPQNode.siblings = None
            else:
                oldPQNode.left = None
                oldPQNode.right = None
        return True

    def becomeChild(self, theChild):
        self.childAccessNode = theChild.childAccessNode
        self.fullChildAccessNode = theChild.fullChildAccessNode
        self.partialChildAccessNode = theChild.partialChildAccessNode
        self.endMostChildren = theChild.endMostChildren
        self.childCount = theChild.childCount
        self.fullChildCount = theChild.fullChildCount
        self.partialChildCount = theChild.partialChildCount
        self.pertinentChildCount = theChild.pertinentChildCount
        self.pertinentLeafCount = theChild.pertinentLeafCount
        self.type = theChild.type
        self.data = theChild.data
        self.deleted = theChild.deleted
        self.pseudoNode = theChild.pseudoNode
        if self.isPNode():
            raise Exception("*** ERROR Nodes are only meant to assume the identity of one of their Q-Node children!")
        else:
            if self.isQNode():
                ## for-while
                i = 0
                while i < len(self.endMostChildren):
                    self.endMostChildren[i].parent = self
                    i += 1
                if self.fullChildCount > 0:
                    currentNode = self.fullChildAccessNode
                    nextNode = PQNode()
                    while True:
                        nextNode = currentNode.fullRight
                        currentNode.parent = self
                        if (nextNode != currentNode):
                            currentNode = nextNode
                        else:
                            break
                        if (currentNode == self.fullChildAccessNode):
                            break
        theChild.delete()

    def mergePartialChildren(self, partialChild1, partialChild2):
        if partialChild1.isPartial() and partialChild2.isPartial():
            endMostChildren1 = partialChild1.getEndMostChildren()
            endMostChildren2 = partialChild2.getEndMostChildren()
            if (len(endMostChildren1) == 2) and (len(endMostChildren2) == 2):
                tempNode = PQNode()
                fullEndMostNode1 = None
                emptyEndMostNode1 = None
                ## for-while
                i = 0
                while i < len(endMostChildren1):
                    tempNode = endMostChildren1[i]
                    if tempNode.isFull():
                        fullEndMostNode1 = tempNode
                    else:
                        if tempNode.isEmpty():
                            emptyEndMostNode1 = tempNode
                    i += 1
                fullEndMostNode2 = None
                emptyEndMostNode2 = None
                ## for-while
                i = 0
                while i < len(endMostChildren2):
                    tempNode = endMostChildren2[i]
                    if tempNode.isFull():
                        fullEndMostNode2 = tempNode
                    else:
                        if tempNode.isEmpty():
                            emptyEndMostNode2 = tempNode
                    i += 1
                if fullEndMostNode1 is not None and emptyEndMostNode1 is not None and fullEndMostNode2 is not None and emptyEndMostNode2 is not None:
                    fullEndMostNode1.parent = partialChild2
                    emptyEndMostNode1.parent = partialChild2
                    fullEndMostNode1.siblings.addSibling(fullEndMostNode2)
                    fullEndMostNode2.siblings.addSibling(fullEndMostNode1)
                    endMostChildren2.remove(fullEndMostNode2)
                    endMostChildren2.append(emptyEndMostNode1)
                    endMostChildren1.remove(fullEndMostNode1)
                    endMostChildren1.remove(emptyEndMostNode1)
                    if partialChild1.fullChildCount > 0:
                        currentNode = partialChild1.fullChildAccessNode
                        nextNode = PQNode()
                        while True:
                            nextNode = currentNode.fullRight
                            partialChild1.removeChild(currentNode, False)
                            partialChild2.addChild(currentNode, False)
                            currentNode.parent = partialChild2
                            if (nextNode != currentNode):
                                currentNode = nextNode
                            else:
                                break
                            if partialChild1.fullChildAccessNode is None:
                                break
                    self.removeChild(partialChild1)
                else:
                    raise Exception("*** ERROR merge children were not partial!")
            else:
                raise Exception("*** ERROR merge children were not partial!")
        else:
            raise Exception("*** ERROR merge only meant for partial children!")

    def getMaximalConsecutiveBlockedSiblings(self):
        aVector = []
        previousNode = None
        currentNode = None
        nextNode = None
        ## for-while
        i = 0
        while i < len(self.siblings):
            previousNode = self
            currentNode = self.siblings.siblingAt(i)
            while currentNode is not None and currentNode.isBlocked():
                aVector.append(currentNode)
                nextNode = currentNode.siblings.nextSibling(previousNode)
                previousNode = currentNode
                currentNode = nextNode
            i += 1
        return aVector

    def getFullEndMostChildren(self):
        aVector = []
        ## for-while
        i = 0
        while i < len(self.endMostChildren):
            aNode = self.endMostChildren[i]
            if aNode.isFull():
                aVector.append(aNode)
            i += 1
        return aVector

    def getEmptyEndMostChildren(self):
        aVector = []
        ## for-while
        i = 0
        while i < len(self.endMostChildren):
            aNode = self.endMostChildren[i]
            if aNode.isEmpty():
                aVector.append(aNode)
            i += 1
        return aVector

    def getBlockedSiblings(self):
        aVector = []
        if self.siblings is not None:
            if self.siblings.siblingAt(0) is not None and self.siblings.siblingAt(0).isBlocked():
                aVector.append(self.siblings.siblingAt(0))
            if self.siblings.siblingAt(1) is not None and self.siblings.siblingAt(1).isBlocked():
                aVector.append(self.siblings.siblingAt(1))
        return aVector

    def getUnblockedSiblings(self):
        aVector = []
        if self.siblings is not None:
            if self.siblings.siblingAt(0) is not None and not self.siblings.siblingAt(0).isBlocked() and self.siblings.siblingAt(0).parent is not None and not self.siblings.siblingAt(0).parent.isDeleted():
                aVector.append(self.siblings.siblingAt(0))
            if self.siblings.siblingAt(1) is not None and not self.siblings.siblingAt(1).isBlocked() and self.siblings.siblingAt(1).parent is not None and not self.siblings.siblingAt(1).parent.isDeleted():
                aVector.append(self.siblings.siblingAt(1))
        return aVector

    def checkFullAreAdjacent(self):
        if (self.fullChildCount == 0):
            return True
        else:
            previousChild = self.fullChildAccessNode
            currentChild = PQNode()
            fullCount = 1
            nextChild = PQNode()
            ## for-while
            i = 0
            while i < len(previousChild.siblings):
                currentChild = previousChild.siblings.siblingAt(i)
                while fullCount < self.fullChildCount and currentChild is not None and currentChild.isFull():
                    fullCount += 1
                    nextChild = currentChild.siblings.nextSibling(previousChild)
                    previousChild = currentChild
                    currentChild = nextChild
                i += 1
            return (fullCount == self.fullChildCount)

    def checkFullAreAdjacentTo(self, aNode):
        if (self.fullChildCount == 0):
            return True
        else:
            return self.checkFullAreAdjacent() and aNode.siblings.siblingAt(0) is not None and aNode.siblings.siblingAt(0).isFull() or aNode.siblings.siblingAt(1) is not None and aNode.siblings.siblingAt(1).isFull()

    def checkFullAreEndMost(self):
        if (self.fullChildCount == 0):
            return True
        else:
            if not self.checkFullAreAdjacent():
                return False
            ## for-while
            i = 0
            while i < len(self.endMostChildren):
                if self.endMostChildren[i].isFull():
                    return True
                i += 1
            return False

    def checkPartialAreAtEnds(self):
        if (self.partialChildCount == 0):
            return True
        else:
            if not self.endMostChildren.contains(self.partialChildAccessNode):
                return False
            if (self.partialChildCount == 2) and not self.endMostChildren.contains(self.partialChildAccessNode.partialRight):
                return False
            return True

    def checkEndMostAreEmptyOrPartial(self):
        ## for-while
        i = 0
        while i < len(self.endMostChildren):
            if self.endMostChildren[i].isFull():
                return False
            i += 1
        return True

    def childrenAreFull(self):
        if self.isQNode():
            countFullEndMost = 0
            ## for-while
            i = 0
            while i < len(self.endMostChildren):
                if self.endMostChildren[i].isFull():
                    countFullEndMost += 1
                i += 1
            return (countFullEndMost == len(self.endMostChildren)) and self.checkFullAreAdjacent()
        else:
            return (self.fullChildCount == self.childCount)

    def hasOnlyOneChild(self):
        if self.isQNode():
            return (len(self.endMostChildren) == 1)
        else:
            return (self.childCount == 1)

    def hashCode(self):
        return str(self.internal_id)
    
    def infoString(self):
        outString = "["
        if self.data is not None:
            outString = outString + str(self.data)
        else:
            outString = outString
        if self.isFull():
            outString = outString + " f "
        else:
            if self.isPartial():
                outString = outString + " p "
            else:
                if self.isEmpty():
                    outString = outString + " e "
        outString = outString + " fc: " + str(self.fullChildCount)
        outString = outString + " fp: " + str(self.partialChildCount)
        if self.parent is not None:
            outString = outString + " p: " + self.parent.hashCode()
            if self.parent.isPNode():
                if self.left is not None:
                    outString = outString + " l: " + self.left.hashCode()
                else:
                    outString = outString + " l: " + "null"
                if self.right is not None:
                    outString = outString + " r: " + self.right.hashCode()
                else:
                    outString = outString + " r: " + "null"
            else:
                if self.parent.isQNode():
                    if self.siblings is None:
                        outString = outString + " siblings are null!"
                    else:
                        if self.siblings.siblingAt(0) is not None:
                            outString = outString + " s1: " + self.siblings.siblingAt(0).hashCode()
                        else:
                            outString = outString + " s1: " + "null"
                        if self.siblings.siblingAt(1) is not None:
                            outString = outString + " s2: " + self.siblings.siblingAt(1).hashCode()
                        else:
                            outString = outString + " s2: " + "null"
            if self.fullLeft is not None:
                outString = outString + " fl: " + self.fullLeft.hashCode()
            else:
                outString = outString + " fl: " + "null"
            if self.fullRight is not None:
                outString = outString + " fr: " + self.fullRight.hashCode()
            else:
                outString = outString + " fr: " + "null"
            if self.partialLeft is not None:
                outString = outString + " pl: " + self.partialLeft.hashCode()
            else:
                outString = outString + " pl: " + "null"
            if self.partialRight is not None:
                outString = outString + " pr: " + self.partialRight.hashCode()
            else:
                outString = outString + " pr: " + "null"
        else:
            outString = outString + " p: null"
        if self.isQNode():
            outString = outString + " e:"
            ## for-while
            i = 0
            while i < len(self.endMostChildren):
                outString = outString + " " + self.endMostChildren[i].infoString()
                i += 1
        outString = outString + " perl: " + str(self.pertinentLeafCount)
        outString = outString + " perc: " + str(self.pertinentChildCount)
        if self.fullChildAccessNode is None:
            outString = outString + " fcan: null"
        else:
            outString = outString + " fcan: " + str(self.fullChildAccessNode)
        outString = outString + "]"
        return outString

    def toString(self):
        if self.data is not None:
            return str(self.data)
        else:
            return "Interior Node"

    def printStructure(self):
        print self.infoString()
        children = self.getAllChildren()
        ## for-while
        i = 0
        while i < len(children):
            children[i].printStructure()
            i += 1


    def countSubLeaves(self, parent_depth):
        self.subLeafCount = 0
        self.depth = parent_depth + 1
        tempDepth = self.depth
        if self.hasChildren():
            childNode = PQNode()
            children = self.getAllChildren()
            ## for-while
            i = 0
            while i < len(children):
                childNode = children[i]
                self.subLeafCount += childNode.countSubLeaves(tempDepth)
                if childNode.depth > self.depth:
                    self.depth = childNode.depth
                i += 1
            return self.subLeafCount
        else:
            return 1

    def countSubNodes(self):
        subNodeCount = 1
        if self.hasChildren():
            children = self.getAllChildren()
            ## for-while
            i = 0
            while i < len(children):
                subNodeCount += children[i].countSubNodes()
                i += 1
        return subNodeCount


    def clear(self, recurse = True):
        self.labelAsEmpty()
        self.queued = False
        self.blocked = False
        self.pertinentChildCount = 0
        self.pertinentLeafCount = 0
        if recurse:
            if self.parent and ((self.parent.label != self.LABEL_EMPTY)\
                                or self.parent.queued\
                                or self.parent.blocked\
                                or (self.parent.pertinentChildCount != 0)\
                                or (self.parent.pertinentLeafCount != 0)\
                                or (self.parent.fullChildCount != 0)\
                                or (self.parent.partialChildCount != 0)):
                self.parent.clear()


    def get_countSubDeletedNodes(self):
        return self.countSubDeletedNodes([])

    def set_countSubDeletedNodes(self, deletedNodes):
        subDeletedNodeCount = 0
        if self.hasChildren():
            childNode = PQNode()
            children = self.getAllChildren()
            ## for-while
            i = 0
            while i < len(children):
                childNode = children[i]
                if childNode.parent.isDeleted():
                    if not deletedNodes.contains(childNode.parent):
                        deletedNodes.append(childNode.parent)
                        subDeletedNodeCount += 1
                subDeletedNodeCount += childNode.countSubDeletedNodes(deletedNodes)
                i += 1
        return subDeletedNodeCount

    countSubDeletedNodes = property(get_countSubDeletedNodes, set_countSubDeletedNodes)


    def __str__(self):
        if self.isPNode(): node_type = "P"
        else: node_type = "Q"
        return '%s-%d' % (node_type, self.internal_id)