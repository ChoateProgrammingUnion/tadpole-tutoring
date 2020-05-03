
import glob
import tqdm
import subprocess
import os
import shutil

ORIGINAL_DIR = 'precompile/' 

## You can edit as you wish. You need to install all of these first.
convert = "/usr/local/bin/convert"
quality = "100"
optimizers =	{
  "jpgs": ['**/*.jpg', '/usr/local/bin/guetzli --nomemlimit --quality 100 input output'],
  "jpges": ['**/*.jpeg', '/usr/local/bin/guetzli --nomemlimit --quality 100 input output'],
  "pngs": ['**/*.png', '/usr/local/bin/pngcrush input output'],
}

for filetype, options in optimizers.items():
    print(filetype)
    glob_opt = options[0]
    print(glob_opt)
    cli_opt = options[1]
    files = glob.iglob(ORIGINAL_DIR + glob_opt, recursive=True)
    for each_file in files:
        if "screenshot-github.jpg" in each_file:
            continue

        base_filename = each_file.split('.')[0]
        print(base_filename)
        if not os.path.isfile(base_filename + ".jpg"):
            subprocess.run(convert + " " + each_file + " -quality "+ quality +" " +
                           base_filename + ".jpg", shell=True)

        if not os.path.isfile(base_filename + ".webp"):
            subprocess.run(convert + " " + each_file + " -quality "+ quality +" " +
                           base_filename + ".webp", shell=True)

        if not os.path.isfile(base_filename + ".jp2"):
            subprocess.run(convert + " " + each_file + " -quality "+ quality +" " +
                           base_filename + ".jp2", shell=True)
