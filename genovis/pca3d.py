import os,sys
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
from matplotlib import pyplot as plt
import itertools

IS_GUI = os.environ.get("GENOVIS_GUI") == "1"
def fail(msg):
    if IS_GUI:
        raise RuntimeError(msg)
    else:
        print(f"[ERROR] {msg}",file=sys.stderr,flush=True)
        sys.exit(1)

def add_subparser(subparsers):
    parser = subparsers.add_parser("pca3d",help="Plot 3D and 2D PCA plot.")
    parser.add_argument('--evec',help='eigenvec file',required=True)
    parser.add_argument('--eval',help='eigenval file',required=True)
    parser.add_argument('--dim',  help='Plot dimension', choices=['2d','3d'], default='3d')
    parser.add_argument('--s',help='Scatter point size',type=float,default=40)
    parser.add_argument('--c',help='Colormap name (please see https://matplotlib.org/stable/users/explain/colors/colormaps.html)',type=str,default='brg')
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
    parser.set_defaults(func=run)

def run(args):
    if args.s <= 0: fail("--s (scatter size) must be > 0")
    if args.x <= 0 or args.y <= 0: fail("--x/--y (figure width/height) must be > 0")
    if args.fs <= 0: fail("--fs (font size) must be > 0")
    if args.dpi < 300: fail("--dpi must be >= 300")
    if args.dim == '3d':
        if not (-360 <= args.azim <= 360): fail("--azim must be between -360 and 360 (3D only)")
        if not (-360 <= args.elev <= 360): fail("--elev must be between -360 and 360 (3D only)")
    if not os.path.isfile(args.evec): fail(f"Eigenvec file not found: {args.evec}")
    if not os.path.isfile(args.eval): fail(f"Eigenval file not found: {args.eval}")
    print("===== Dataframe preparation ... =====")
    eig = pd.read_csv(args.eval, sep=r'\s+', header=None).iloc[:, 0].values
    min_pcs = 2 if args.dim == '2d' else 3
    if eig.size < min_pcs:fail(f"Eigenval must contain at least {min_pcs} PCs for a {args.dim.upper()} plot.")
    percents = np.round(eig / eig.sum() * 100, 2)
    data = pd.read_csv(args.evec,sep=r'\s+', header=None)
    num_pc_vec = data.shape[1] - 2
    num_pc_val = eig.shape[0]
    if num_pc_vec < min_pcs: fail(f"Eigenvec must contain at least {min_pcs} PCs (found {num_pc_vec}).")
    if num_pc_vec != num_pc_val: fail(f"PC mismatch: eigenvec has {num_pc_vec} PCs but eigenval has {num_pc_val} PCs. " "Please re-generate PCA files to ensure consistency.")
    if args.dim == '2d':
        for name, pc in (("fp", args.fp), ("sp", args.sp)):
            if not isinstance(pc, int): fail(f"--{name} must be integer.")
            if pc < 1 or pc > num_pc_val: fail(f"--{name} must be between 1 and {num_pc_val}")
        if args.fp == args.sp: fail("PCs must be distinct.")
        needed_cols = 2 + max(args.fp, args.sp)
    else:
        for name, pc in (("fp", args.fp), ("sp", args.sp), ("tp", args.tp)):
            if not isinstance(pc, int): fail(f"--{name} must be integer.")
            if pc < 1 or pc > num_pc_val: fail(f"--{name} must be between 1 and {num_pc_val}")
        if len({args.fp, args.sp, args.tp}) < 3: fail("PCs must be distinct.")
        needed_cols = 2 + max(args.fp, args.sp, args.tp)
    if data.shape[1] < needed_cols: fail(f"Eigenvec file has only {data.shape[1]} columns, but needs at least {needed_cols}.")
    mpl.rcParams['font.family'] = args.f
    mpl.rcParams['font.size']   = args.fs
    if args.dim == '2d':
        i, j = args.fp, args.sp
        col_names = ['Breed', 'ID', f"PC{i}({percents[i-1]}%)", f"PC{j}({percents[j-1]}%)"]
        PCA = data.iloc[:, [0, 1, i+1, j+1]].copy()
        PCA.columns = col_names
    else:
        i, j, k = args.fp, args.sp, args.tp
        col_names = ['Breed', 'ID',
                    f"PC{i}({percents[i-1]}%)",
                    f"PC{j}({percents[j-1]}%)",
                    f"PC{k}({percents[k-1]}%)"]
        PCA = data.iloc[:, [0, 1, i+1, j+1, k+1]].copy()
        PCA.columns = col_names
    print(PCA)
    PCA['Breed'] = pd.Categorical(PCA['Breed'])
    labels = np.unique(PCA['Breed'])
    palette = sns.color_palette(args.c, len(labels))
    markers = ["d", ",", "o", "D", "v", "H", "s", "p", "*", "h", "^", "P"]
    marker_cycle = itertools.cycle(markers)
    fig = plt.figure(figsize=(args.x, args.y))
    if args.dim == '2d':
        print("Plotting 2d-PCA plot")
        ax = fig.add_subplot(111)
        for label, color in zip(labels, palette):
            m = next(marker_cycle)
            subset = PCA[PCA['Breed'] == label]
            ax.scatter(subset.iloc[:, 2], subset.iloc[:, 3],
                    s=args.s, color=color, edgecolor='k', label=label, marker=m)
        ax.set_xlabel(PCA.columns[2], labelpad=8)
        ax.set_ylabel(PCA.columns[3], labelpad=8)
    else:
        print("Plotting 3d-PCA plot")
        ax=fig.add_subplot(projection='3d')
        for label, color in zip(labels, palette):
            m=next(marker_cycle)
            subset = PCA[PCA['Breed'] == label]
            ax.scatter(subset.iloc[:, 2],subset.iloc[:, 3],subset.iloc[:, 4],s=args.s,color=color,edgecolor='k',label=label,marker=m)
        ax.set_xlabel(PCA.columns[2], labelpad=8)
        ax.set_ylabel(PCA.columns[3], labelpad=8)
        ax.set_zlabel(PCA.columns[4], labelpad=8)
        ax.view_init(elev=args.elev, azim=args.azim)

    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=args.fs)
    plt.tight_layout()

    suffix = '2D' if args.dim == '2d' else '3D'
    if args.mode == 'int':
        print(f"Displaying {suffix} PCA plot...")
        plt.show()
    else:
        path = f"{args.o}_{suffix}.{args.ft}"
        plt.savefig(path, format=args.ft, dpi=args.dpi)
        print(f"Plot saved as {path} (dpi={args.dpi})")
        plt.close('all')