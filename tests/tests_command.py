import tarfile
import zipfile

from src.logger import setup_logging, log_success, log_error, log_command, log_warning
import pytest

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.commands import ls, cd, cat, cp, mv, rm, create_zip, extract_zip, create_tar, extract_tar



class TestCommands:

    def test_ls(self, fs):
        """Тест команды ls"""
        fs.create_file("/file1.txt", contents="content1")
        fs.create_file("/file2.txt", contents="content2")
        fs.create_dir("/subdir")
        fs.create_dir("/test_dir")
        fs.create_file("/test_dir/file3.txt", contents="test")

        result = ls("/")

        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "subdir" in result
        assert "test_dir" in result

    def test_ls_does_not_exist(self, fs):
        """Тест команды ls, при несуществующей директории"""
        with pytest.raises(FileNotFoundError):
            ls("nonexistent_directory")

    def test_ls_l(self, fs):
        """Тест команды ls с флагом -l"""
        fs.create_file("/file1.txt", contents="content1")

        result = ls("/")

        assert len(result) > 0
        assert any("file1.txt" in line for line in result)

    def test_cd(self, fs):
        """Тест команды cd"""
        fs .create_dir("/subdir")
        start_path = os.getcwd()
        new_path = cd("/subdir")

        path2 = os.path.normpath("/subdir")

        assert os.getcwd() != start_path
        assert os.path.exists(new_path)
        assert os.path.isdir(new_path)
        assert os.getcwd() == new_path

    def test_cd_parent(self, fs):
        """Тест cd для родительской директории"""
        fs.create_dir("/subdir")
        start_dir = os.getcwd()
        cd("/subdir")
        assert os.getcwd() != start_dir

        cd("..")
        assert os.getcwd() == start_dir

    def test_cd_does_not_exist(self, fs):
        """Тест для не существующий директории"""
        with pytest.raises(FileNotFoundError):
            cd("nonexistent_directory")

    def test_cat(self, fs):
        """Тест команды cd"""
        content = "content"
        fs.create_file("/file1.txt", contents=content)

        result = cat("/file1.txt")
        assert result == content

    def test_cat_does_not_exist(self, fs):
        """Тест чтения не существющего файла"""
        with pytest.raises(FileNotFoundError):
            cat("/nonexistent_directory")

    def test_cat_directory_error(self, fs):
        """Тест чтения директории вместо файла"""
        fs.create_dir("/test_dir")

        with pytest.raises(IsADirectoryError):
            cat("/test_dir")

    def test_cp_without_r(self, fs):
        """тест команды cp бух фдага -r"""
        fs.create_file("/file1.txt", contents="content1")
        fs.create_dir("test_dir")

        cp("/file1.txt", "/test_dir", [])
        cp("/file1.txt", "/file2.txt", [])

        assert os.path.exists("/file2.txt")
        assert os.path.exists("/file1.txt")
        assert open("/file2.txt").read() == "content1"
        assert os.path.exists("/test_dir/file1.txt")
        assert open("/test_dir/file1.txt").read() == "content1"

        with pytest.raises(IsADirectoryError):
            cp("/test_dir", "/test2_dir", [])

    def test_cp_with_r(self, fs):
        """тест команды cp с флагом -r"""
        fs.create_dir("/test1_dir")
        fs.create_file("/test1_dir/file1.txt", contents="content1")
        fs.create_dir("/test1_dir/subdir")
        fs.create_file("/test1_dir/subdir/file2.txt", contents="content2")

        cp("/test1_dir", "/test11_dir", ["-r"])

        assert os.path.exists("/test11_dir")
        assert os.path.exists("/test11_dir/file1.txt")
        assert os.path.exists("/test11_dir/subdir")
        assert os.path.exists("/test11_dir/subdir/file2.txt")
        assert open("/test11_dir/file1.txt").read() == "content1"
        assert open("/test11_dir/subdir/file2.txt").read() == "content2"

    def test_mv(self, fs):
        """Тест команды mv"""
        fs.create_file("/file1.txt", contents="content1")
        fs.create_dir("/test_dir")
        fs.create_file("/file2.txt", contents="ya_pishu_testi")

        mv("/file2.txt", "file3.txt")
        mv("/file1.txt", "test_dir")

        assert os.path.exists("/test_dir/file1.txt")
        assert not os.path.exists("/file1.txt")
        assert open("/test_dir/file1.txt").read() == "content1"
        assert os.path.exists("/file3.txt")
        assert open("/file3.txt").read() == "ya_pishu_testi"

    def test_mv_does_not_exist(self, fs):
        """Тест команды mv с несуществующим файлом"""
        with pytest.raises(FileNotFoundError):
            mv("/nonexistent_directory", "/test_dir")

    def test_rm_without_r(self, fs):
        """Тест команды rm бе флага -r"""
        fs.create_file("/file1.txt", contents="content1")
        fs.create_dir("/test_dir")

        rm("/file1.txt",[])

        assert not os.path.exists("/file1.txt")

        with (pytest.raises(Exception)):
              rm("/test_dir",[])

    def test_rm_with_r(self, fs, monkeypatch):
        """Тест команды rm с фалгом -r"""
        fs.create_dir("/test_dir")
        fs.create_file("/test_dir/file1.txt", contents="content1")

        monkeypatch.setattr("builtins.input", lambda x: "y")

        rm("/test_dir",["-r"])

        assert not os.path.exists("/test_dir")

    def test_rm_does_not_exist(self):
        """тест удаления несуществующего файла"""
        with (pytest.raises(NotADirectoryError)):
            rm("/nonexistent_dir", ["-r"])

    def test_create_and_extract_zip(self, fs):
        """Тест создания zip арихваи его извлечения"""
        fs.create_dir("/test_dir")
        fs.create_file("/test_dir/file1.txt", contents="content1")
        fs.create_dir("/test_dir/subdir")
        fs.create_file("/test_dir/subdir/file2.txt", contents="content2")

        create_zip("/test_dir", "test_dir.zip")

        assert os.path.exists("/test_dir.zip")
        assert zipfile.is_zipfile("test_dir.zip")

        with zipfile.ZipFile("test_dir.zip") as zip:
            files = zip.namelist()
            assert "file1.txt" in files
            assert "subdir/file2.txt" in files

        extract_zip("test_dir.zip", "test_extract_dir")
        assert os.path.exists("/test_extract_dir")
        assert os.path.exists("/test_extract_dir/file1.txt")
        assert open("/test_extract_dir/file1.txt").read() == "content1"

    def test_create_and_extract_tar(self, fs):
        """Тест создания и извлечения tar архива"""
        fs.create_dir("/test_dir")
        fs.create_file("/test_dir/file1.txt", contents="content1")
        fs.create_dir("/test_dir/subdir")
        fs.create_file("/test_dir/subdir/file2.txt", contents="content2")

        create_tar("/test_dir", "test_dir.tar")

        assert os.path.exists("/test_dir.tar")
        assert tarfile.is_tarfile("test_dir.tar")

        with tarfile.open("test_dir.tar", "r:gz") as tar:
            files = tar.getnames()

            assert "file1.txt" in files
            assert "subdir/file2.txt" in files

        extract_tar("/test_dir.tar", "test_dir_extracted")

        assert os.path.exists("/test_dir_extracted")
        assert os.path.exists("/test_dir_extracted/file1.txt")
        assert open("/test_dir_extracted/file1.txt").read() == "content1"

    def test_zip_does_not_exist(self, fs):
        """Тест создания и извлечения zip архива из несуществующей директории"""
        with pytest.raises(FileNotFoundError):
            create_zip("/nonexistent_directory", "test.zip")
            extract_zip("/nonexistent_directory.zip", "test")

    def test_tar_does_not_exist(self, fs):
        """Тест создания и извлечения несуществующего tar архива"""
        with pytest.raises(FileNotFoundError):
            create_tar("/nonexistent_directory", "test.tar")
            extract_tar("/nonexistent_directory.tar", "test")

class Test_Const:
    def test_const_commands(self):
        from src.const import COMMANDS
        expected = ("ls", "pwd", "cd", "cat", "cp", "mv", "rm", "zip", "unzip", "tar", "untar")
        assert COMMANDS == expected

class Test_Parse:
    def test_parse_basic_command(self):
        from src.parser import parse
        command, flags, args = parse("ls")
        assert command == "ls"
        assert flags == []
        assert args == []

    def test_parse_with_flags_and_args(self):
        from src.parser import parse
        command, flags, args = parse("cp -r qeweqwqew")
        assert command == "cp"
        assert flags == ["-r"]
        assert args == ["qeweqwqew"]

class Test_logging:
    def test_logging(self):
        setup_logging()
        log_command("test")
        log_error("test1")
        log_success("test2")
        log_success("test3")











