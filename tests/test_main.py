import subprocess


def test_main():
    subprocess.check_output('python3 pocket_stats', shell=True)
