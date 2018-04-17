import os, asyncio
from functools import partial
from cryfs.e2etest.utils.logger import Logger, LogLevel


class FilesystemException(Exception):
    def __init__(self, message: str) -> None:
        self._message = message


    def message(self) -> str:
        return self._message


# Returns true, iff both file system nodes are equal, i.e.
#  - either both are files and have same attributes and contents
#  - or both are symlinks and have same attributes and target
#  - or both are directories and have same attributes and entries, which are also equal (recursively)
def filesystem_node_equals(node1: str, node2: str, logger: Logger) -> bool:
    if not _attributes_equals(node1, node2):
        import pdb
        pdb.set_trace()
        logger.log(LogLevel.INFO, "Attributes different: %s and %s" % (node1, node2))
        return False
    # Need to check for symlinks first, because os.path.isdir and os.path.isfile return True for symlinks
    if os.path.islink(node1):
        if not (os.path.islink(node2) and symlink_equals(node1, node2)):
            logger.log(LogLevel.INFO, "Links different: %s and %s" % (node1, node2))
            return False
    elif os.path.isdir(node1):
        if not (os.path.isdir(node2) and dir_equals(node1, node2, logger)):
            logger.log(LogLevel.INFO, "Dirs different: %s and %s" % (node1, node2))
            return False
    elif os.path.isfile(node1):
        if not (os.path.isfile(node2) and file_equals(node1, node2)):
            logger.log(LogLevel.INFO, "Files different: %s and %s" % (node1, node2))
            return False
    else:
        raise FilesystemException("Unknown filesystem node type")
    return True


def _attributes_equals(node1: str, node2: str) -> bool:
    stat1 = os.stat(node1)
    stat2 = os.stat(node2)
    # TODO Compare more attributes (especially atime, mtime, ctime)
    #print("mode %s vs %s" % (stat1.st_mode, stat2.st_mode))
    #print("nlink %s vs %s" % (stat1.st_nlink, stat2.st_nlink))
    #print("uid %s vs %s" % (stat1.st_uid, stat2.st_uid))
    #print("gid %s vs %s" % (stat1.st_gid, stat2.st_gid))
    #print("isdir: %d", os.path.isdir(node1))
    #print("size %s vs %s" % (stat1.st_size, stat2.st_size))
    #print("atime %s vs %s" % (stat1.st_atime, stat2.st_atime))
    #print("mtime %s vs %s" % (stat1.st_mtime, stat2.st_mtime))
    #print("ctime %s vs %s" % (stat1.st_ctime, stat2.st_ctime))
    #return stat1.st_mode == stat2.st_mode  \
    #  and stat1.st_nlink == stat2.st_nlink \
    #  and stat1.st_uid == stat2.st_uid     \
    #  and stat1.st_gid == stat2.st_gid     \
    #  and (os.path.isdir(node1) or stat1.st_size == stat2.st_size)   \
    #  and stat1.st_atime == stat2.st_atime \
    #  and stat1.st_mtime == stat2.st_mtime \
    #  and stat1.st_ctime == stat2.st_ctime
    return stat1.st_uid == stat2.st_uid     \
      and stat1.st_gid == stat2.st_gid     \
      and (os.path.isdir(node1) or stat1.st_size == stat2.st_size)


def dir_equals(node1: str, node2: str, logger: Logger) -> bool:
    # TODO Could be faster using os.scandir() instead of os.listdir() because that already returns the stat information
    entries1 = sorted(os.listdir(node1))
    entries2 = sorted(os.listdir(node2))
    if entries1 != entries2:
        return False
    for entry in entries1:
        if not filesystem_node_equals(os.path.join(node1, entry), os.path.join(node2, entry), logger):
            return False
    return True


def file_equals(node1: str, node2: str) -> bool:
    with open(node1, 'rb') as file1, open(node2, 'rb') as file2:
        content1 = file1.read()
        content2 = file2.read()
        return content1 == content2


def symlink_equals(node1: str, node2: str) -> bool:
    return os.readlink(node1) == os.readlink(node2)


async def async_dir_equals(node1: str, node2: str, logger: Logger) -> bool:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(dir_equals, node1, node2, logger))
