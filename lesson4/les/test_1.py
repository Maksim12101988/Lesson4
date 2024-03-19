from checkers import getout
import yaml
from sshcheckers import ssh_checkout, upload_files

with open('config.yaml') as f:
    # читаем документ YAML
    data = yaml.safe_load(f)

class TestPositive:

    def save_log(self, print_time, name):
        with open(name, 'w') as f:
            f.write(getout(f'journalctl --since"{print_time}"'))

    def test_step0(self, print_time):
        res = []
        upload_files(data["host"], data["user"], data["password"], "tests/p7zip-full.deb", "/home/user2/p7zip-full.deb")
        res.append(ssh_checkout(data["host"], data["user"], data["password"], "echo '11' | sudo -S dpkg -i /home/user2/p7zip-full.deb",
                                "Настраивается пакет"))
        res.append(ssh_checkout(data["host"], data["user"], data["password"], "echo '11' | sudo -S dpkg -s p7zip-full",
                                "Status: install ok installed"))
        self.save_log(print_time, "log1.txt") # save_checkout
        assert all(res), "test0 FAIL"

    def test_step1(self, make_folders, clear_folders, make_files, print_time):
        # test1
        res1 = ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_in']}; 7z a {data['folder_out']}/arx", "Everything is Ok")
        res2 = ssh_checkout(data["host"], data["user"], data["password"], f"ls {data['folder_out']}", "arx.7z")
        assert res1 and res2, "test1 FAIL"

    def test_step2(self, clear_folders, make_files):
        # test2
        res = []
        res.append(ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_in']}; 7z a {data['folder_out']}/arx", "Everything is Ok"))
        res.append(ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_out']}; 7z e arx.7z -o{data['folder_ext']} -y", "Everything is Ok"))
        for item in make_files:
            res.append(ssh_checkout(data["host"], data["user"], data["password"], f"ls {data['folder_ext']}", item))
        assert all(res)

    def test_step3(self):
        # test3
        assert ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_out']}; 7z t arx.7z", "Everything is Ok"), "test3 FAIL"

    def test_step4(self):
        # test4
        assert ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_in']}; 7z u arx2.7z", "Everything is Ok"), "test4 FAIL"

    def test_step5(self, clear_folders, make_files):
        # test5
        res = []
        res.append(ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_in']}; 7z a {data['folder_out']}/arx", "Everything is Ok"))
        for i in make_files:
            res.append(ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_out']}; 7z l arx.7z", i))
        assert all(res), "test5 FAIL"

    def test_step6(self, clear_folders, make_files, make_subfolder):
        # test6
        res = []
        res.append(ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_in']}; 7z a {data['folder_out']}/arx", "Everything is Ok"))
        res.append(ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_out']}; 7z x arx.7z -o{data['folder_ext2']} -y", "Everything is Ok"))
        for i in make_files:
            res.append(ssh_checkout(data["host"], data["user"], data["password"], f"ls {data['folder_ext2']}", i))
        res.append(ssh_checkout(data["host"], data["user"], data["password"], f"ls {data['folder_ext2']}", make_subfolder[0]))
        res.append(ssh_checkout(data["host"], data["user"], data["password"], f"ls {data['folder_ext2']}/{make_subfolder[0]}", make_subfolder[1]))
        assert all(res), "test6 FAIL"

    def test_step7(self):
        # test7
        assert ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_out']}; 7z d arx.7z", "Everything is Ok"), "test7 FAIL"

    def test_step8(self, clear_folders, make_files):
        # test8
        res = []
        for i in make_files:
            res.append(ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_in']}; 7z h {i}", "Everything is Ok"))
            hash = getout(f"cd {data['folder_in']}; crc32 {i}").upper()
            res.append(ssh_checkout(data["host"], data["user"], data["password"], f"cd {data['folder_in']}; 7z h {i}", hash))
        assert all(res), "test8 FAIL"

    def test_step99(self):
        res = []
        res.append(ssh_checkout(data["host"], data["user"], data["password"],
                                "echo '11' | sudo -S dpkg -r p7zip-full",
                                "Удаление пакета"))
        res.append(ssh_checkout(data["host"], data["user"], data["password"],
                                "echo '11' | sudo -S dpkg -s p7zip-full",
                                "Status: deinstall ok uninstalled"))

        assert all(res), "test99 FAIL"
