#!/usr/bin/env python
# -*- coding: utf-8 -*-


class SiblingVector(list):
    """ generated source for SiblingVector

    """

    def __init__(self):
        pass

    def addSibling(self, aSibling):
        if len(self) < 2:
            self.append(aSibling)
        else:
            if aSibling not in self:
                raise Exception("*** ERROR cannot add more than 2 siblings!")


    def removeSibling(self, aSibling):
        return self.remove(aSibling)

    def siblingAt(self, index):
        if index < len(self):
            return self[index]
        else:
            return

    def nextSibling(self, aSibling):
        if (len(self) == 1) and aSibling is None:
            return self.siblingAt(0)
        else:
            if (len(self) == 1):
                return
            else:
                if (aSibling == self.siblingAt(0)):
                    return self.siblingAt(1)
                else:
                    if (aSibling == self.siblingAt(1)):
                        return self.siblingAt(0)
                    else:
                        raise Exception("*** ERROR no proper next sibling could be found! " + aSibling)


    def otherSibling(self, aSibling):
        if (len(self) == 1):
            return
        else:
            if (self.siblingAt(0) == aSibling):
                return self.siblingAt(1)
            else:
                if (self.siblingAt(1) == aSibling):
                    return self.siblingAt(0)
                else:
                    raise Exception("*** ERROR cannot return other sibling of " + aSibling)


    def replaceSibling(self, oldSibling, newSibling):
        if (self.siblingAt(0) == oldSibling):
            self[0] = newSibling
        else:
            if (self.siblingAt(1) == oldSibling):
                self[1] = newSibling
            else:
                raise Exception("*** ERROR cannot replace nonexistant sibling: " + oldSibling)


