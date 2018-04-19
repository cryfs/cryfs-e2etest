import os
from cryfs.e2etest.test_framework.logger import Logger, LogLevel


# Returns true, iff both file system nodes are equal, i.e.
#  - either both are files and have same attributes and contents
#  - or both are symlinks and have same attributes and target
#  - or both are directories and have same attributes and entries, which are also equal (recursively)
def expect_filesystem_node_equals(node1: str, node2: str, logger: Logger) -> None:
    if not _attributes_equals(node1, node2):
        logger.log(LogLevel.ERROR, "Attributes different: %s and %s" % (node1, node2))
    # Need to check for symlinks first, because os.path.isdir and os.path.isfile return True for symlinks
    if os.path.islink(node1):
        if not os.path.islink(node2):
            logger.log(LogLevel.ERROR, "%s is a symlink but %s is not" % (node1, node2))
        else:
            expect_symlink_equals(node1, node2, logger)
    elif os.path.isdir(node1):
        if not os.path.isdir(node2):
            logger.log(LogLevel.ERROR, "%s is a dir but %s is not" % (node1, node2))
        else:
            expect_dir_equals(node1, node2, logger)
    elif os.path.isfile(node1):
        if not os.path.isfile(node2):
            logger.log(LogLevel.ERROR, "%s is a file but %s is not" % (node1, node2))
        else:
            expect_file_equals(node1, node2, logger)
    else:
        logger.log(LogLevel.FATAL, "Unknown filesystem node type: %s" % node1)


def _attributes_equals(node1: str, node2: str) -> bool:
    stat1 = os.stat(node1, follow_symlinks=False)
    stat2 = os.stat(node2, follow_symlinks=False)
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


def expect_dir_equals(node1: str, node2: str, logger: Logger) -> None:
    # TODO Could be faster using os.scandir() instead of os.listdir() because that already returns the stat information
    entries1 = sorted(os.listdir(node1))
    entries2 = sorted(os.listdir(node2))
    if entries1 != entries2:
        logger.log(LogLevel.ERROR, "Different directory entries: %s and %s" % (node1, node2))
    else:
        for entry in entries1:
            expect_filesystem_node_equals(os.path.join(node1, entry), os.path.join(node2, entry), logger)


def expect_file_equals(node1: str, node2: str, logger: Logger) -> None:
    with open(node1, 'rb') as file1, open(node2, 'rb') as file2:
        content1 = file1.read()
        content2 = file2.read()
        if content1 != content2:
            logger.log(LogLevel.ERROR, "File contents differ: %s and %s" % (node1, node2))


def expect_symlink_equals(node1: str, node2: str, logger: Logger) -> None:
    if os.readlink(node1) != os.readlink(node2):
        logger.log(LogLevel.ERROR, "Symlinks have different targets: %s and %s" % (node1, node2))
