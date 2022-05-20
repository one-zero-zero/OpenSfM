
import argparse
import os
import sys
import glob
import subprocess
import multiprocessing

def run_command(cmd, show_progress=False, env=None):
    if show_progress is False:
        rinfo = subprocess.run(cmd, shell=True, stdout=open(os.devnull, "wb"), env=env)
    else:
        rinfo = subprocess.run(cmd, shell=True, env=env)
    return (rinfo.returncode == 0)

def num_cpus():
    return multiprocessing.cpu_count()

def write_yaml_file(file_name, cdata):
    with open(file_name, "w") as f:
        for k in sorted(cdata):
            # skip unset values
            if cdata[k] is None:
                continue
            f.write("{}: {}\n".format(k, cdata[k]))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='process a dataset')
    parser.add_argument('--dataset-folder', '-df', type=str, help='folder containing a 360 video file', default="/external/in/")

    script_dir = os.path.dirname(os.path.realpath(__file__))

    env = os.environ.copy()
    # env["OMP_NUM_THREADS"] = str(max_threads)

    args, unknown_args = parser.parse_known_args()
    if args.dataset_folder is None:
        parser.print_help()
        sys.exit(1)

    dataset_folder = args.dataset_folder

    if not os.path.isdir( os.path.join(dataset_folder,'images') ):
        print('images/ folder is not present under the dataset folder')
        sys.exit(1)

    # generate config.yaml
    config_file = os.path.join(dataset_folder,"config.yaml")
    config_data = {
        "processes": num_cpus(),
        "align_method": "naive",
        "feature_type": "AKAZE",
        "feature_extract_from_cubemap_panorama": True,
        "feature_extract_from_cubemap_augmented": True,
        "feature_extract_save_debug_images": False,
        "feature_min_frames": 2000,
        "feature_process_size": 4096,
        "feature_min_frames_panorama": 2048,
        "feature_process_size_panorama": 2048,
        "matching_gps_distance": 0,
        "matching_gps_neighbors": 0,
        "matching_use_filters": False,
        "matching_vlad_neighbors": 0,
        "undistorted_image_max_size": 8400000,
        "matcher_type": "FLANN",
        "robust_matching_calib_threshold_same_camera": 0.004,
        "robust_matching_calib_threshold": 0.015,
        "robust_matching_threshold": 0.004,
        "five_point_algo_threshold": 0.004,
        "depthmap_num_matching_views": 8,
        "depthmap_resolution": 800,
        "robust_matching_min_match": 15,
        "lowes_ratio": 0.9
    }
    write_yaml_file(config_file, config_data)
    print("\n")

    if not os.path.isdir( os.path.join(dataset_folder, 'exif') ):
        cmd = f'/source/OpenSfM/bin/opensfm extract_metadata "{dataset_folder}"'
        print( cmd )
        run_command(cmd)
    else:
        print('found exif folder - skipping metadata extraction')

    if not os.path.isdir( os.path.join(dataset_folder, 'features') ):
        cmd = f'/source/OpenSfM/bin/opensfm detect_features "{dataset_folder}"'
        print( cmd )
        run_command(cmd)
    else:
        print('found features folder - skipping feature extraction')

    if not os.path.isdir( os.path.join(dataset_folder, 'matches') ):
        cmd = f'/source/OpenSfM/bin/opensfm match_features "{dataset_folder}"'
        print( cmd )
        run_command(cmd)
    else:
        print('found matches folder - skipping matching')

    if not os.path.isfile( os.path.join(dataset_folder, 'tracks.csv') ):
        cmd = f'/source/OpenSfM/bin/opensfm create_tracks "{dataset_folder}"'
        print( cmd )
        run_command(cmd)
    else:
        print('found tracks.csv - skipping track creation')

    if not os.path.isfile( os.path.join(dataset_folder, 'reconstruction.json') ):
        cmd = f'/source/OpenSfM/bin/opensfm reconstruct "{dataset_folder}"'
        print( cmd )
        run_command(cmd)
    else:
        print('found reconstruction.json - skipping reconstruction')

    if not os.path.isdir( os.path.join(dataset_folder, 'undistorted') ):
        cmd = f'/source/OpenSfM/bin/opensfm undistort "{dataset_folder}"'
        print( cmd )
        run_command(cmd)
    else:
        print('found undistorted folder - skipping undistortion')

    cmd = f'/source/OpenSfM/bin/opensfm export_openmvs "{dataset_folder}"'
    print( cmd )
    run_command(cmd)
