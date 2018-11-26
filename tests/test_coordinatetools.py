from toon.tools import cart2pol, pol2cart, cart2sph, sph2cart


def test_2d():
    # nothing wild
    want = (3.0, 3.0)
    tup = pol2cart(*cart2pol(*want))
    tup = tuple(round(x, 7) for x in tup)
    assert(tup == want)
    # allow for different units
    tup = pol2cart(*cart2pol(*want, units='rad'), units='rad')
    tup = tuple(round(x, 7) for x in tup)
    assert(tup == want)
    # non-zero reference point
    tup = pol2cart(*cart2pol(*want, ref=(1, 3)), ref=(1, 3))
    tup = tuple(round(x, 7) for x in tup)
    assert(tup == want)


def test_3d():
    # nothing wild
    want = (3.0, 3.0, 3.0)
    tup = sph2cart(*cart2sph(*want))
    tup = tuple(round(x, 7) for x in tup)
    assert(tup == want)
    # different units
    tup = sph2cart(*cart2sph(*want, units='rad'), units='rad')
    tup = tuple(round(x, 7) for x in tup)
    assert(tup == want)
    # non-zero reference
    tup = sph2cart(*cart2sph(*want, ref=(1, 3, 5)), ref=(1, 3, 5))
    tup = tuple(round(x, 7) for x in tup)
    assert(tup == want)
