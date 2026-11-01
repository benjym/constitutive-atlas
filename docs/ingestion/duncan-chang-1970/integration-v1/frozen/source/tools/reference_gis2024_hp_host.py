"""Independent Cartesian/source-sign HP/ASBS reference.

Only stdlib. Inputs sigma and outputs m use plain six-component Mandel sequences;
no Atlas DSL, typed evaluator or structured inverse is called.
"""
import math

S2 = math.sqrt(2)

def mat(v):
    x, y, z, u, v, w = v
    return [[x, u / S2, w / S2], [u / S2, y, v / S2], [w / S2, v / S2, z]]

def mandel(a):
    return [a[0][0], a[1][1], a[2][2], S2 * a[0][1], S2 * a[1][2], S2 * a[0][2]]

def dot(a, b):
    return sum((a[i][j] * b[i][j] for i in range(3) for j in range(3)))

def mul(a, s):
    return [[x * s for x in row] for row in a]

def add(a, b):
    return [[a[i][j] + b[i][j] for j in range(3)] for i in range(3)]

def trace(a):
    return sum((a[i][i] for i in range(3)))

def norm(a):
    return math.sqrt(dot(a, a))

def rotate(a):
    q = [[1 / 3, 2 / 3, 2 / 3], [2 / 3, 1 / 3, -2 / 3], [-2 / 3, 2 / 3, -1 / 3]]
    return [[sum((q[i][k] * a[k][l] * q[j][l] for k in range(3) for l in range(3))) for j in range(3)] for i in range(3)]

def solve(a, b):
    aug = [list(row) + [v] for row, v in zip(a, b)]
    for k in range(len(b)):
        p = max(range(k, len(b)), key=lambda i: abs(aug[i][k]))
        aug[k], aug[p] = (aug[p], aug[k])
        divisor = aug[k][k]
        if divisor == 0:
            raise ValueError('singular oracle matrix')
        aug[k] = [v / divisor for v in aug[k]]
        for i in range(len(b)):
            if i != k:
                factor = aug[i][k]
                aug[i] = [x - factor * y for x, y in zip(aug[i], aug[k])]
    return [row[-1] for row in aug]

def oracle(v):
    sigma = mul(mat(v['sigma']), -1)
    tr = trace(sigma)
    p = -tr / 3
    H = mul(sigma, 1 / tr)
    Hd = [[H[i][j] - (1 / 3 if i == j else 0) for j in range(3)] for i in range(3)]
    Q = dot(H, H)
    j2 = dot(Hd, Hd)
    psi = math.sqrt(3 * j2)
    cube = sum((Hd[i][j] * Hd[j][k] * Hd[k][i] for i in range(3) for j in range(3) for k in range(3)))
    lode = -math.sqrt(6) * cube / j2 ** 1.5 if j2 else 0
    F = math.sqrt(psi * psi / 8 + (2 - psi * psi) / (2 + math.sqrt(2) * psi * lode)) - psi / (2 * math.sqrt(2))
    a = math.sqrt(3 / 8) * (3 - math.sin(v['phi'])) / math.sin(v['phi'])
    compression = math.exp(-(3 * p / v['hs']) ** v['n'])
    ei = v['ei0'] * compression
    ec = v['ec0'] * compression
    ed = v['ed0'] * compression
    fs = v['hs'] / v['n'] * (ei / v['e']) ** v['beta'] * (1 + ei) / ei * (3 * p / v['hs']) ** (1 - v['n']) / (3 + a * a - a * math.sqrt(3) * ((v['ei0'] - v['ed0']) / (v['ec0'] - v['ed0'])) ** v['alpha'])
    fd = ((v['e'] - ed) / (ec - ed)) ** v['alpha']

    def L(X):
        return mul(add(mul(X, F * F), mul(H, a * a * dot(H, X))), 1 / Q)
    cols = [mandel(L(mat(tuple((float(i == j) for i in range(6)))))) for j in range(6)]
    matrix = [[cols[j][i] for j in range(6)] for i in range(6)]
    N = mul(add(H, Hd), F * a / Q)
    B = mat(tuple(solve(matrix, mandel(N))))
    Caux = mul(mat(tuple(solve(matrix, mandel(mul(sigma, 1 / norm(sigma)))))), 1 / fs)
    G = v['n'] / v['hs'] * trace(mul(sigma, 1 / norm(sigma))) * (3 * p / v['hs']) ** (v['n'] - 1)
    r = (1 + v['e']) / v['e']
    den = G - r * trace(Caux)
    t = r * trace(B) / den
    bracket = dot(B, B) + dot(Caux, Caux) * t * t + 2 * dot(B, Caux) * t
    fdstar = 1 / math.sqrt(bracket)
    return dict(F=F, fs=fs, fd=fd, fdAstar=fdstar, m=tuple(mandel(mul(B, 1 / norm(B)))), C=norm(B) * fdstar, S=fd / fdstar, L=matrix, B_source=B, C_source=Caux, G_source=G)
