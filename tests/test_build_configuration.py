from pathlib import Path
import unittest


class BuildConfigurationTests(unittest.TestCase):
    def test_build_uses_a_pinned_verified_qt_runtime(self) -> None:
        root = Path(__file__).resolve().parents[1]
        build_script = (root / "build_executavel.bat").read_text(encoding="utf-8")
        requirements = (root / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("from PySide6 import QtCore", build_script)
        self.assertIn("--force-reinstall --no-cache-dir", build_script)
        self.assertIn("PySide6==6.8.3", requirements)
        self.assertIn("PySide6.__version__ == '6.8.3'", build_script)
        self.assertNotIn("--collect-all PySide6", build_script)
        self.assertNotIn("--collect-all shiboken6", build_script)

    def test_installer_and_executable_metadata_use_version_1_1_1(self) -> None:
        root = Path(__file__).resolve().parents[1]
        setup = (root / "installer" / "setup.iss").read_text(encoding="utf-8")
        version_info = (root / "installer" / "version_info.txt").read_text(encoding="utf-8")
        self.assertIn('#define MyAppVersion "1.1.1"', setup)
        self.assertIn("filevers=(1, 1, 1, 0)", version_info)
        self.assertIn("ProductVersion', u'1.1.1'", version_info)


if __name__ == "__main__":
    unittest.main()
