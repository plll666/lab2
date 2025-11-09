import shlex

def parse(cmd):
    """
    Парсинг введенной команды на составляющие.
    Args:
        cmd: Введенная пользователем команда
    Returns:
        tuple:(command, flags, args)
    """
    flags = []
    args = []

    pars = shlex.split(cmd)
    command = pars[0]
    part = pars[1:]
    for i in part:
        if i.startswith("-"):
                flags.append(i)
        else:
                args.append(i)

    return command, flags, args



