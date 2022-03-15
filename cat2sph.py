from json.tool import main
from multiprocessing.spawn import _main
import numpy as np

def cart2sph(x,y,z):
    azimuth = np.arctan2(y,x)
    elevation = np.arctan2(z,np.sqrt(x**2 + y**2))
    r = np.sqrt(x**2 + y**2 + z**2)
    return azimuth, elevation, r

def sph2cart(azimuth,elevation,r):
    x = r * np.cos(elevation) * np.cos(azimuth)
    y = r * np.cos(elevation) * np.sin(azimuth)
    z = r * np.sin(elevation)
    return x, y, z

def deg2rad(angle):
    return angle * np.pi / 180

def rad2deg(angle):
    return angle * 180 / np.pi


if __name__ == '__main__':
    print(cart2sph(11.7387, -98.5493, -37.2658))
    print(sph2cart(deg2rad(-83.2072), deg2rad(-20.5806), 106.012))