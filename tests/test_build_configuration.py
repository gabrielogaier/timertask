from pathlib import Path
import unittest


class BuildConfigurationTests(unittest.TestCase):
    def test_build_collects_qt_runtime_from_a_verified_environment(self) -> None:
        root = Path(__file__).resolve().parents[1]
        build_script = (root / "build_executavel.bat").read_text(encoding="utf-8")
        self.assertIn("from PySide6 import QtCore", build_script)
        self.assertIn("--force-reinstall --no-cache-dir", build_script)
        self.assertIn("--collect-all PySide6", build_script)
        self.assertIn("--collect-all shiboken6", build_script)

    def test_installer_and_executable_metadata_use_version_1_1_1(self) -> None:
        root = Path(__file__).resolve().parents[1]
        setup = (root / "installer" / "setup.iss").read_text(encoding="utf-8")
        version_info = (root / "installer" / "version_info.txt").read_text(encoding="utf-8")
        self.assertIn('#define MyAppVersion "1.1.1"', setup)
        self.assertIn("filevers=(1, 1, 1, 0)", version_info)
        self.assertIn("ProductVersion', u'1.1.1'", version_info)


if __name__ == "__main__":
    unittest.main()
