from python_helper.api.src.annotation import TestAnnotation
from python_helper.api.src.annotation.TestAnnotation import Test
from python_helper.api.src.domain import Constant as c
from python_helper.api.src.service import SettingHelper, LogHelper, ReflectionHelper, ObjectHelper, StringHelper
import time

PY = 'py'
DOT_PY = f'{c.DOT}{PY}'
TEST_SUFIX_NAME = 'Test'
TEST_DOT_PY = f'{TEST_SUFIX_NAME}{DOT_PY}'
TEST_PACKAGE = TEST_SUFIX_NAME.lower()

GLOBALS_INSTANCE_LIST = []
RESULTS = {}
TEST_KWARGS = {
    'argsOfCallBefore' : [GLOBALS_INSTANCE_LIST],
    'argsOfCallAfter' : [GLOBALS_INSTANCE_LIST],
    'returns' : RESULTS,
    'logResult' : False
}

def getRaisedException(callableThing, *args, logGetRaisedExceptionIfAny=False, **kwargs):
    try:
        callableThing(*args, **kwargs)
    except Exception as exception:
        if logGetRaisedExceptionIfAny:
            LogHelper.error(getRaisedException, 'Exception', exception)
        return exception

def getUnitTest(inspectGlobals, globalsInstance) :
    @Test(**getGlobalsTestKwargs(inspectGlobals, globalsInstance))
    def unitTest(testModule, testName, data, testReturns, logResult) :
        discountTimeEnd = time.time()
        unitTestException = None
        if logResult :
            LogHelper.test(unitTest, f'{testName}{c.DOT}{data[1]} test started')
        moduleTestStartTime = time.time()
        try :
            testReturns[data[1]] = data[0]()
            LogHelper.printSuccess(f'{data[0].__module__}{c.DOT}{data[0].__name__} succeed', condition=logResult, newLine=False, margin=False)
        except Exception as exception :
            LogHelper.printError(f'{data[0].__module__}{c.DOT}{data[0].__name__} failed', condition=True, newLine=False, margin=False, exception=exception)
            unitTestException = exception
        if logResult :
            LogHelper.test(unitTest, f'{testName}{c.DOT}{data[1]} test completed in {time.time() - moduleTestStartTime} seconds')
        if ObjectHelper.isNotNone(unitTestException) :
            raise unitTestException
        someDidRun = True
        return testName, data, testReturns, someDidRun, logResult, discountTimeEnd
    return unitTest

def getUnitTestBatch(inspectGlobals, globalsInstance) :
    @Test(**getGlobalsTestKwargs(inspectGlobals, globalsInstance))
    def unitTestBatch(testModule, data) :
        discountTimeEnd = time.time()
        data[0]()
        return discountTimeEnd
    return unitTestBatch

