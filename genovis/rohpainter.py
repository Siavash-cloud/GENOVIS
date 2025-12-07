import os, sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import argparse

IS_GUI = os.environ.get("GENOVIS_GUI") == "1"
def fail(msg):
    if IS_GUI:
        raise RuntimeError(msg)
    else:
        print(f"[ERROR] {msg}", file=sys.stderr, flush=True)
        sys.exit(1)

def add_subparser(subparsers):
    parser = subparsers.add_parser("rohpainter",help="Plot runs of homozygous regions barplot.")
    parser.add_argument('--d',help='Dataframe(1st column:population label, 2nd: Individual ID, 3rd: chromosome, 4th: start position, 5th: end position)',type=str,required=True)
    parser.add_argument('--i',help='Genome index(1st column:chromosome, 2nd: size)',type=str,required=True)
    parser.add_argument('--mode',help='Output mode: "int" for interactive show, solid format to save as pdf,svg or png',type=str,choices=['int', 'solid'], default='int')
    parser.add_argument('--x',help='Horizontal size of figure',default=10,type=float)
    parser.add_argument('--y',help='Vertical size of figure',default=4,type=float)
    parser.add_argument('--yt',help='Font size of yticks',default=9,type=float)
    parser.add_argument('--xt',help='Font size of xticks',default=9,type=float)
    parser.add_argument('--t',help='Threshold for identifying common intervals(e.g., 0.8). Please use “--t false”, if you do not want to pinpoint common intervals.',default="false",type=str)
    parser.add_argument('--tc',help='Threshold line color',default="red",type=str)
    parser.add_argument('--tw',help='Threshold line width',default=0.75,type=float)
    parser.add_argument('--sl', help='Show labels in y axis', choices=['true', 'false'], default='true', type=str)
    parser.add_argument('--c',help='Choosing colormap (please see https://matplotlib.org/stable/users/explain/colors/colormaps.html)', default="Paired",type=str)
    parser.add_argument('--Chr',help='Chromosomal prefix (chr, chromosome, contig, etc.)',type=str,default="Chromosome")
    parser.add_argument('--f',help='Font family',default='Calibri',type=str)
    parser.add_argument('--fs',help='Font size',default=12,type=float)
    parser.add_argument('--o',help='Output file prefix',default="out",type=str)
    parser.add_argument('--ft',help='Format type pdf, tif, tiff, jpg, jpeg, eps, pgf, png, ps, raw, rgba, svgz, svg or webp',choices=['pdf','svg','svgz','png','tif','tiff','jpg','jpeg','eps','pgf','ps','raw','rgba','webp'],type=str,default='jpg')
    parser.add_argument('--dpi',help='dpi',type=int,default=300)
    parser.set_defaults(func=run)

