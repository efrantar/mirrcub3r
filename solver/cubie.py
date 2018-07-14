from defs import *


class CubieCube:

    @staticmethod
    def make(cp, co, ep, eo):
        c = CubieCube()
        c.cp = cp # corner permutation
        c.co = co # corner orientations
        c.ep = ep # edge permutation
        c.eo = eo # edge orientations
        return c

    @staticmethod
    def make_solved():
        return CubieCube.make(
            [URF, UFL, ULB, UBR, DFR, DLF, DBL, DRB], [0] * N_CORNERS,
            [UR, UF, UL, UB, DR, DF, DL, DB, FR, FL, BL, BR], [0] * N_EDGES
        )


    MOVES = [
        # U
        make(
            [UBR, URF, UFL, ULB, DFR, DLF, DBL, DRB], [0] * N_CORNERS,
            [UB, UR, UF, UL, DR, DF, DL, DB, FR, FL, BL, BR], [0] * N_EDGES
        ),
        # R
        make(
            [DFR, UFL, ULB, URF, DRB, DLF, DBL, UBR], [2, 0, 0, 1, 1, 0, 0, 2],
            [FR, UF, UL, UB, BR, DF, DL, DB, DR, FL, BL, UR], [0] * N_EDGES
        ),
        # F
        make(
            [UFL, DLF, ULB, UBR, URF, DFR, DBL, DRB], [1, 2, 0, 0, 2, 1, 0, 0],
            [UR, FL, UL, UB, DR, FR, DL, DB, UF, DF, BL, BR], [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0]
        ),
        # D
        make(
            [URF, UFL, ULB, UBR, DLF, DBL, DRB, DFR], [0] * N_CORNERS,
            [UR, UF, UL, UB, DF, DL, DB, DR, FR, FL, BL, BR], [0] * N_EDGES
        ),
        # L
        make(
            [URF, ULB, DBL, UBR, DFR, UFL, DLF, DRB], [0, 1, 2, 0, 0, 2, 1, 0],
            [UR, UF, BL, UB, DR, DF, FL, DB, FR, UL, DL, BR], [0] * N_EDGES
        ),
        # B
        make(
            [URF, UFL, UBR, DRB, DFR, DLF, ULB, DBL], [0, 0, 1, 2, 0, 0, 2, 1],
            [UR, UF, UL, BR, DR, DF, DL, BL, FR, FL, UB, DB], [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1]
        )
    ]


    @static_method
    def _mul(p1, p2):
        p3 = [-1] * len(p1)
        for i in range(len(p1)):
            p3[i] = p1[p2[i]]
        return p3

    def mul_corners(self, other):
        self.cp = _mul(self.cp, other.cp)
        self.co = [(self.co[other.cp[i]] + other.co[i]) % 3 for i in range(N_CORNERS)]

    def mul_edges(self, other):
        self.ep = _mul(self.ep, other.ep)
        self.eo = [(self.eo[other.ep[i]] + other.eo[i]) & 1 for i in range(N_EDGES)]


    @staticmethod
    def _encode1(a, basis):
        c = 0
        for i in range(len(a) - 1):
            c = basis*c + a[i]
        return c

    @staticmethod
    def _decode1(c, a, basis):
        par = 0
        for i in range(len(a) - 2, -1, -1):
            a[i] = c % basis
            par += a[i]
            c //= basis
        a[len(a)-1] = (basis - (par % basis)) % basis

    @staticmethod
    def _encode2(p, elems):
        p1 = [-1] * len(elems)
        
        c1 = 0 # positions
        j = 0
        for i in range(1, len(a)):
            if p[i] in elems:
                c1 += cnk(i, j + 1)
                p1[j] = p[i]
                j += 1
                
        c2 = 0 # permutation
        for i in range(len(elems) - 1, 0, -1):
            cnt = 0
            while p1[i] != elems[i]:
                # Left rotate by 1
                tmp = p1[0]
                for j in range(1, i + 1):
                    p1[j-1] = p1[j]
                p1[i] = tmp
                cnt += 1
            c2 = (c2 + cnt) * i

        return math.factorial(len(elems)) * c1 + c2

    @staticmethod
    def _decode2(c, p, elems):
        elems = elems.copy() # we don't want to mess up the passed array       
        # We want to modify the passed parameter        
        for i in range(len(p)):
            p[i] = -1

        tmp = math.factorial(len(elems))
        c1 = c // tmp
        c2 = c % tmp

        for i in range(1, len(elems)):
            cnt = c2 % (i + 1)
            for _ in range(cnt):
                # Right rotate by 1
                tmp = elems[i]
                for j in range(i):
                    elems[j+1] = elems[j]
                elems[0] = tmp
            c2 //= (i + 1)

        j = len(elems) - 1
        for i in range(len(p) - 1, -1, -1):
            tmp = cnk(i, j + 1)
            if c1 - tmp >= 0:
                p[i] = elems[j]
                c1 -= tmp
                j -= 1

        # cnt = 0
        # for i in range(len(p)):
        #     if p[i] == 0:
        #         while cnt in elems:
        #             cnt += 1
        #         p[i] = cnt
        #         cnt += 1


    FRBR_EDGES = [FR, FL, BL, BR]
    URFDLF_CORNERS = [URF, UFL, ULB, UBR, DFR, DLF]
    URUL_EDGES = [UR, UF, UL]
    UBDF_EDGES = [UB, DR, DF]
    URDF_EDGES = URUL_EDGES + UBDF_EDGES

    def get_twist(self):
        return _encode1(self.co, MAX_CO + 1)

    def set_twist(self, c):
        _decode1(c, self.co, MAX_CO + 1)

    def get_flip(self):
        return _encode1(self.eo, MAX_EO + 1)

    def set_flip(self, c):
        _decode1(c, self.eo, MAX_EO + 1)

    def get_frbr(self):
        return _encode2(self.ep, FRBR_EDGES)

    def set_frbr(self, c):
        _decode2(c, self.ep, FRBR_EDGES)

    def get_urfdlf(self):
        return _encode2(self.cp, URFDLF_CORNERS)

    def set_urfdlf(self, c):
        _decode2(c, self.cp, URFDLF_CORNERS)

    def get_urul(self):
        return _encode2(self.ep, URUL_EDGES)

    def set_urul(self, c):
        _decode2(c, self.ep, URUL_EDGES)

    def get_ubdf(self):
        return _encode2(self.ep, UBDF_EDGES)

    def set_ubdf(self):
        return _decode2(c, self.ep, UBDF_EDGES)

    def get_urdf(self):
        return _encode2(self.ep, URDF_EDGES)

    def set_urdf(self, c):
        _decode(c, self.ep, URDF_EDGES)

    
    @staticmethod
    def merge_urdf(urul, ubdf):
        c1 = make_solved()
        c1.set_urul(urul)
        c2 = make_solved()
        c2.set_ubdf(ubdf)

        for i in range(N_EDGES - len(FRBR_EDGES)):
            if c2.ep[i] in UBDF_EDES:
                c1.ep[i] = c2.ep[i]

        return c1.get_urdf()

    @static_method
    def check(self):
        pass


def cnk(n, k):
    c = 1
    for i in range(min(k, n - k)):
        c = c * (n-i) / (i+1)
    return c

