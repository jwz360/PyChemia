import numpy as np

# Define the tolerance
tol = 1.e-5


# return [x, y, d], that ax + by = d, d = gcd(a, b)
def ext_gcd(a, b):
    v1 = [1, 0, a]
    v2 = [0, 1, b]

    if a > b:
        a, b = b, a
    while v1[2] > 0:
        q = v2[2] / v1[2]
        for i in range(0, len(v1)):
            v2[i] = v2[i] - q * v1[i]
        v1, v2 = v2, v1
    return v2


def print_vector(v):
    print 'v = ',
    for i in range(3):
        print v[i],
    print "\n"


def create_surface(structure, h, k, l, layers):
    cell = structure.cell
    a1 = np.array(cell[0])
    a2 = np.array(cell[1])
    a3 = np.array(cell[2])
    rcell = structure.lattice.reciprocal().cell
    b1 = np.array(rcell[0])
    b2 = np.array(rcell[1])
    b3 = np.array(rcell[2])

    # Solve equation pk + ql = 1 for p and q using extended_Euclidean algorithm

    v = ext_gcd(k, l)
    p = v[0]
    q = v[1]
    print 'p = ', p
    print 'q = ', q

    k1 = np.dot(p * (k * a1 - h * a2) + q * (l * a1 - h * a3), l * a2 - k * a3)
    k2 = np.dot(l * (k * a1 - h * a2) - k * (l * a1 - h * a3), l * a2 - k * a3)
    print "\n\nk1 = ", k1
    print "k2 = ", k2

    if abs(k2) > tol:
        c = -int(round(k1 / k2))
        print "c = -int(round(k1/k2)) = ", c
        p, q = p + c * l, q - c * k

    # Calculate lattice vectors {v1, v2, v3} defining basis of the new cell

    v1 = p * (k * a1 - h * a2) + q * (l * a1 - h * a3)
    v2 = l * a2 - k * a3
    n = p * k + q * l
    v = ext_gcd(n, h)
    a = v[0]
    b = v[1]
    v3 = b * a1 + a * p * a2 + a * q * a3
    newbasis = np.array([v1, v2, v3])

    print '\n\n********* Lattice vectors of the original cell *********\n\n', cell
    print '\n\n********* ATOMIC positions in the original cell **********\n', structure.positions
    print '\nTotal number of atoms in cell = ', structure.natom

    # Now create the surface starting from the original structure
    surf = structure.copy()
    surf.set_cell(newbasis)

    print '\n\n********* New basis of the surface cell *********\n\n', surf.cell
    print '\n\n********* Atomic coordinates in the newbasis of surface cell *********\n\n', surf.positions

    surf = surf.supercell((1, 1, layers))
    a1, a2, a3 = surf.cell

    surf.set_cell([a1, a2,
                   np.cross(a1, a2) * np.dot(a3, np.cross(a1, a2)) /
                   np.linalg.norm(np.cross(a1, a2)) ** 2])

    # Change unit cell to have the x-axis parallel with a surface vector
    # and z perpendicular to the surface:

    a1, a2, a3 = surf.cell
    surf.set_cell([(np.linalg.norm(a1), 0, 0),
                   (np.dot(a1, a2) / np.linalg.norm(a1),
                    np.sqrt(np.linalg.norm(a2) ** 2 - (np.dot(a1, a2) / np.linalg.norm(a1)) ** 2), 0),
                   (0, 0, np.linalg.norm(a3))])

    # Move atoms into the unit cell:

    scaled = surf.reduced
    scaled[:, :2] %= 1
    surf.set_reduced(scaled)
    #    surf.center(vacuum=vacuum, axis=2)
    return surf
