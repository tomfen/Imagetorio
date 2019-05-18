import cv2
from glob import glob

import numpy as np

for file in glob(r'C:\Users\Tomek\Desktop\pics\fff\*.png'):
    img = cv2.imread(file)
    img = img.astype('float')
    sq = img**2
    sqavg = np.average(np.average(sq, 0), 0)
    b, g, r = np.sqrt(sqavg)

    print('([%.0f., %.0f., %.0f.], %s)' % (b, g, r, file))
