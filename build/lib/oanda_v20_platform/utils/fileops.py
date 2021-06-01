from pathlib import Path


def get_abs_path(pathlist=['data', 'marketdata.db']):
    """To solve the problem of finding files with relative
    paths on windows/linux/mac etc. esp when a module has been
    imported into a different working directory
    This finds the current working directory cuts it back
    to oanda_v20_platform_public then adds the components of pathlist
    Args:
        pathlist list of str, folder and filenames required
        after oanda_v20_platform
    Returns:
         a pathlib object with the absolute path

    """
    p = Path()
    # get the current working dir
    cwd = p.cwd()
    # get the dir tree
    tree = list(cwd.parts)
    # print("Total tree: ", tree)
    if 'oanda_v20_platform' in tree:
        # shorten it to the oanda_v20_platform root
        tree = tree[:tree.index('oanda_v20_platform')+1]
        for x in pathlist:
            tree.append(x)
        newpath = Path(*tree)

    else:
        # shorten tree and try to find oanda_v20_platfrom
        tree = tree[:-1]
        shortpath = Path(*tree)
        nextpath = list(shortpath.glob('**/oanda_v20_platform/'))[-1]
        newtree = list(nextpath.parts)
        if 'oanda_v20_platform' in newtree:
            newtree = newtree[:newtree.index('oanda_v20_platform')+1]
            for x in pathlist:
                newtree.append(x)
            newpath = Path(*newtree)
        else:
            message = ("Can't find the right files,"
                       " check installation")
            raise FileNotFoundError(message)

    return newpath.absolute()
