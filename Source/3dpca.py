import os
import shutil
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import itertools
parser = argparse.ArgumentParser(description="3dpca")
parser.add_argument('--evec',help='eigenvec file',required=True)
parser.add_argument('--eval',help='eigenval file',required=True)
parser.add_argument('--s',help='Scatter point size',type=float,default=40)
parser.add_argument('--c',help='Colormap name',type=str,default='brg')
parser.add_argument('--x',help='Figure width',type=float,default=10)
parser.add_argument('--y',help='Figure height',type=float,default=5)
parser.add_argument('--f',help='Font family',type=str,default="Calibri")
parser.add_argument('--fp',help='1st PC',type=int,default=1)
parser.add_argument('--sp',help='2nd PC',type=int,default=2)
parser.add_argument('--tp',help='3rd PC',type=int,default=3)
parser.add_argument('--fs',help='Font size',default=10,type=float)
parser.add_argument('--mode',help='Output mode: "int" for interactive show, solid format to save as pdf,svg or png',type=str,choices=['int', 'solid'], default='int')
parser.add_argument('--o',help='Output file prefix',type=str, default='3D_PCA')
parser.add_argument('--ft',help='Format type pdf, tif, tiff, jpg, jpeg, eps, pgf, png, ps, raw, rgba, svgz, svg or webp',choices=['pdf','svg','svgz','png','tif','tiff','jpg','jpeg','eps','pgf','ps','raw','rgba','webp'],type=str,default='jpg')
parser.add_argument('--azim', help='View azimuth angle (degrees)',   type=float, default=65)
parser.add_argument('--elev', help='View elevation angle (degrees)', type=float, default=20)
parser.add_argument('--dpi', help='dpi', type=int, default=300)
args = parser.parse_args()
print("Dataframe preparation ...")
eig = pd.read_csv(args.eval, sep='\s+', header=None).iloc[:, 0].values
percents = np.round(eig / eig.sum() * 100, 2)
i=args.fp
j=args.sp
k=args.tp
col_names = ['Breed', 'ID'] + [f"PC{i}({percents[i-1]}%)"]+[f"PC{j}({percents[j-1]}%)"]+[f"PC{k}({percents[k-1]}%)"]

data = pd.read_csv(args.evec, sep='\s+', header=None)
PCA = data.iloc[:, [0,1,i+1,j+1,k+1]].copy()
PCA.columns = col_names
print(PCA)
print("3DPlot preparation ...")
mpl.rcParams['font.family'] = args.f
mpl.rcParams['font.size']   = args.fs

markers = ["d", ",", "o", "D", "v", "H", "s", "p", "*", "h", "^","P"]
fig = plt.figure(figsize=(args.x, args.y))
ax  = fig.add_subplot(projection='3d')

PCA['Breed'] = pd.Categorical(PCA['Breed'])
labels = np.unique(PCA['Breed'])
palette = sns.color_palette(args.c, len(labels))

marker_cycle = itertools.cycle(markers)
for label, color in zip(labels, palette):
    m = next(marker_cycle)
    subset = PCA[PCA['Breed'] == label]
    ax.scatter(
    subset.iloc[:, 2],
    subset.iloc[:, 3],
    subset.iloc[:, 4],
    s=args.s,
    color=color,
    edgecolor='k',
    label=label,
    marker=m)
ax.set_xlabel(PCA.columns[2],labelpad=8)
ax.set_ylabel(PCA.columns[3],labelpad=8)
ax.set_zlabel(PCA.columns[4],labelpad=8)
ax.view_init(elev=args.elev, azim=args.azim)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=args.fs)
plt.tight_layout()
if args.mode == 'int':
    print("Displaying plot interactively with elev=%.1f, azim=%.1f" % (args.elev, args.azim))
    plt.show()
else:
    path = f"{args.o}.{args.ft}"
    plt.savefig(path, format=args.ft, dpi=args.dpi)
    print(f"Plot saved as {path} with elev={args.elev}, azim={args.azim},dpi={args.dpi}")
    plt.close('all')
