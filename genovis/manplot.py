import os, sys
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

IS_GUI = os.environ.get("GENOVIS_GUI") == "1"
def fail(msg):
    if IS_GUI:
        raise RuntimeError(msg)
    else:
        print(f"[ERROR] {msg}", file=sys.stderr, flush=True)
        sys.exit(1)

def add_subparser(subparsers):
    parser = subparsers.add_parser("manplot",help="Plot manhattan plot.")
    parser.add_argument('--d',help='Dataframe(1th column:chromosome, 2th column:position, 3th column:value)',type=str,required=True)
    parser.add_argument('--mode',help='Output mode: "int" for interactive show, solid format to save as pdf,svg or png',type=str,choices=['int','solid'],default='int')
    parser.add_argument('--c',help='Choosing colormaps (please see https://matplotlib.org/stable/users/explain/colors/colormaps.html)',default="plasma",type=str)
    parser.add_argument('--nc',help='Number of colors',default=10,type=int)
    parser.add_argument('--a',help='The alpha blending value, between 0 (transparent) and 1 (opaque)',default=1,type=float)
    parser.add_argument('--x',help='Horizontal size of figure',default=8.4,type=float)
    parser.add_argument('--y',help='Vertical size of figure',default=4,type=float)
    parser.add_argument('--s',help='Scatter size',default=0.5,type=float)
    parser.add_argument('--sug1',help='Suggestive line 1',default=None,type=float)
    parser.add_argument('--sug2',help='Suggestive line 2',default=None,type=float)
    parser.add_argument('--sug1lw',help='Width size of suggestive line 1 ',default=None,type=float)
    parser.add_argument('--sug2lw',help='Width size of suggestive line 2',default=None,type=float)
    parser.add_argument('--sug1c',help='Color of suggestive line 1',default="blue",type=str)
    parser.add_argument('--sug2c',help='Color of suggestive line 2',default="red",type=str)
    parser.add_argument('--xlab',help='X label',default="Chromosome",type=str)
    parser.add_argument('--ylab',help='Y label',default="Value",type=str)
    parser.add_argument('--f',help='Font family',default='Calibri',type=str)
    parser.add_argument('--fs',help='Font size',default=14,type=float)
    parser.add_argument('--xt',help='Font size of xticks',default=9,type=float)
    parser.add_argument('--yt',help='Font size of yticks',default=9,type=float)
    parser.add_argument('--o',help='Output file prefix',default="manplot_out",type=str)
    parser.add_argument('--ft',help='Format type pdf, tif, tiff, jpg, jpeg, eps, pgf, png, ps, raw, rgba, svgz, svg or webp',choices=['pdf','svg','svgz','png','tif','tiff','jpg','jpeg','eps','pgf','ps','raw','rgba','webp'],type=str,default='png')
    parser.add_argument('--dpi', help='Pixel density', type=int, default=300)
    parser.set_defaults(func=run)

def run(args):
    if not os.path.isfile(args.d): fail(f"Dataframe not found: {args.d}") 
    if args.x <= 0 or args.y <= 0: fail("--x/--y (figure width/height) must be > 0")
    if args.s <= 0: fail("--s (scatter size) must be > 0")
    if args.fs <= 0: fail("--fs (font size) must be > 0")
    if args.xt <= 0 or args.yt <= 0 : fail("Font size of x/y ticks must be > 0")
    if args.dpi < 300: fail("--dpi must be >= 300")
    if args.nc <= 0:fail("--nc (number of colors) must be > 0")
    if not (0 <= args.a <= 1):fail("--a (alpha) must be between 0 and 1")
    print("Dataframe preparation ...")
    cols = ["chr", 'pos','value']
    df = pd.read_csv(args.d,header=None,sep=r'\s+')
    if df.shape[1] != 3:fail(f"Input must have exactly 3 columns, got {df.shape[1]}.")
    df.columns = cols
    print(df)
    try:chromosomes = sorted(df['chr'].unique(), key=lambda x: float(x))
    except Exception:chromosomes = sorted(df['chr'].unique())
    chr_to_idx = {c:i for i,c in enumerate(chromosomes, start=1)}
    df['chr_idx'] = df['chr'].map(chr_to_idx)
    chr_max = df.groupby('chr')['pos'].max().reindex(chromosomes)
    total_data = chr_max.sum()
    fraction_of_gaps = 0.20
    num_chr = len(chromosomes)
    if num_chr > 1: 
        num_gaps = num_chr - 1
        gap = total_data * fraction_of_gaps / num_gaps
    else:
        gap = 0
    offset_series = (chr_max + gap).cumsum().shift(fill_value=0)
    offset = offset_series.to_dict()
    df['cum_pos'] = df['pos'] + df['chr'].map(offset)
    print("Plot preparation ...")
    mpl.rcParams['font.family'] = args.f
    mpl.rcParams['font.size']   = args.fs
    mpl.rcParams['xtick.labelsize'] = args.xt
    mpl.rcParams['ytick.labelsize'] = args.yt
    mpl.rcParams['mathtext.fontset'] = 'custom'
    mpl.rcParams['mathtext.rm']      = args.f
    mpl.rcParams['mathtext.it']      = args.f
    mpl.rcParams['mathtext.bf']      = args.f
    palette = sns.color_palette(args.c,args.nc)
    sns.set_theme(style="ticks", rc={"axes.grid": False})
    chr_colors = {c: palette[(i-1) % len(palette)] for c, i in chr_to_idx.items()}
    df['color'] = df['chr'].map(chr_colors)
    fig, ax = plt.subplots(figsize=(args.x,args.y))
    ax.scatter( df['cum_pos'], df['value'],c=df['color'], s=args.s,alpha=args.a)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    if args.sug1 is not None:ax.axhline(y=args.sug1, color=args.sug1c, linestyle='--', linewidth=args.sug1lw)
    if args.sug2 is not None:ax.axhline(y=args.sug2, color=args.sug2c, linestyle='--', linewidth=args.sug2lw)
    ticks = [offset[c] + chr_max[c]/2 for c in chromosomes]
    ax.set_xticks(ticks)
    ax.set_xticklabels(chromosomes, rotation=45)
    ax.set_xlabel(args.xlab,fontfamily=args.f, fontsize=args.fs,fontweight='bold')
    ax.set_ylabel(args.ylab,fontfamily=args.f, fontsize=args.fs,fontweight='bold')
    plt.xticks(fontsize=args.xt,fontfamily=args.f,fontweight='bold')
    plt.yticks(fontsize=args.yt,fontfamily=args.f,fontweight='bold')
    plt.tight_layout()
    if args.mode == 'int':
            plt.show()
    else:
        path = f"{args.o}.{args.ft}"
        plt.savefig(path, format=args.ft, dpi=args.dpi)
        plt.close('all')
        print(f"Plot saved as {path} with dpi={args.dpi}")