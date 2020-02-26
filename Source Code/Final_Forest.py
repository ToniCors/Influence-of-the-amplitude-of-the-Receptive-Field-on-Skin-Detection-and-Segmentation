import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.image as img
import ast
import math
import pickle
from sklearn.ensemble import RandomForestClassifier as rfc
import pandas as pd

def save_predictions(prediction, path, n_rows, n_cols, block_size, treshold):
    plt.imsave(path, np.array(build_output_mask(n_rows, n_cols, prediction, block_size, treshold)), cmap=cm.gray)

def create_name_string(number):
    s = str(number)
    for i in range(5 -len(s)):
        s = '0' + s
    return s

def fetch_images(start_index, end_index):
    images = []
    masks = []
    for i in range(start_index, end_index):
        cur = create_name_string(i)
        images.append(img.imread('ECU\\001\\im'+cur+'.jpg'))
        masks.append(img.imread('ECU\\masks\\001\\im'+cur+'_s.bmp'))
        
    return np.asarray(images), np.asarray(masks)

from math import *
def get_hue(r, g, b):

    nr = r/255
    ng = g/255
    nb = b/255

    hue = 0.0

    mi = min(min(nr, ng), nb);
    ma = max(max(nr, ng), nb);

    if (mi == ma):
        return hue

    if (ma == nr):
        hue = (ng - nb) / (ma - mi)

    elif (ma == ng):
        hue = 2.0 + (nb - nr) / (ma - mi)

    else:
        hue = 4.0 + (nr - ng) / (ma - mi)

    hue = hue * 60

    if (hue < 0):
        hue = hue + 360

    hue = round(hue)
    return hue

def feature_extractor(image):
    height = len(image)
    width = len(image[0])
    #print(str(height)+" "+str(width))
    
    features_image = []
    
    for i in range(height):
        row = []
        for j in range(width):
            
            r = image[i][j][0]
            g = image[i][j][1]
            b = image[i][j][2]
                        
            #conversion to YCrCb
            y = (.299*r + .587*g + .114*b)
            cb = (128 -.168736*r -.331364*g + .5*b)
            cr = (128 +.5*r - .418688*g - .081312*b)
            
            values = [y, cb, cr, get_hue(r, g, b), r/255]
            row.append(values)
        features_image.append(row)
    
    return features_image

def compute_features(images):
    result = []
    avoid=[]
    for i in range(len(images)):
        print(i)
        try:
            result.append(feature_extractor(images[i]))
        except:
            avoid.append(i)
            print("Exception happened!! - exc. number "+str(len(avoid)))
    return result, avoid

def get_block(section, block_size):
    block = np.asarray([])
    for i in range(block_size):
        for j in range(block_size):
            block = np.insert(block, len(block), section[i][j], 0)
    return np.asarray(block)

def get_separate_blocks(items, block_size, avoid = []):
    
    blocks = []
    for k in range(len(items)):
        if k in avoid:
            continue
        item = np.asarray(items[k])
        height = len(item)
        width = len(item[1])
        n_horizontal_blocks = int(math.floor(width/block_size))
        n_vertical_blocks = int(math.floor(height/block_size))

        for i in range(n_vertical_blocks):
            for j in range(n_horizontal_blocks):
                section = np.asarray(item[(i*block_size) : ((i+1)*block_size), (j*block_size) :((j+1)*block_size)])
                
                blocks.append(get_block(section, block_size))

    return np.asarray(blocks)

#Questa funzione ricostruisce la maschera a partire dalle predizioni fatte dagli algoritmi

def build_output_mask_separate(n_rows, n_cols, predictions, block_size):

    n_horizontal_blocks = int(math.floor(n_cols/block_size))
    n_vertical_blocks = int(math.floor(n_rows/block_size))
            
    height = n_vertical_blocks*block_size
    width = n_horizontal_blocks*block_size
    
    out_mask = np.zeros((n_vertical_blocks*block_size, n_horizontal_blocks*block_size), int)


    for i in range(n_vertical_blocks):
        for j in range(n_horizontal_blocks):
            p = predictions[(i*n_horizontal_blocks)+j]
            #current = out_mask[(i*block_size) : ((i+1)*block_size), (j*block_size) :((j+1)*block_size)]
            out_mask[(i*block_size) : ((i+1)*block_size), (j*block_size) :((j+1)*block_size)] =  np.reshape(p, (block_size, block_size))
            
    return height, width, out_mask