def getModuleTest(inspectGlobals, logResult, globalsInstance) :
    @Test(**getGlobalsTestKwargs(inspectGlobals, globalsInstance))
    def tddModule(testName, testModule, dataList, times, runSpecificTests, testsToRun, allShouldRun, someShouldRun, logResult) :
        import globals
        tddModuleGlobalsInstance = globals.newGlobalsInstance(testModule.__file__
            , successStatus = globalsInstance.successStatus
            , errorStatus = globalsInstance.errorStatus
            , failureStatus = globalsInstance.failureStatus
            , settingStatus = globalsInstance.settingStatus or inspectGlobals
            , statusStatus = globalsInstance.statusStatus
            , infoStatus = globalsInstance.infoStatus
            , debugStatus = globalsInstance.debugStatus
            , warningStatus = globalsInstance.warningStatus
            , wrapperStatus = globalsInstance.wrapperStatus
            , testStatus = globalsInstance.testStatus
            , logStatus = globalsInstance.logStatus
            , logsWithColors = globalsInstance.logsWithColors or LogHelper.colorsEnabled()
        )
        LogHelper.test(tddModule, f'{testName} started')
        testReturns = {}
        testTime = 0
        for data in dataList :
            testMustRun = isTestToRun(testModule, data, runSpecificTests, testsToRun)
            LogHelper.prettyPython(tddModule, f'test attribute or method', data[0], logLevel=LogHelper.TEST)
            LogHelper.prettyPython(tddModule, f'isTestToRun', testMustRun, logLevel=LogHelper.TEST)
            if testMustRun :
                for index in range(times) :
                    testTimeStart = time.time()
                    if times - 1 == index :
                        runnableUnitTest = getUnitTest(inspectGlobals, globalsInstance)
                        testName, data, testReturns, someDidRun, logResult, discountTimeEnd = runnableUnitTest(testModule, testName, data, testReturns, logResult)
                    else :
                        runnableUnitTestBatch = getUnitTestBatch(inspectGlobals, globalsInstance)
                        discountTimeEnd = runnableUnitTestBatch(testModule, data)
                    testTime += time.time() - discountTimeEnd
            else :
                allDidRun = False
        if not allShouldRun == allDidRun and someShouldRun == someDidRun :
            amountAlthought = getAmmount(allShouldRun, someShouldRun)
            shouldOrShouldnt = getShouldOrShouldntAsString(allShouldRun, someShouldRun)
            amountAfterAlthought = getAmmount(allDidRun, someDidRun)
            didOrDidnt = getSomeDidOrDidntAsString(allDidRun, someDidRun)
            errorMessage = f'Inconsistenc{StringHelper.getS(allShouldRun or someShouldRun, es=True)} detected. Although {amountAlthought} test{StringHelper.getS(allShouldRun or someShouldRun)} {shouldOrShouldnt} run, {amountAfterAlthought} {didOrDidnt} run'
            exception = Exception(errorMessage)
            raise exception
        return allDidRun, someDidRun, testTime, testReturns
    return tddModule

def runModuleTests(testName, runnableTddModule, times, runSpecificTests, testsToRun, logResult, globalsInstance) :
    import globals
    testModule = globals.importModule(testName, required=True)
    # if ObjectHelper.isNone(testModule):
    #     errorMessage = f'Not possible to import {testName}'
    #     exception = Exception(f'Not possible to import {testName}')
    #     LogHelper.error(runModuleTests, f'{errorMessage}. Please check warnings for more details', exception)
    #     raise exception
    dataList = ReflectionHelper.getAttributeDataList(testModule)
    LogHelper.prettyPython(runnableTddModule, f'{ReflectionHelper.getName(testModule)} tests loaded', dataList, logLevel=LogHelper.TEST)
    allShouldRun, someShouldRun, allDidRun, someDidRun = getRunStatus(testModule, dataList, runSpecificTests, testsToRun)
    testReturns = {}
    testTime = 0
    totalTestTimeStart = time.time()
    if someShouldRun :
        defaultMessage = f'{testName}{StringHelper.getS(allShouldRun)}'
        methodReturnException = None
        LogHelper.test(runModuleTests, f'{defaultMessage} started')
        try :
            allDidRun, someDidRun, testTime, testReturns = runnableTddModule(testName, testModule, dataList, times, runSpecificTests, testsToRun, allShouldRun, someShouldRun, logResult)
            LogHelper.printSuccess(f'{defaultMessage} succeed. {getTestRuntimeInfo(times, testTime, time.time() - totalTestTimeStart)}', condition=logResult, newLine=True, margin=False)
        except Exception as exception :
            methodReturnException = exception
            LogHelper.printError(f'{defaultMessage} failed', condition=True, newLine=True, margin=False, exception=methodReturnException)
        exceptionRaised = ObjectHelper.isNotNone(methodReturnException)
        defaultMessage = f'{testName}{StringHelper.getS(not exceptionRaised and allDidRun)}'
        if exceptionRaised :
            raise methodReturnException
    return allDidRun, someDidRun, testTime, testReturns

def getRunStatus(testModule, dataList, runSpecificTests, testsToRun) :
    allDidRun = True
    someDidRun = False
    allShouldRun = True
    someShouldRun = False
    for data in dataList :
        if isTestToRun(testModule, data, runSpecificTests, testsToRun) :
            someShouldRun = True
        else :
            allShouldRun = False
    allShouldRun, someShouldRun, allDidRun, someDidRun
    return allShouldRun, someShouldRun, allDidRun, someDidRun

