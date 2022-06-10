#!/usr/bin/env python3
import sys
import os
from os.path import abspath, join, dirname, isfile

sys.path.insert(0, abspath(join(dirname(__file__), "..")))

import numpy as np
import glob

from collections.abc import Mapping
import json

import argparse

from opensfm import dataset
from opensfm import features

def load_json(d, u):
    for k, v in u.items():
        if isinstance(v, Mapping):
            d[k] = load_json(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def load_json_file(json_file):
    jdata = {}
    with open(json_file,"r",encoding='utf-8') as f:
        jdata = load_json(jdata, json.load(f))
    return jdata


def find_track_id(data, recon, tracks_manager, image_name, x, y, dth):

    ixy  = np.empty((1, 2))
    ixy[:,0] = x
    ixy[:,1] = y

    h, w = data.image_size(image_name)

    for track, obs in tracks_manager.get_shot_observations(image_name).items():
        if track in recon.points:
            coord = recon.points[track].coordinates

            oxy  = np.empty((1, 2))
            oxy[:,0] = obs.point[0]
            oxy[:,1] = obs.point[1]
            oxy = features.denormalized_image_coordinates(oxy, w, h)

            idist = np.linalg.norm(oxy-ixy,ord=2)
            if idist < dth:
                return track
    return None

def save_json_file(dv, json_file):
    with open(json_file, "w") as fp:
        json.dump(dv,fp)
    return

def parse_geocalib_file(geo_file, data, recon, tracks_manager, corr_dict):

    print( f'parsing file {geo_file}')

    match_dict = load_json_file(geo_file)

    n_found = 0
    for vs in match_dict['allCorrespondences'].items():
        if not 'frame' in vs[1]:
            continue
        if not 'others' in vs[1]:
            continue
        if vs[1]['others'] == None:
            continue

        fname = vs[1]['frame']['frame']
        fx = vs[1]['frame']['x']
        fy = vs[1]['frame']['y']

        oname = vs[1]['others'][0]['frame']
        ox = vs[1]['others'][0]['x']
        oy = vs[1]['others'][0]['y']

        if os.path.dirname(fname) == 'views':
            obs_x = fx
            obs_y = fy
            trk_x = ox
            trk_y = oy
            imtag = os.path.basename(fname).replace('_features.png','')
            cname = os.path.basename(oname).replace('_features.png','')
        else:
            obs_x = ox
            obs_y = oy
            trk_x = fx
            trk_y = fy
            imtag = os.path.basename(oname).replace('_features.png','')
            cname = os.path.basename(fname).replace('_features.png','')

        trk_id = find_track_id(data, recon, tracks_manager, cname, trk_x, trk_y, dth)
        if trk_id == None:
            continue

        n_found += 1
        coord = recon.points[trk_id].coordinates

        if imtag in corr_dict:
            corr_dict[ imtag ].append( [obs_x, obs_y, coord[0], coord[1], coord[2]] )
        else:
            corr_dict[ imtag ] = [ [obs_x, obs_y, coord[0], coord[1], coord[2]] ]

    print( f'parsing file {geo_file}: found matches in file {len(match_dict["allCorrespondences"])} : Initialized {n_found} track-correspondences' )

    return corr_dict



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Find track ID from point coordinate on image')
    parser.add_argument('--dataset',
                        help='path to the dataset to be processed')
    parser.add_argument('--geocalib',
                        help='geocalib generated file or folder')
    parser.add_argument('--dth', type=float,
                        help='distance threshold for assigning tracks', default=3)

    args = parser.parse_args()

    dataset_folder = args.dataset

    if not isfile(args.geocalib):
        print('geocalib file needs to be set')
        sys.exit(1)

    geocalib_files = []
    if isfile(args.geocalib):
        geocalib_files.append(args.geocalib)
    else:
        geocalib_files = glob.glob(args.geocalib+"/*.cscn")

    data = dataset.DataSet(args.dataset)
    tracks_manager = data.load_tracks_manager()
    reconstructions = data.load_reconstruction()
    if len(reconstructions) > 0:
        recon = reconstructions[0]
    else:
        print('could not load reconstruction')

    data = None
    tracks_manager = None
    recon = None

    if args.dth:
        dth = args.dth
    else:
        dth = 3.0

    corr_dict = {}

    for geo_file in geocalib_files:
        corr_dict = parse_geocalib_file(geo_file, data, recon, tracks_manager, corr_dict)

    for fkey in corr_dict:
        jfile = dataset_folder + '/corrs-' + fkey + '.json'
        jdata = {}
        jdata['corrs'] = corr_dict[fkey]
        save_json_file(jdata, jfile)


