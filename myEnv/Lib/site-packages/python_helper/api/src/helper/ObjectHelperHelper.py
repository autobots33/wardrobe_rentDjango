from python_helper.api.src.service import ObjectHelper, ReflectionHelper, LogHelper

def generatorInstance():
    while True :
        yield False
        break

def leftEqual(left, right, ignoreKeyList, ignoreCharactereList, ignoreAttributeList, ignoreAttributeValueList, visitedIdInstances, muteLogs=True):
    if ObjectHelper.isNone(left) or ObjectHelper.isNone(right):
        return left is None and right is None
    isEqual = True
    leftIsCollection = ObjectHelper.isCollection(left)
    rightIsCollection = ObjectHelper.isCollection(right)
    if leftIsCollection and rightIsCollection:
        if len(left) == len(right):
            for itemLeft, itemRight in zip(left, right):
                if itemRight not in ignoreAttributeValueList and not ObjectHelper.equals(
                    itemLeft,
                    itemRight,
                    ignoreKeyList = ignoreKeyList,
                    ignoreCharactereList = ignoreCharactereList,
                    ignoreAttributeList = ignoreAttributeList,
                    ignoreAttributeValueList = ignoreAttributeValueList,
                    visitedIdInstances = visitedIdInstances,
                    muteLogs = muteLogs
                ):
                    isEqual = False
                    break
            return isEqual
        else:
            return left == right
    elif (leftIsCollection and not rightIsCollection) or (not leftIsCollection and rightIsCollection):
        return False
    else:
        attrinuteDataList = ReflectionHelper.getAttributeDataList(left)
        if not muteLogs :
            LogHelper.prettyPython(leftEqual, f'{left} data list', attrinuteDataList, logLevel=LogHelper.DEBUG, condition=not muteLogs)
        if 0 == len(attrinuteDataList):
            return False
        if not isEqual:
            return isEqual
        for value, name in attrinuteDataList:
            if name not in ignoreAttributeList and value not in ignoreAttributeValueList and not ObjectHelper.equals(
                value,
                ReflectionHelper.getAttributeOrMethod(right, name),
                ignoreKeyList = ignoreKeyList,
                ignoreCharactereList = ignoreCharactereList,
                ignoreAttributeList = ignoreAttributeList,
                ignoreAttributeValueList = ignoreAttributeValueList,
                visitedIdInstances = visitedIdInstances,
                muteLogs = muteLogs
            ):
                isEqual = False
                break
        return isEqual
