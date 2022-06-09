#!/usr/bin/env python3
import os
import sys
from os.path import abspath, join, dirname, isdir
from os import mkdir

sys.path.insert(0, abspath(join(dirname(__file__), "..")))

import argparse
import numpy as np
from numpy import ndarray

import cv2

from opensfm import dataset
from opensfm import features

def draw_rendered_image(data, recon, tracks_manager, image_name, verbose=False):

    img = data.load_image(image_name)
    h, w, c = img.shape

    features_data = data.load_features(image_name)
    assert features_data
    points = features.denormalized_image_coordinates(features_data.points, w, h)

    n_tracks = 0
    for track, obs in tracks_manager.get_shot_observations(image_name).items():
        if track in recon.points:
            ix = points[obs.id][0].round().astype(int)
            iy = points[obs.id][1].round().astype(int)
            if ix > 1 and ix < w-1 and iy > 1 and iy < h-1:
                img[iy,ix] = (255,0,0)
                img[iy-1,ix] = (255,0,0)
                img[iy+1,ix] = (255,0,0)
                img[iy,ix-1] = (255,0,0)
                img[iy,ix+1] = (255,0,0)
                n_tracks += 1

    if verbose:
        print( f'{image_name}: found {n_tracks} tracks out of {len(points)} features')

    cv2.imwrite( out_folder + "/" + image_name + "_features.png", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    return


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Find track ID from point coordinate on image')
    parser.add_argument('--dataset',
                        help='path to the dataset to be processed')
    parser.add_argument('--image',
                        help='image name to render the tracked-features for')
    parser.add_argument('--images',  help="render for all images", action='store_true')

    args = parser.parse_args()

    data = dataset.DataSet(args.dataset)

    out_folder = args.dataset + "/rendered"
    if not isdir(out_folder):
        mkdir(out_folder)

    tracks_manager = data.load_tracks_manager()

    reconstructions = data.load_reconstruction()
    if len(reconstructions) > 0:
        recon = reconstructions[0]
    else:
        print('could not load reconstruction')
        sys.exit(1)

    if args.images:
        print('render for all')
        for im_name in data.images():
            print( f'{im_name}' )
            draw_rendered_image(data, recon, tracks_manager, im_name)
    elif args.image:
        draw_rendered_image(data, recon, tracks_manager, args.image, verbose=True)
    else:
        print('set either an image or enable for all images')
        sys.exit(1)