def getAmmount(allShouldRun, someShouldRun) :
    if allShouldRun :
        return 'all'
    elif someShouldRun :
        return 'some'
    else :
        return 'none'

def getShouldOrShouldntAsString(allShouldRun, someShouldRun) :
    return f'should' if allShouldRun or someShouldRun else f'shouldn{c.SINGLE_QUOTE}t'

def getSomeDidOrDidntAsString(allDidRun, someDidRun) :
    if allDidRun :
        return 'all'
    elif someDidRun :
        return 'some'
    else :
        return 'none'

def getSomeDidOrDidntAsString(allDidRun, someDidRun) :
    return 'did' if allDidRun or someDidRun else f'didn{c.SINGLE_QUOTE}t'

def run(
    filePath,
    runOnly = None,
    ignore=None,
    times = 1,
    successStatus = True,
    errorStatus = True,
    settingStatus = False,
    statusStatus = True,
    infoStatus = True,
    debugStatus = True,
    warningStatus = True,
    failureStatus = True,
    wrapperStatus = False,
    testStatus = False,
    logStatus = False,
    logsWithColors = False,
    inspectGlobals = False,
    logResult = True
) :
    import globals
    globalsInstance = globals.newGlobalsInstance(filePath
        , successStatus = successStatus
        , errorStatus = errorStatus
        , settingStatus = settingStatus or inspectGlobals
        , statusStatus = statusStatus
        , infoStatus = infoStatus
        , debugStatus = debugStatus
        , warningStatus = warningStatus
        , failureStatus = failureStatus
        , wrapperStatus = wrapperStatus
        , testStatus = testStatus
        , logStatus = logStatus
        , logsWithColors = logsWithColors or LogHelper.colorsEnabled()
    )
    testModuleNames, testsToRun, runSpecificTests = getTestModuleNames(runOnly, ignore, globalsInstance)
    returns = {}
    totalTestTimeStart = time.time()
    testTime = 0
    for testModuleName in testModuleNames :
        runnableTddModule = getModuleTest(inspectGlobals, logResult, globalsInstance)
        allDidRun, didRun, moduleTestTime, testReturns = runModuleTests(testModuleName, runnableTddModule, times, runSpecificTests, testsToRun, logResult, globalsInstance)
        returns[testModuleName] = testReturns
        testTime += moduleTestTime
    totalTestTime = time.time() - totalTestTimeStart
    if logResult :
        LogHelper.success(run, f'{globalsInstance.apiName} tests completed. {getTestRuntimeInfo(times, testTime, totalTestTime)}')
    return returns

def getTestModuleNames(runOnly, ignore, globalsInstance) :
    testsToRun = [] if ObjectHelper.isNone(runOnly) or ObjectHelper.isNotCollection(runOnly) else runOnly
    testsToIgnore = [] if ObjectHelper.isNone(ignore) or ObjectHelper.isNotCollection(ignore) else ignore
    runSpecificTests = ObjectHelper.isNotEmpty(testsToRun)
    LogHelper.prettyPython(getTestModuleNames, f'runSpecificTests: {runSpecificTests}, testsToRun', testsToRun, logLevel=LogHelper.TEST)
    testModuleNames = []
    if ObjectHelper.isEmpty(testsToRun) :
        testQueryTree = SettingHelper.querySetting(TEST_PACKAGE, globalsInstance.apiTree)
        LogHelper.prettyPython(getTestModuleNames, 'Test query tree', testQueryTree, logLevel=LogHelper.TEST)
        testModuleNames += getTestModuleNamesFromQuerryTree(testQueryTree, runOnly, ignore)
    else :
        for testName in testsToIgnore :
            if testName in testsToRun :
                testModuleNames, testsToRun, runSpecificTests .remove(testName)
        for testName in testsToRun :
            testNameSplitted = testName.split(c.DOT)
            testModuleName = c.NOTHING
            if 2 == len(testNameSplitted) :
                testModuleName = testNameSplitted[-2]
            if testModuleName not in testModuleNames and StringHelper.isNotBlank(testName) :
                testModuleNames.append(testModuleName)
    LogHelper.prettyPython(getTestModuleNames, 'Test module names', testModuleNames, logLevel=LogHelper.TEST)
    return testModuleNames, testsToRun, runSpecificTests

