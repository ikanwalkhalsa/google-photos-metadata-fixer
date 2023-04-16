import datetime
import zipfile
import shutil
import glob
import json
import sys
import os

source_folder = sys.argv[1] if len(sys.argv)>1 else os.environ.get('HOME')+'/Downloads'
destination_folder = source_folder + f'/Output-{datetime.datetime.now().strftime("%Y%m%dT%H%M%S")}'

intermediate_folder_name = 'Takeout'
intermediate_folder_path = source_folder + f'/Takeout'
zip_pattern = '/takeout-*.zip'
folder_pattern = '/takeout-*/Takeout/*/*'
all_rec_pattern = '/takeout-*/Takeout/*/*/**'

def print_bar(i:int, l:int, n_bars=50)->None:
    print ("\033[A                             \033[A")
    n_pipes = n_bars if i==l else i // (l // n_bars) if l > n_bars else (n_bars // l) * i
    n_pipes %= (n_bars+1)
    bar = '|'*n_pipes + '-'*(n_bars-n_pipes)
    print('\t', bar, f'({i}/{l})')

def unzip_files(all_zip_files:list) -> None:
    print()
    for i, zip_file in enumerate(all_zip_files):
        if os.path.exists(zip_file[:-4]):
            continue
        print_bar(i+1, len(all_zip_files))
        with zipfile.ZipFile(zip_file, "r") as fl:
            fl.extractall(zip_file[:-4])

def create_intermediate_locations(locations:list)->None:
    if not os.path.exists(intermediate_folder_path):
        os.mkdir(intermediate_folder_path)
    print()
    for i, loc in enumerate(locations):
        print_bar(i+1, len(locations))
        if os.path.isdir(loc):
            loc = ''.join(loc.split(intermediate_folder_name)[1:])
            intermediate_loc = intermediate_folder_path
            for fol in loc.split('/'):
                intermediate_loc += '/'+fol
                if not os.path.exists(intermediate_loc):
                    os.mkdir(intermediate_loc)

def move_files_to_intermediate_locations(all_files:str):
    print()
    for i, fl in enumerate(all_files):
        if not os.path.isfile(fl):
            continue
        file_intermediate_loc = intermediate_folder_path + ''.join(fl.split(intermediate_folder_name)[1:])
        if not os.path.exists(file_intermediate_loc):
            print_bar(i+1, len(all_files))
            shutil.copy2(fl, file_intermediate_loc)
            os.remove(fl)

def get_json_name(fl:str):
    fl_1 = fl[:47] if fl.startswith('/') else fl[:46]
    jsn = f'{fl_1}.json'
    if '(' in fl:
        s, e = fl.index('('), fl.index(')')
        if fl == fl_1:
            jsn = f'{fl[:s]+fl[e+1:]+fl[s:e+1]}.json'
        else:
            jsn = f'{fl_1+fl[s:e+1]}.json'
    return jsn

def create_file_metadata_pairs(intermediate_locations:list) -> tuple:
    valid_pairs, remaining_files = [], []
    print()
    for i, loc in enumerate(intermediate_locations):
        loc_name = ''.join(loc.split(intermediate_folder_name)[1:])
        print_bar(i+1, len(intermediate_locations))
        loc_files = glob.glob(loc+'/*')
        json_files = [fl.split(loc_name)[-1] for fl in loc_files if fl.endswith('.json')]
        non_json_files = [fl.split(loc_name)[-1] for fl in loc_files if fl.split(loc_name)[-1] not in json_files]
        for fl in non_json_files:
            jsn = get_json_name(fl)
            if jsn in json_files:
                valid_pairs.append((intermediate_folder_path+loc_name+fl, intermediate_folder_path+loc_name+jsn))
            else:
                remaining_files.append(intermediate_folder_path+loc_name+fl)
    return valid_pairs, remaining_files

