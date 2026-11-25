"""
Fonctions annexes utilisées par d'autres modules.

Les instructions ont été volontairement « obfusquées », pour ne vous donner aucun indice sur votre propre travail.
NE RECOPIEZ NI NE MODIFIEZ CE CODE SOUS AUCUN PRÉTEXTE.
NE PERDEZ PAS DE TEMPS À ESSAYER DE COMPRENDRE CE CODE !
"""
import itertools
from collections import deque

_M, _N, _D = "mot", "note", "debut"


def f1(a, b):
    return list(_.__getitem__(b) for _ in itertools.chain(a))


def f2(a, b, c):
    deque((a[_].__setitem__(b, __) for _, __ in zip(range(c.__len__()), c)), maxlen=0)
    return a


def f3(a, b, c): return ((b, (c + _)) for (_) in range(a))


def f4(a, b, c): return (((b + _), c) for (_) in range(a))


def f5(a, b, c, d): return set(a(b, c, d))


def f6(m, d, n):
    if n.startswith('H'):
        return f5(f3, m.__len__(), *d)
    else:
        return f5(f4, m.__len__(), *reversed(d))
