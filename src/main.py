from parser import parse
from commands import *
from const import COMMANDS
from logger import *



def main():
    setup_logging()
    while True:
        user_input = input(f"{Path.cwd()}> ")
        user_input = user_input.replace("\\","/")

        if not user_input:
            continue

        if user_input == "q":
            log_command("q")
            break

        log_command(user_input)

        try:
            command, flags, args = parse(user_input)
        except Exception as e:
            log_error(f"Parse error: {e}")
            print(f"Parse error: {e}")
            continue

        if command == "ls":
            path = args[0] if args else "."
            if len(flags) == 0:
                try:
                    files = ls(path)
                    for file in files:
                        print(file)
                        log_success(file)
                    log_success(f"ls -l {path} : {len(files)}")

                except (FileNotFoundError, PermissionError) as e:
                    log_error(str(e))
                    print(e)
            if '-l' in flags:
                try:
                    files = ls_l(path)
                    for file in files:
                        print(file)
                        log_success(file)
                    log_success(f"ls {path}: {len(files)} items")
                except (FileNotFoundError, PermissionError) as e:
                    log_error(str(e))
                    print(e)

        if command == "cd":
            try:
                cd(args[0])
            except (FileNotFoundError, PermissionError) as e:
                log_error(str(e))
                print(e)

        if command == "pwd":
            print(Path.cwd())
            log_command(Path.cwd())

        if command == "cat":
            if not args:
                print("")
                continue
            try:
                print(cat(args[0]))
                log_success(cat(args[0]))
            except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
                log_error(str(e))
                print(e)

        if command == "cp":
            if len(args) < 2:
                print("Error: cp must have at least 2 arguments")
                continue
            try:
                cp(args[0], args[1], flags)
                log_success(cp(args[0], args[1], flags))
            except (FileNotFoundError, FileExistsError, IsADirectoryError, NotADirectoryError) as e:
                log_error(str(e))
                print(e)

        if command == "mv":
            if len(args) < 2:
                print("Error: mv must have at least 2 arguments")
                continue
            try:
                mv(args[0], args[1])

            except (FileNotFoundError) as e:
                log_error(str(e))
                print(e)

        if command == "rm":
            if not args:
                print("Error: rm must have at least 1 argument")
                continue
            try:
                rm(args[0], flags)

            except (FileNotFoundError, ValueError, NotADirectoryError, InvalidInputError, NotFlagError,\
                    PermissionError) as e:
                log_error(str(e))
                print(e)

        if command == "zip":
            if len(args) < 2:
                print("Error: zip must have at least 2 arguments")
                continue
            try:
                create_zip(args[0], args[1])

            except (FileNotFoundError, LenArgsError) as e:
                log_error(str(e))
                print(e)
        if command ==  "unzip":
            if not args:
                print("Error: unzip must have at least 1 argument")
                continue
            try:
                extract_zip(args[0])

            except (FileNotFoundError, InvalidArchiveError, ArchiveError) as e:
                log_error(str(e))
                print(e)

        if command == "tar":
            if len(args) < 2:
                print("Error: tar must have at least 2 arguments")
                continue
            try:
                create_tar(args[0], args[1])

            except (FileNotFoundError, ArchiveError, InvalidArchiveError, LenArgsError) as e:
                log_error(str(e))
                print(e)

        if command == "untar":
            if not args:
                print("Error: untar must have at least 1 argument")
                continue
            try:
                extract_tar(args[0])

            except (FileNotFoundError, ArchiveError, InvalidArchiveError) as e:
                log_error(str(e))
                print(e)

        if command not in COMMANDS:
            log_error(f"Invalid command: {command}")
            print(f"Invalid command: {command}")





if __name__ == "__main__":
    main()