def get_accuratezza_singola(pred, ground):
    TP = float(0)
    TN = float(0)
    FP = float(0)
    FN = float(0)
    n_rows = len(pred)
    n_cols = len(pred[0])
    for i in range(n_rows):
        for j in range(n_cols):
            if ground[i][j] == 255 and pred[i][j] == 255:
                TN = TN + 1
            elif ground[i][j] == 255 and pred[i][j] == 0:
                FP = FP + 1
            elif ground[i][j] == 0 and pred[i][j] == 0:
                TP = TP + 1
            elif ground[i][j] == 0 and pred[i][j] == 255:
                FN = FN + 1
    
    precision = TP/(TP+FP)
    recall=TP/(TP+FN)
    
    f_measure=2*((precision*recall)/(precision+recall))
    
    print("F_Measure = "+str(f_measure))
    return TP, TN, FP, FN

def get_accuratezza_globale(preds, grounds, avoid = []):
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    n_img = len(preds)
    for i in range(n_img):
        if i in avoid:
            continue
        print(i)
        cTP, cTN, cFP, cFN = get_accuratezza_singola(preds[i], grounds[i])
        
        TP = TP + cTP
        TN = TN + cTN
        FP = FP + cFP
        FN = FN + cFN
        
    precision = TP/(TP+FP)
    recall=TP/(TP+FN)
    f_measure=2*((precision*recall)/(precision+recall))
    print("F_Measure = "+str(f_measure))
    return TP, TN, FP, FN

def scale_labels(labels, block_size):
    new_labels = []
    
    for k in range(len(labels)):
        c = []
        for i in range(block_size*block_size):
            if labels[k][i] == 0:
                c.append(0)
            else :
                c.append(1)
        new_labels.append(c)
    return np.asarray(new_labels)

def add_border(vertical_diff, horizontal_diff, image):
    height = len(image)
    width = len(image[0])
    mask = np.zeros((height+(2*vertical_diff), width+(2*horizontal_diff), 5), int)
    mask[vertical_diff:height+vertical_diff, horizontal_diff: width+horizontal_diff] = image
    return mask

def join_predictions(p1, p2, height, width, h_dif, v_dif, block_size, treshold):
    a, b, mask1 = build_output_mask_separate(height+v_dif, width+h_dif, p1, block_size)
    a, b, mask2 = build_output_mask_separate(height+v_dif, width+h_dif, p2, block_size)
    
    mask1 = mask1[v_dif:height+v_dif, h_dif:width+h_dif]
    mask2 = mask2[0:height, 0:width]
    
    mask = mask1 + mask2
    
    for i in range(height):
        for j in range(width):
            if mask[i, j] == 2:
                mask[i, j] = 255
            else:
                mask[i, j] = 0
    return mask

def get_prediction(classifier, image, block_size):
    height=len(image)
    width=len(image[0])

    horizontal_difference = block_size - (width % block_size)
    vertical_difference = block_size - (height % block_size)

    image = add_border(vertical_difference, horizontal_difference, image)

    b1 = get_separate_blocks([image[0:height+vertical_difference, 0:width+horizontal_difference]], block_size)
    b2 = get_separate_blocks([image[vertical_difference:height+(2*vertical_difference), horizontal_difference:width+(2*horizontal_difference)]], block_size)

    p1 = classifier.predict(b1)
    p2 = classifier.predict(b2)

    return join_predictions(p1, p2, height, width, horizontal_difference, vertical_difference, block_size, 2)

def get_predictions(classifier, images, block_size):
    l = len(images)
    predictions = []
    for i in range(l):
        predictions.append(get_prediction(classifier, images[i], block_size))
    return predictions

def adjust_pred(prediction):
    image = []
    for i in range(len(prediction)):
        row = []
        for j in range(len(prediction[0])):
            p = int(prediction[i][j][0])
            if p == 1:
                p = 255
            row.append(p)
        image.append(row)
    return np.asarray(image)

