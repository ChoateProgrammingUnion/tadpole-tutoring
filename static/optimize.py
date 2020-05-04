import glob
import hashlib
import os
import pickle
import shutil
import subprocess

import tqdm

ORIGINAL_DIR = 'precompile/'
OUTPUT_DIR = 'compiled/'
UPDATE = True
QUALITY = '85'

# You can edit as you wish. You need to install all of these first.
convert = "/usr/local/bin/convert"
optimizers = {
    "jpgs-guetzli": [
        '**/*.jpg', '/usr/local/bin/guetzli --nomemlimit --quality ' + QUALITY
        + ' input output'
    ],
    "jpgs-optim": ['**/*.jpg', 'jpegoptim --strip-all -d output input'],
    "jpges-guetzli": [
        '**/*.jpeg', '/usr/local/bin/guetzli --nomemlimit --quality ' + QUALITY
        + ' input output'
    ],
    "jpges-optim": ['**/*.jpeg', 'jpegoptim --strip-all -d output input'],
    "pngs": ['**/*.png', '/usr/local/bin/pngcrush input output'],
    "css-minify": ['**/*.css', 'minify -o output input'],
    "css-csso": ['**/*.css', 'csso input --comments none -o output'],
    # "js-closure-compiler": [
        # '**/*.js',
        # 'closure-compiler --js input --js_output_file output -O ADVANCED'
    # ],
    "js-minify": ['**/*.js', 'minify -o output input'],
    # "js-uglify": ['**/*.js', 'uglifyjs --compress input -o output'],
    "html": ['**/*.html', 'minify -o output input'],
    "svgo": ['**/*.svg', 'svgo -i input -o output'],
    "webp": [
        '**/*.webp',
        'cwebp input -o output -z 9 -m 6 -mt -pass 10 -metadata all -q ' +
        QUALITY
    ]
}


def sha_hash(filename):
    # Credit: https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


if os.path.isfile('cache.pickle'):
    cache_pickle = open("cache.pickle", "rb")
    cache = pickle.load(cache_pickle)  # Make sure you trust this!
    cache_pickle.close()
else:
    cache = {}

glob_history = []
for filetype, options in optimizers.items():
    print(filetype)
    glob_opt = options[0]
    if not glob_opt in glob_history:
        glob_history.append(glob_opt)
        SEEN = False
    else:
        SEEN = True

    print(glob_opt)
    cli_opt = options[1]
    print(cli_opt)
    files = glob.iglob(ORIGINAL_DIR + glob_opt, recursive=True)
    for each_file in files:
        print(each_file)
        output_location = each_file.replace(ORIGINAL_DIR, OUTPUT_DIR)
        print(output_location)
        if os.path.isfile(output_location) and UPDATE and each_file in cache:
            time = os.path.getmtime(each_file)
            other_time = os.path.getmtime(output_location)
            if time < other_time:
                continue
            if cache[each_file] == sha_hash(each_file):
                continue

        if "screenshot-github.jpg" in each_file:
            continue

        if SEEN:
            shutil.move(output_location, each_file)

        if not os.path.exists(os.path.dirname(output_location)):
            try:
                os.makedirs(os.path.dirname(output_location))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        command = cli_opt.replace(' output', ' ' + output_location).replace(
            'input', each_file)
        print(command)
        subprocess.run(command, shell=True)
        cache[each_file] = sha_hash(each_file)

cache_pickle = open("cache.pickle", "wb")
pickle.dump(cache, cache_pickle)
cache_pickle.close()

# Copy
entire_directory = glob.iglob(ORIGINAL_DIR + '**', recursive=True)
for each_file in entire_directory:
    output_location = each_file.replace(ORIGINAL_DIR, OUTPUT_DIR)
    if os.path.isfile(output_location) and UPDATE:
        time = os.path.getmtime(each_file)
        other_time = os.path.getmtime(output_location)
        if time < other_time:
            continue

    if not os.path.exists(os.path.dirname(output_location)):
        try:
            os.makedirs(os.path.dirname(output_location))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    if os.path.isfile(each_file):
        shutil.copy(each_file, output_location)
