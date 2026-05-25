"""Generating version_info.txt from version.py"""
import re
from pathlib import Path


def parse_version(version_str: str) -> tuple:
    """Converts the version string '1.0' to the tuple (1, 0)."""
    parts = version_str.split('.')
    while len(parts) < 1:
        parts.append('0')
    return tuple(int(p) for p in parts[:5])


def generate_version_info(version: str, output_path: Path):
    """Generate version_info.txt."""
    version_tuple = parse_version(version)

    content = f"""# UTF-8
#
# Automatically generated from version.py
# Version: {version}

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
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
            StringStruct(u'FileVersion', u'{version}'),
            StringStruct(u'InternalName', u'MyLittleNeptune.exe'),
            StringStruct(u'LegalCopyright', u'© 2026 Neptune Noise. All rights reserved.'),
            StringStruct(u'OriginalFilename', u'MyLittleNeptune.exe'),
            StringStruct(u'ProductName', u'My Little Neptune'),
            StringStruct(u'ProductVersion', u'{version}'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [0x409, 0x4B0])])
  ]
)
"""

    output_path.write_text(content, encoding='utf-8')
    print(f" 📄 [DEV] Generated {output_path} with version: {version}")


if __name__ == "__main__":
    version_file = Path(__file__).parent / 'version.py'

    if version_file.exists():
        content = version_file.read_text(encoding='utf-8')
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            version = match.group(1)
            generate_version_info(version, Path(__file__).parent / 'version_info.txt')
        else:
            print(" ❌ [DEV] Not Found __version__ в version.py")
    else:
        print(" ❌ [DEV] version.py not found")