def run(args):
    t_raw = str(args.t).strip().lower()
    if t_raw == "false":
        use_threshold = False
        thresh_frac = None
    else:
        try:
            thresh_frac = float(t_raw)
        except ValueError:
            fail("--t must be 'false' or a number between 0 and 1 (e.g., 0.8).")
        if not (0.0 < thresh_frac <= 1.0):
            fail("--t must be between 0 and 1 (e.g., 0.8).")
        use_threshold = True
    if not os.path.isfile(args.d): fail(f"Dataframe not found: {args.d}") 
    if not os.path.isfile(args.i): fail(f"Genome index not found: {args.i}") 
    if args.x <= 0 or args.y <= 0: fail("--x/--y (figure width/height) must be > 0") 
    if args.xt <= 0 or args.yt <= 0 : fail("Font size of x/y ticks must be > 0") 
    if args.tw <= 0: fail("--tw (Threshold line width) must be > 0")
    if args.fs <= 0: fail("--fs (font size) must be > 0")
    if args.dpi < 300: fail("--dpi must be >= 300")
    print("===== Dataframe preparation ... =====")
    df = pd.read_csv(args.d,sep=r'\s+',header=None,names=['pop', 'ind', 'chr', 'start', 'end'],dtype={'pop': str, 'ind': str, 'chr': str, 'start': int, 'end': int})
    print("Dataframe:")
    print(df)
    index = pd.read_csv(args.i,sep=r'\s+',header=None,names=['chr', 'chr_size'],dtype={'chr': str, 'chr_size': int})
    print("Genome index:")
    print(index)
    df2 = pd.merge(df,index,on='chr')
    if df2.empty:fail("After merging input dataframe with genome index, no chromosomes matched. ""Check that chromosome names in --d and --i use the same naming convention.")
    individuals = df2['ind'].unique()
    n_inds = len(individuals)
    y_positions = {ind: i for i, ind in enumerate(individuals)}
    pops = df2['pop'].unique()
    n = pops.shape[0]
    color = sns.color_palette(args.c, n)
    colors = dict(zip(pops, color))
    sns.set_theme(style="ticks", rc={"axes.grid": False})
    shared_list = []
    mpl.rcParams['font.family'] = args.f
    mpl.rcParams['font.size'] = args.fs
    mpl.rcParams['axes.titlesize']   = args.fs
    mpl.rcParams['axes.labelsize']   = args.fs
    mpl.rcParams['legend.fontsize']  = args.fs
    mpl.rcParams['ytick.labelsize'] = args.yt
    mpl.rcParams['xtick.labelsize'] = args.xt
    mpl.rcParams['font.weight']       = 'bold'
    for chrom, sub in df2.groupby('chr'):
        size_bp = sub['chr_size'].iloc[0]
        if use_threshold:
            threshold = thresh_frac*n_inds
            breakpoints = sorted(set(sub['start'].tolist() + sub['end'].tolist()))
            shared_intervals = []
            for i in range(len(breakpoints) - 1):
                seg_start = breakpoints[i]
                seg_end = breakpoints[i + 1]
                count_cover = sub[(sub['start']<= seg_start)&(sub['end'] >= seg_end)]['ind'].nunique()
                if count_cover >= threshold:
                    if not shared_intervals or seg_start > shared_intervals[-1][1]:
                        shared_intervals.append([seg_start, seg_end])
                    else:
                        shared_intervals[-1][1] = seg_end
        else:
            shared_intervals = []

        for (s_bp, e_bp) in shared_intervals:shared_list.append({'chr': chrom,'start': s_bp,'end': e_bp})
        fig, ax = plt.subplots(figsize=(args.x, args.y))
        ax.set_title(f'{args.Chr} {chrom}')
        ax.set_xlim(0, size_bp / 1e6)
        if args.sl == 'true':
            ax.set_yticks(list(y_positions.values()))
            ax.set_yticklabels(list(y_positions.keys()), fontsize=args.yt)
        if args.sl == 'false':
            ax.set_yticks([])
        ax.set_ylim(-1, len(individuals))
        ax.set_xlabel('Position (Mbp)')
        ax.set_ylabel('Individual')
        for _, row in sub.iterrows():
            y = y_positions[row['ind']] - 0.3
            start_mbp = row['start'] / 1e6
            width_mbp = (row['end'] - row['start']) / 1e6
            ax.broken_barh([(start_mbp, width_mbp)], (y, 0.6), facecolors=colors[row['pop']])
        if use_threshold:
            for (s_bp, e_bp) in shared_intervals:
                s_mbp = s_bp / 1e6
                e_mbp = e_bp / 1e6
                ax.axvline(x=s_mbp,color=args.tc,linestyle='--',linewidth=args.tw)
                ax.axvline(x=e_mbp,color=args.tc,linestyle='--',linewidth=args.tw)

        handles = [plt.Line2D([0], [0], color=colors[p], lw=6) for p in pops]
        ax.legend(handles,pops,title='Population',loc='upper left',title_fontsize=args.fs+1,bbox_to_anchor=(1.02, 1.0),borderaxespad=0.)
        fig.subplots_adjust(right=0.75)
        plt.tight_layout()
        if args.mode == 'int':
            plt.show()
        else:
            out_fname=f"{args.o}.chr{chrom}.{args.ft}"
            fig.savefig(out_fname, dpi=args.dpi)
            plt.close(fig)
            print(f"Plot saved as {out_fname} with dpi={args.dpi}")

    if use_threshold:
        if shared_list:
            shared_df = pd.DataFrame(shared_list)
            intervals = f"{args.o}_shared_intervals.txt"
            shared_df.to_csv(intervals, sep='\t', index=False)
            print(f"Shared intervals saved to {intervals}")
        else:
            print(f"No common intervals found based on provided threshold {args.t}")