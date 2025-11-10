from pathlib import Path
from datetime import datetime
import stat
import os
import shutil

import zipfile
import tarfile
from src.errors import *
from src.logger import log_command, log_success, log_error


def ls(path="."):
    """
    команда ls без флага -l
    Args:
        path: Путь к директории
    Returns:
        list: Список имен файлов и директорий
    Raises:
        FileNotFoundError: Если директория не существует
        NotADirectoryError: Если путь не является директорией
    """
    directory = Path(path).resolve()

    if not directory.exists():
        raise FileNotFoundError(f"Directory {directory} does not exist")

    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a directory")

    return [file.name for file in directory.iterdir()]

def ls_l(path="."):
    """
    команда ls с флагом -r
    Args:
        path: Путь к директории
    Returns:
        list: Список строк
    Raises:
        FileNotFoundError: Если директория не существует
        NotADirectoryError: Если путь не является директорией
        PermissionError: Если доступ к директории запрещен
    """
    directory = Path(path).resolve()

    if not directory.exists():
        raise FileNotFoundError(f"Directory {directory} does not exist")

    if not directory.is_dir():
        raise NotADirectoryError(f"Directory {directory} is not a directory")

    def permissions(mode):
        perm = ""

        if stat.S_ISDIR(mode):
            perm += "d"
        if stat.S_ISLNK(mode):
            perm += "l"
        else:
            perm += "-"

        perm += 'd' if mode & stat.S_ISDIR(mode) else '-'
        perm += 'r' if mode & stat.S_IRUSR else '-'
        perm += 'w' if mode & stat.S_IWUSR else '-'
        perm += 'x' if mode & stat.S_IXUSR else '-'

        perm += 'r' if mode & stat.S_IRGRP else '-'
        perm += 'w' if mode & stat.S_IWGRP else '-'
        perm += 'x' if mode & stat.S_IXGRP else '-'

        perm += 'r' if mode & stat.S_IROTH else '-'
        perm += 'w' if mode & stat.S_IWOTH else '-'
        perm += 'x' if mode & stat.S_IXOTH else '-'

        return perm

    def time(time):
        dt = datetime.fromtimestamp(time)
        return dt.strftime('%b %d %H:%M')

    result = []
    try:
        items = list(directory.iterdir())
        items.sort(key = lambda x: x.name)
        for item in items:
            try:
                if item.is_symlink():
                    stat_info = item.lstat()
                else:
                    stat_info = item.stat()


                perm = permissions(stat_info.st_mode)
                size = stat_info.st_size
                mtime = time(stat_info.st_mtime)
                name = item.name

                result.append(f"{perm} {size:8} {mtime} {name}")
            except (PermissionError, OSError):
                continue
    except PermissionError as e:
        raise PermissionError(f"Permission error: {e}")
    return result

def cd(path="."):
    """
    команда cd
    Args:
        path: Путь к целевой директории
    Returns:
        str: Новый путь директории
    Raises:
        FileNotFoundError: Если директория не существует
        NotADirectoryError: Если путь не является директорией
    """
    if not path:
        return ""

    directory = Path(path)

    if path == '.':
        directory = Path.cwd()
    elif path == '..':
        directory = Path.cwd().parent
    elif path == "~":
        directory = Path.home()
    else:
        if not directory.is_absolute():
            directory = Path.cwd() / directory

    directory = directory.resolve()
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory {directory} does not exist")
    if not directory.is_dir():
        raise NotADirectoryError(f"Directory {directory} is not a directory")


    if not directory.is_absolute():
        directory = Path.cwd() / directory

    os.chdir(str(directory))
    return str(directory)