def search_metadata_global(remaining_files:list, all_json_files:list) -> tuple:
    json_file_names = [fl.split('/')[-1] for fl in all_json_files]
    valid_pairs, failed = [], []
    for fl in remaining_files:
        fl_name = fl.split('/')[-1]
        jsn = get_json_name(fl_name)
        try:
            jsn_idx = json_file_names.index(jsn)
            valid_pairs.append(fl, all_json_files[jsn_idx])
        except ValueError:
            failed.append(fl)
    return valid_pairs, failed

def merge_file_metadata(file_metadata_pair:list) -> None:
    if not os.path.exists(destination_folder):
        os.mkdir(destination_folder)

    print()
    for i, (fl, md) in enumerate(file_metadata_pair):
        file_name = fl.split('/')[-1]
        destination_file_path = f'{destination_folder}/{file_name}'
        if os.path.exists(destination_file_path):
            continue
        with open(md) as json_file:
            json_md = json.load(json_file)
        create_time = int(json_md.get('photoTakenTime',{}).get('timestamp', '0'))
        if not create_time:
            create_time = int(json_md.get('creationTime',{}).get('timestamp', '0'))
        if create_time:
            print_bar(i+1, len(file_metadata_pair))
            shutil.copy2(fl, destination_file_path)
            os.utime(destination_file_path, (create_time, create_time))
            os.remove(fl)
            os.remove(md)

def handle_remaining_files(remaining_files:list) -> None:
    fail_path = destination_folder+'/FAILED'
    print('\nMoving Remaining Files to ', fail_path)
    if not os.path.exists(fail_path):
        os.mkdir(fail_path)
    print()
    for i, fl in enumerate(remaining_files):
        print_bar(i+1, len(remaining_files))
        fl_name =fl.split('/')[-1]
        shutil.copy2(fl, fail_path+'/'+fl_name)
        os.remove(fl)

def clean_dir()->None:
    all_zip_folders = [fl[:-4] for fl in glob.glob(source_folder+zip_pattern)]
    print()
    for i, fl in enumerate(all_zip_folders):
        print_bar(i+1, len(all_zip_folders)+1)
        shutil.rmtree(fl, ignore_errors=True)
    print_bar(len(all_zip_folders)+1, len(all_zip_folders)+1)
    shutil.rmtree(intermediate_folder_path, ignore_errors=True)

def main()->None:
    print('\nFixing Google Takeout MetaData : ', source_folder)
    all_zip_files = glob.glob(source_folder+zip_pattern)
    print('Found',len(all_zip_files), 'zip files, Unzipping...')
    unzip_files(all_zip_files)

    print('Creating Intermediate Locations...')
    required_locations = glob.glob(source_folder+folder_pattern)
    create_intermediate_locations(required_locations)

    print('Moving Files to Intermediate Location...')
    all_files = glob.glob(source_folder+all_rec_pattern, recursive=True)
    move_files_to_intermediate_locations(all_files)

    print('Creating File Pairs...')
    all_files = [fl for fl in glob.glob(intermediate_folder_path+'/**/*', recursive=True) if os.path.isfile(fl)]
    all_json_files = [fl for fl in all_files if fl.endswith('.json')]
    new_locations = glob.glob(intermediate_folder_path+'*/**/*')
    valid_pairs, remaining_files = create_file_metadata_pairs(new_locations)
    additional_pairs, remaining_files = search_metadata_global(remaining_files, all_json_files)
    valid_pairs += additional_pairs
    
    print('Merging Files with metadata...')
    merge_file_metadata(valid_pairs)

    if len(remaining_files):
        handle_remaining_files(remaining_files)

    print('Cleaning Directories...')
    clean_dir()
    
    print('\nAll Files (MetaData+File) : ', len(all_files))
    print('JSON Files                : ', len(all_json_files))
    print('Files with MetaData       : ', len(valid_pairs))
    print('Files without MetaData    : ', len(remaining_files))
    print('Finished! Files saved in the following location')
    print(destination_folder)


if __name__ == '__main__':
    main()
