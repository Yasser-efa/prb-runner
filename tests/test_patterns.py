import pytest

from prb.patterns import check_patterns
from prb.sources import read_sources


@pytest.fixture
def check(tmp_path):
    def run(code):
        (tmp_path / "code.py").write_text(f"import re\n\n{code}\n", encoding="utf-8")
        return [problem.message for problem in check_patterns(read_sources(tmp_path)["code.py"])]

    return run


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        ("[a-z", "crochet [ non fermé"),
        ("(abc", "parenthèse ( non fermée"),
        ("abc)", "parenthèse ) en trop"),
        ("*a", "répétition sans rien devant"),
        ("a**", "deux répétitions à la suite"),
        ("a{2,1}", "répétition dont le minimum dépasse le maximum"),
        (r"\y", r"échappement inconnu \y"),
        ("a\\", "barre \\ seule à la fin"),
        ("[z-a]", "intervalle incorrect z-a"),
        (r"(a)\2", "le groupe 2 n'existe pas"),
        ("(?P=nom)", "le groupe 'nom' n'existe pas"),
        ("(?P<nom>a)(?P<nom>b)", "deux groupes nommés 'nom'"),
        ("(?<=a+)b", "(?<=…) doit avoir une longueur fixe"),
        ("(?z)", "unknown extension ?z"),
    ],
)
def test_bad_patterns(check, pattern, expected):
    found = check(f"re.search({pattern!r}, 'texte')")
    assert found == [f"expression régulière incorrecte : {expected}"]


@pytest.mark.parametrize(
    "pattern", [r"\d+", "[A-Z]{2,} [A-Z]{2,}", "(?P<nom>a)(?P=nom)", "a{2", "}]", "é[à-ü]", ""]
)
def test_good_patterns(check, pattern):
    assert check(f"re.search({pattern!r}, 'texte')") == []


@pytest.mark.parametrize(
    "line",
    [
        "motif = re.compile('(')",
        "re.sub('(', '', 'a')",
        "re.search(pattern='(', string='a')",
        "re.search('(' + 'a', 'a')",
        "re.search(f'(a', 'a')",
        "re.search(b'(a', b'a')",
        "import re as motifs\nmotifs.findall('(', 'a')",
        "from re import split\nsplit('(', 'a')",
        "from re import fullmatch as complet\ncomplet('(', 'a')",
        "re.search('''(a  # fin )\n''', 'a', re.VERBOSE)",
    ],
)
def test_where_patterns_are_found(check, line):
    assert len(check(line)) == 1


@pytest.mark.parametrize(
    "line",
    [
        "'a(b'.split('(')",
        "re.escape('(')",
        "motif = '('\nre.search(motif, 'a')",
        "nombre = 2\nre.search(f'(a{nombre}', 'a')",
        "def search(texte):\n    return texte\n\n\nsearch('(')",
        "re.search('''(a)  # commentaire (\n''', 'a', flags=re.X)",
        "re.search()",
    ],
)
def test_what_is_not_a_written_pattern(check, line):
    assert check(line) == []
