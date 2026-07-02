"""Generating version_info.txt from version.py"""
import re
from pathlib import Path


def parse_version(version_str: str) -> tuple:
    """Converts the version string to the tuple"""
    parts = version_str.split('.')
    while len(parts) < 4:
        parts.append('0')
    return tuple(int(p) for p in parts[:4])


def generate_version_info(version_str: str, output_path: Path):
    """Генерирует version_info.txt."""
    version_tuple = parse_version(version_str)
    major, minor, build, revision = version_tuple

    content = f"""# UTF-8
#
# Automatically generated from version.py
# Version: {version}

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {build}, {revision}),
    prodvers=({major}, {minor}, {build}, {revision}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'Neptune Noise'),
            StringStruct(u'FileDescription', u'My Little Neptune'),
            StringStruct(u'FileVersion', u'{version_str}'),
            StringStruct(u'InternalName', u'MyLittleNeptune.exe'),
            StringStruct(u'LegalCopyright', u'© 2025-2026 Neptune Noise. All rights reserved.'),
            StringStruct(u'OriginalFilename', u'MyLittleNeptune.exe'),
            StringStruct(u'ProductName', u'My Little Neptune'),
            StringStruct(u'ProductVersion', u'{version_str}'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [0x409, 0x4B0])])
  ]
)
"""

    output_path.write_text(content, encoding='utf-8')
    print(f"[INFO] Generated {output_path} with version: {major}.{minor}.{build}.{revision}")


if __name__ == "__main__":
    version_file = Path(__file__).parent / 'version.py'

    if version_file.exists():
        content = version_file.read_text(encoding='utf-8')
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            version = match.group(1)
            generate_version_info(version, Path(__file__).parent / 'version_info.txt')
        else:
            print("[ERROR] Not Found __version__ в version.py")
    else:
        print("[ERROR] version.py not found")