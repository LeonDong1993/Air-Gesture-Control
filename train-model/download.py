import os, json
import numpy as np 
from collections import defaultdict

OUTPUT_DIR = './downloaded_data/'
os.makedirs(OUTPUT_DIR)

data_specification = [('stop','https://sc.link/gXgk'),
                      ('fist','https://sc.link/wgB8'),
                      ('one','https://sc.link/oJqX'),
                      ('peace','https://sc.link/l6nM'),
                      ('like','https://sc.link/r7wp'),
                      ('ok','https://sc.link/pV0V')  ]

anno_file_url = 'https://sc.link/BE5Y'

# download anotation first
os.system('wget {} -O {} -o /dev/null'.format(anno_file_url, 'anno.zip'))
os.system('unzip anno.zip > /dev/null && rm anno.zip')
os.system(f'mv ann_train_val ./{OUTPUT_DIR}/annotations')

# download images for each class, only keep part of them 
np.random.seed(3)
NUM_THRESH = 2500

for class_name, url in data_specification:
    print(f'Working on {class_name} ....')
    os.system('wget {} -O {}.zip -o /dev/null'.format(url, class_name))
    os.makedirs(f'./{OUTPUT_DIR}/imgs/{class_name}', exist_ok = True)
    os.system('unzip {}.zip -d ./{}/imgs/{}/ > /dev/null && rm {}.zip'.format(
        class_name, OUTPUT_DIR, class_name, class_name))
    
    # keep only part of the images
    with open(f'./{OUTPUT_DIR}/annotations/{class_name}.json') as f:
        anno_info = json.load(f)
    
    user_imgs = defaultdict(list)
    for imgid in anno_info:
        uid = anno_info[imgid]['user_id']
        user_imgs[uid].append(imgid)
    
    print(f'Total number of users in class {class_name}:{len(user_imgs)}')
    
    keep = set()
    for uid in user_imgs:
        n = len(user_imgs[uid])
        ind = np.random.randint(0,n)
        keep.add(user_imgs[uid][ind])
        if len(keep) >= NUM_THRESH:
            break
    
    print(f'Total number of images kept is {len(keep)}.')
    
    # remove imgs that are not wanted to save disk space 
    for imgid in anno_info:
        if imgid not in keep:
            os.system(f'rm {OUTPUT_DIR}/imgs/{class_name}/{imgid}.jpg')
    