## Codice per l'allenamento e la serializzazione dei classificatori

images_train, masks_train = fetch_images(1, 3)
images_train_features, avoid_train = compute_features(images_train)

block_sizes = [1, 2, 5, 10, 20]
for i in range(len(block_sizes)):
    block_size = block_sizes[i]
    clf = rfc(n_estimators = 50, max_depth = 20)
    blocks_images_train = get_separate_blocks(images_train_features, block_size)
    print(1)
    blocks_masks_train = get_separate_blocks(masks_train, block_size, avoid_train)
    print(2)
    blocks_masks_train = scale_labels(blocks_masks_train, block_size)
    print(3)
    clf.fit(blocks_images_train, blocks_masks_train)
    print(4)
    pickle.dump(clf, open('C1_'+str(block_size)+'.sav', 'wb'))
    print("DONE! "+str(block_size))

# Codice per calcolare una serie di predizioni con i classificatori serializzati e salvarle

block_sizes = [1, 2, 5, 10, 20]

images_to_save, masks_to_save = fetch_images(3, 6)
im_features_save, avoid_save = compute_features(images_to_save)

for i in range(len(block_sizes)):
    block_size = block_sizes[i]
    clf = pickle.load(open("C1_"+str(block_size)+".sav", 'rb'))
    print("Caricato "+str(block_size))
    p = get_predictions(clf, im_features_save, block_size)
    print("Predizioni fatte "+str(block_size))
    for j in range(len(p)):
        cur = p[j]
        plt.imsave("immagini_test_2//predizione_N_"+str(j)+"_BS_"+str(block_size)+".png", cur, cmap=cm.gray)
    print("Finito "+str(block_size)+" !!!!")

## Codice per il calcolo di precisione, richiamo ed f measure sulle predizioni

block_sizes = [1, 2, 5, 10, 20]
out_file = open("results_pr_2.txt", "w")
TP_count = [float(0), float(0), float(0), float(0), float(0)]
TN_count = [float(0), float(0), float(0), float(0), float(0)]
FP_count = [float(0), float(0), float(0), float(0), float(0)]
FN_count = [float(0), float(0), float(0), float(0), float(0)]
c = 0
for m in range(len(masks_to_save)):
    if (m % 50) == 0:
        print("iterazione "+str(m)+" #################")
    cur_p = [0, 0, 0, 0, 0]
    cur_r = [0, 0, 0, 0, 0]
    cur_f = [0, 0, 0, 0, 0]
    current_mask = masks_to_save[m]
    try:
        for b in range(len(block_sizes)):
            block_size = block_sizes[b]
            current_pred = adjust_pred(img.imread("immagini_test_2//predizione_N_"+str(m)+"_BS_"+str(block_size)+".png"))
            TP, TN, FP, FN = get_accuratezza_singola(current_pred, current_mask)
            TP_count[b] = TP_count[b] + TP
            TN_count[b] = TN_count[b] + TN
            FP_count[b] = FP_count[b] + FP
            FN_count[b] = FN_count[b] + FN
            precision = TP/(TP+FP)
            recall=TP/(TP+FN)
            f_measure=2*((precision*recall)/(precision+recall))
            cur_p[b] = precision
            cur_r[b] = recall
            cur_f[b] = f_measure
    except:
        c = c + 1
        continue
    out_file.write("\n img "+str(1500+m) +": \n P = "+str(cur_p)+" R = "+str(cur_r)+" F ="+str(cur_f))
print("#Exceptions = "+str(c))
print("Global F_scores:")
out_file.write("\n Global Results \n")
for b in range(len(block_sizes)):
    print("Block_size = " + str(block_sizes[b]))
    tp = TP_count[b]
    tn = TN_count[b]
    fp = FP_count[b]
    fn = FN_count[b]
    precision = tp/(tp+fp)
    recall=tp/(tp+fn)
    f_measure=2*((precision*recall)/(precision+recall))
    print("P = "+str(precision)+" R = "+str(recall)+" F = " +str(f_measure))
    out_file.write("P = "+str(precision)+" R = "+str(recall)+" F = " +str(f_measure))