def getTestModuleNamesFromQuerryTree(testQueryTree, runOnly, ignore) :
    testModuleNames = []
    for queryResultKey, queryResult in testQueryTree.items() :
        LogHelper.prettyPython(getTestModuleNamesFromQuerryTree, 'Query result', queryResult, logLevel=LogHelper.TEST)
        updateTestModuleNames(testModuleNames, queryResult, runOnly, ignore)
    return testModuleNames

def updateTestModuleNames(testModuleNames, queryResult, runOnly, ignore) :
    if not c.NOTHING == queryResult :
        for key, value in queryResult.items() :
            if c.NOTHING == value and key.endswith(TEST_DOT_PY) :
                testModuleName = key[:-len(DOT_PY)]
                if ObjectHelper.isNone(runOnly) or ObjectHelper.isNotNone(runOnly) and testModuleName in runOnly :
                    testModuleNames.append(testModuleName)
            else :
                updateTestModuleNames(testModuleNames, value, runOnly, ignore)

def isTestToRun(testModule, attributeData, runSpecificTests, testsToRun) :
    return (
            not runSpecificTests or
            (runSpecificTests and f'{ReflectionHelper.getName(testModule)}{c.DOT}{attributeData[1]}' in testsToRun)
        ) and ReflectionHelper.getAttributeOrMethod(attributeData[0], TestAnnotation.IS_TEST_METHOD, muteLogs=True)

def getTestRuntimeInfo(times, testTime, totalTestTime) :
    testRuntimeInfo = None
    try :
        testRuntimeInfo = f'It {StringHelper.getToBe(True, singular=1==times, tense=StringHelper.PAST)} {times} test run{StringHelper.getS(times > 1)} in {testTime} seconds. Total test time: {totalTestTime} seconds'
    except Exception as exception :
        LogHelper.warning(getTestRuntimeInfo, 'Not possible do get test runtime info', exception=exception)
        testRuntimeInfo = c.NOTHING
    return testRuntimeInfo

def getTestEnvironmentVariables(globalsInstance) :
    return {
        LogHelper.LOG : globalsInstance.logStatus,
        LogHelper.INFO : globalsInstance.infoStatus,
        LogHelper.STATUS : globalsInstance.statusStatus,
        LogHelper.SUCCESS : globalsInstance.successStatus,
        LogHelper.SETTING : globalsInstance.settingStatus,
        LogHelper.DEBUG : globalsInstance.debugStatus,
        LogHelper.WARNING : globalsInstance.warningStatus,
        LogHelper.FAILURE : globalsInstance.failureStatus,
        LogHelper.WRAPPER : globalsInstance.wrapperStatus,
        LogHelper.ERROR : globalsInstance.errorStatus,
        LogHelper.TEST : globalsInstance.testStatus,
        LogHelper.ENABLE_LOGS_WITH_COLORS: globalsInstance.logsWithColors
    }

def getGlobalsTestKwargs(inspectGlobals, globalsInstance) :
    import globals
    TEST_KWARGS['callBefore'] = globals.runBeforeTest
    TEST_KWARGS['callAfter'] = globals.runAfterTest
    TEST_KWARGS['inspectGlobals'] = inspectGlobals
    TEST_KWARGS['kwargsOfCallBefore'] = {
        'muteLogs' : not inspectGlobals,
        'logLevel' : LogHelper.DEBUG
    }
    TEST_KWARGS['kwargsOfCallAfter'] = {
        'muteLogs' : not inspectGlobals,
        'logLevel' : LogHelper.DEBUG
    }
    return {
        'environmentVariables' : getTestEnvironmentVariables(globalsInstance),
        **TEST_KWARGS
    }