def cat(path):
    """
    команда cat
    Args:
        path: Путь к файлу
    Returns:
        str: Содержимое файла
    Raises:
        FileNotFoundError: Если файл не существует
        IsADirectoryError: Если путь является директорией
    """
    directory = Path(path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory {directory} does not exist")
    if directory.is_dir():
        raise IsADirectoryError(f"Directory {directory} is a directory")

    return directory.read_text(encoding="utf-8")

def cp(dir_get, dir_to, flags):
    """
    команда cp
    Args:
        dir_get: Источник копирования
        dir_to: Целевой путь
        flags: Флаги команды
    Raises:
        FileNotFoundError: Если источник не существует
        IsADirectoryError: Если источник является директорией без флага -r
        NotADirectoryError: Если источник не является директорией с флагом -r
        FileExistsError: Если целевая директория уже существует
    """
    directory_get = Path(dir_get)
    directory_to = Path(dir_to)

    if not directory_get.exists():
        raise FileNotFoundError(f"File {directory_get} does not exist")

    if  directory_to.exists() and  directory_to.is_dir():
        final_dir =  directory_to / directory_get.name
    else:
        final_dir =  directory_to

    if final_dir.exists() and  directory_to.samefile(final_dir):
        raise ValueError(f"Directory {directory_get} already exists")

    if "-r" in flags:
        if not directory_get.is_dir():
            raise NotADirectoryError(f"Source is not a directory")
        if final_dir.exists():
            raise FileExistsError(f"Directory {final_dir} already exists")
        return shutil.copytree(directory_get, final_dir)
    else:
        if directory_get.is_dir():
            raise IsADirectoryError(f"Source is not a directory")

        return shutil.copy2(directory_get, final_dir)

def mv(dir_get, dir_to):
    """
    команда mv
    Args:
        dir_get (str): Источник перемещения
        dir_to (str): Целевой путь
    Raises:
        FileNotFoundError: Если источник не существует
    """
    directory_get = Path(dir_get)
    directory_to = Path(dir_to)

    if not directory_get.exists():
        raise FileNotFoundError(f"File {directory_get} does not exist")
    if directory_to.is_dir() and directory_to.exists():
        directory_to2 = directory_to / directory_get.name
        return shutil.move(directory_get, directory_to2)
    elif directory_to.is_dir() and not directory_to.exists():
        return shutil.move(directory_get, directory_to)
    elif not(directory_to.is_dir() and directory_to.exists()):
        return shutil.move(directory_get, directory_to)

def rm(dir_del, flag):
    """
    команда rm
    Args:
        dir_del: Путь к удаляемому объекту
        flag: Флаг
    Raises:
        NotADirectoryError: Если объект не существует
        PermissionError: Если попытка удалить защищенную директорию
        NotFlagError: Если для удаления директории не указан флаг -r
        InvalidInputError: Если ввод пользователя неверен
    """

    directory_del = Path(dir_del).resolve()
    if not directory_del.exists():
        raise NotADirectoryError(f"Directory {directory_del} does not exist")

    ogr_paths = {Path("\\"), Path("~"), Path.home().resolve(), Path.cwd().parent.resolve()}

    if directory_del.resolve() in ogr_paths:
        raise PermissionError(f"Directory {directory_del} cannot be removed")

    if directory_del.is_file():
            return os.remove(directory_del)
    elif directory_del.is_dir():
        if flag and flag[0] == "-r":
            confirmation_user = input(f"Remove {directory_del}? [y/n]: ").strip().lower()
            if confirmation_user == "y":
                shutil.rmtree(directory_del)
            elif confirmation_user == "n":
                return print("cancellation")
            else:
                raise InvalidInputError(f"Invalid input: {confirmation_user}")
        else:
            raise NotFlagError("for delete directory use flag: -r")
    else:
        raise ValueError(f"{directory_del} is not a directory ir file")

def create_zip(folder, archive):
    """
    создание zip архива
    Args:
        folder: Путь к исходной директории
        archive: Путь к создаваемому архиву
    Raises:
        FileNotFoundError: Если директория не существует
        NotADirectoryError: Если путь не является директорией
        ArchiveError: Если произошла ошибка при создании архива
    """

    folder = Path(folder)
    archive = Path(archive)

    if not folder.exists():
        raise FileNotFoundError(f"Folder {folder} does not exist")
    if not folder.is_dir():
        raise NotADirectoryError(f"Folder {folder} is not a directory")

    log_command(f"Creating zip {archive}")

    try:
        with zipfile.ZipFile(archive, "w") as zip_file:
            for file in folder.rglob("*"):
                if file.is_file():
                    try:
                        arcname = file.relative_to(folder)
                    except ValueError:
                        arcname = file.name
                    zip_file.write(file, arcname)
                    log_success(f"Added {arcname}")
        log_success(f"Created {archive}")
    except Exception as e:
        log_error(f"Failed to create zip: {e}")
        raise ArchiveError(f"Failed to create zip: {e}")

def extract_zip(archive, extract_path = None):
    """
    извлечение zip архива
    Args:
        archive: Путь к архиву
        extract_path: Путь для извлечения
    Raises:
        FileNotFoundError: Если архив не существует
        InvalidArchiveError: Если файл не является zip архивом
        ArchiveError: Если произошла ошибка при извлечении
    """

    archive = Path(archive)

    if not archive.exists():
        raise FileNotFoundError(f"File {archive} does not exist")
    if not zipfile.is_zipfile(archive):
        raise InvalidArchiveError(f"File {archive} is not a zip file")

    if extract_path is None:
        extract_path = archive.parent / archive.stem
    else:
        extract_path = Path(extract_path)

    extract_path.mkdir(parents=True, exist_ok=True)

    log_command(f"Extracting {archive}")

    try:
        with zipfile.ZipFile(archive, "r") as zip_file:
            file = zip_file.testzip()
            if file is not None:
                raise InvalidArchiveError(f"File {file} already exists")
            file_list = zip_file.namelist()

            zip_file.extractall(extract_path)

            for file in file_list:
                log_success(f"Extracted {file}")

    except Exception as e:
        log_error(f"Failed to extract zip: {e}")
        raise ArchiveError(f"Failed to extract zip: {e}")

def create_tar(folder, archive):
    """
    создание tar архива
    Args:
        folder: Путь к исходной директории
        archive : Путь к создаваемому архиву
    Raises:
        FileNotFoundError: Если директория не существует
        ArchiveError: Если произошла ошибка при создании архива
    """
    folder = Path(folder)
    archive = Path(archive)

    if not folder.exists():
        raise FileNotFoundError(f"Folder {folder} does not exist")

    log_command(f"Creating tar {archive}")

    try:
        with tarfile.open(archive, "w:gz") as tar:
            for file in folder.rglob("*"):
                if file.is_file():
                    try:
                        arcname = file.relative_to(folder)
                    except ValueError:
                        arcname = file.name
                    tar.add(file, arcname)
                    log_success(f"Added {arcname}")
            log_success(f"Created {archive}")
    except Exception as e:
        log_error(f"Failed to create tar: {e}")
        raise ArchiveError(f"Failed to create tar: {e}")

def extract_tar(archive, extract_path = None):
    """
    извлечение tar архива
     Args:
        archive: Путь к архиву
        extract_path: Путь для извлечения
    Raises:
        FileNotFoundError: Если архив не существует
        InvalidArchiveError: Если файл не является tar архивом
        ArchiveError: Если произошла ошибка при извлечении
    """
    archive = Path(archive)

    if not archive.exists():
        raise FileNotFoundError(f"File {archive} does not exist")
    if not tarfile.is_tarfile(archive):
        raise InvalidArchiveError(f"File {archive} is not a tar file")

    if extract_path is None:
        archive_name = archive.stem
        if archive_name.endswith('.tar'):
            archive_name = archive_name[:-4]
        extract_path = archive.parent / archive_name
    else:
        extract_path = Path(extract_path)

    extract_path.mkdir(parents=True, exist_ok=True)

    log_command(f"Extracting {archive}")
    try:
        with tarfile.open(archive, "r:*") as tar:
            file_list = tar.getnames()
            tar.extractall(extract_path)
            for file in file_list:
                log_success(f"Extracted {file}")
        log_success(f"Extracted {archive}")
    except tarfile.TarError as e:
        log_error(f"Failed to extract tar: {e}")
        raise ArchiveError(f"Failed to extract tar: {e}")











        
    

    
    


