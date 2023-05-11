import json, os, cv2
import numpy as np
from glob import glob

DOWN_SAMPLE = True
source_dir = './downloaded_data/'
output_dir = './output/'

splits = [('train', 1000), ('test', 100)]
classes = ['stop', 'fist', 'one', 'peace', 'like' ,'ok']


n_splits = len(splits)
n_img = sum([item[1] for item in splits])
np.random.seed(3)

os.system(f'rm -rf hagrid_coco_format/ {output_dir}')


for label in classes:
    print(f'Working on {label}......')
    with open(f'./{source_dir}/annotations/{label}.json') as f:
        anno_info = json.load(f)

    all_imgs = glob(f'{source_dir}/imgs/{label}/*.jpg')
    all_ids = [item.split('/')[-1][:-4] for item in all_imgs]
    selected = np.random.choice(len(all_ids), size = n_img, replace = False)

    i = 0
    for phase, size in splits:
        img_dir = f'{output_dir}/imgs/{phase}/{label}/'
        anno_dir = f'{output_dir}/annotations/ann_{phase}/'
        os.makedirs(img_dir, exist_ok = True)
        os.makedirs(anno_dir, exist_ok = True)

        anno = {}
        j = i+size
        for k in range(i,j):
            imgid = all_ids[ selected[k] ]
            anno[imgid] = anno_info[imgid]

            if not DOWN_SAMPLE:
                os.system(f'cp {all_imgs[selected[k]]} {img_dir}')
            else:
                img = cv2.imread(all_imgs[selected[k]])
                h,w = img.shape[:2]
                img = cv2.resize(img, [w//2, h//2])
                cv2.imwrite(f'{img_dir}/{imgid}.jpg', img)


        with open(f'{anno_dir}/{label}.json', 'w+') as f:
            json.dump(anno, f)
        i = j



# set the converter
converter_config = '''
dataset:
  dataset_annotations: {}/annotations/
  dataset_folder: {}/imgs/
  phases: [train, test]
  targets:
    - fist
    - like
    - ok
    - one
    - peace
    - stop
'''.format(output_dir, output_dir)

with open('convert_conf.yaml', 'w+') as f:
    f.write(converter_config)

# run convert
os.system('python hagrid_to_coco.py --cfg convert_conf.yaml')






