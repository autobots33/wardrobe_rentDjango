from python_helper.api.src.domain import FileOperation
from python_helper.api.src.service import LogHelper


def getFileLines(filePath: str, encoding: str = FileOperation.UTF_8):
    lines = []
    try:
        with open(filePath, FileOperation.READ_TEXT, encoding=encoding) as readder :
            lines = readder.readlines()
    except Exception as exception:
        LogHelper.error(getFileLines, f'Not possible to read lines of {filePath}', exception, muteStackTrace=True)
        raise exception
    return lines


def overrideContent(filepath: str, content, encoding: str = FileOperation.UTF_8):
    return writeContent(filepath, content, operation = FileOperation.OVERRIDE_TEXT, encoding = encoding)


def writeContent(filepath: str, content, operation: str = FileOperation.WRITE_TEXT, encoding: str = FileOperation.UTF_8):
    try:
        with open(filepath, operation, encoding=encoding) as writter:
            writter.write(content)
    except Exception as exception:
        LogHelper.error(overrideFileLines, f'Not possible to write content of {filePath}', exception, muteStackTrace=True)
        raise exception


def overrideFileLines(filePath: str, lines: list, operation: str = FileOperation.OVERRIDE_TEXT, encoding: str = FileOperation.UTF_8):
    try:
        with open(filePath, operation, encoding=encoding) as writer:
            writer.writelines(lines)
    except Exception as exception:
        LogHelper.error(overrideFileLines, f'Not possible to override lines of {filePath}', exception, muteStackTrace=True)
        raise exception


def writeFileLines(filePath: str, lines: list, operation: str = FileOperation.WRITE_TEXT, encoding: str = FileOperation.UTF_8):
    try:
        with open(filePath, operation, encoding=encoding) as writer:
            writer.writelines(lines)
    except Exception as exception:
        LogHelper.error(writeFileLines, f'Not possible to write lines of {filePath}', exception, muteStackTrace=True)
        raise exception
