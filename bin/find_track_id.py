#!/usr/bin/env python3
import sys
from os.path import abspath, join, dirname

import numpy as np
from numpy import ndarray

sys.path.insert(0, abspath(join(dirname(__file__), "..")))

import argparse

from opensfm import dataset
from opensfm import features

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Find track ID from point coordinate on image')
    parser.add_argument('--dataset',
                        help='path to the dataset to be processed')
    parser.add_argument('--image',
                        help='image name to search for the point x,y')
    parser.add_argument("--x", type=float, help="image x-coordinate to search for")
    parser.add_argument("--y", type=float, help="image y-coordinate to search for")
    parser.add_argument('--dth', type=float, help="allowed distance threshold")

    args = parser.parse_args()

    data = dataset.DataSet(args.dataset)
    ixy  = np.empty((1, 2))
    ixy[:,0] = args.x
    ixy[:,1] = args.y

    image_name: str = args.image
    tracks_manager = data.load_tracks_manager()

    img = data.load_image(image_name)
    h, w, c = img.shape

    reconstructions = data.load_reconstruction()
    if len(reconstructions) > 0:
        recon = reconstructions[0]
        for track, obs in tracks_manager.get_shot_observations(image_name).items():
            if track in recon.points:
                coord = recon.points[track].coordinates

                oxy  = np.empty((1, 2))
                oxy[:,0] = obs.point[0]
                oxy[:,1] = obs.point[1]
                oxy = features.denormalized_image_coordinates(oxy, w, h)

                idist = np.linalg.norm(oxy-ixy,ord=2)
                if idist < args.dth:
                    print( f'track id {track} obs id {obs.id} : coords {coord[0]}, {coord[1]}, {coord[2]} | observation {oxy[:,0]}, {oxy[:,1]} | dist {idist}' )

    else:
        print ('could not load reconstruction')
