"""PyCharm project files: excluded folders and the current exercise as sources root.

The folder of the current exercise must be a sources root, otherwise PyCharm underlines in
red imports that are correct (``from paquet.module import fonction``).
"""

import xml.etree.ElementTree as ElementTree
from pathlib import Path

EXCLUDED = ("_prive", "sources", "mes_solutions/_archives", ".venv")
_PREFIX = "file://$MODULE_DIR$"
_SOLUTIONS = f"{_PREFIX}/mes_solutions/"

_MODULES = """<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/.idea/{name}" filepath="$PROJECT_DIR$/.idea/{name}" />
    </modules>
  </component>
</project>
"""

_MODULE = """<?xml version="1.0" encoding="UTF-8"?>
<module type="PYTHON_MODULE" version="4">
  <component name="NewModuleRootManager">
    <content url="file://$MODULE_DIR$" />
    <orderEntry type="inheritedJdk" />
    <orderEntry type="sourceFolder" forTests="false" />
  </component>
</module>
"""


def configure(root: Path, exercise_id: str | None = None) -> bool:
    """Create or update the PyCharm module file.

    :param root: the project folder
    :param exercise_id: the exercise to use as sources root, None to leave it unchanged
    :return: True if a file was written
    """
    idea = root / ".idea"
    idea.mkdir(exist_ok=True)
    path = _module_file(idea, root.name)
    created = not path.exists()
    if created:
        path.write_text(_MODULE, encoding="utf-8")
    modules = idea / "modules.xml"
    if not modules.exists():
        modules.write_text(_MODULES.format(name=path.name), encoding="utf-8")
    return _update(path, exercise_id) or created


def _module_file(idea: Path, name: str) -> Path:
    """Find the module file created by PyCharm, or choose its name."""
    existing = sorted(idea.glob("*.iml"))
    return existing[0] if existing else idea / f"{name}.iml"


def _update(path: Path, exercise_id: str | None) -> bool:
    tree = ElementTree.parse(path)
    content = tree.find("./component[@name='NewModuleRootManager']/content")
    if content is None:
        return False
    before = ElementTree.tostring(tree.getroot())
    if exercise_id is not None:
        url = f"{_SOLUTIONS}{exercise_id}"
        for folder in content.findall("sourceFolder"):
            if folder.get("url", "").startswith(_SOLUTIONS) and folder.get("url") != url:
                content.remove(folder)
        if not any(folder.get("url") == url for folder in content.findall("sourceFolder")):
            content.insert(0, ElementTree.Element("sourceFolder", url=url, isTestSource="false"))
    excluded = {folder.get("url") for folder in content.findall("excludeFolder")}
    for name in EXCLUDED:
        if f"{_PREFIX}/{name}" not in excluded:
            ElementTree.SubElement(content, "excludeFolder", url=f"{_PREFIX}/{name}")
    if ElementTree.tostring(tree.getroot()) == before:
        return False
    ElementTree.indent(tree)
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    return True
