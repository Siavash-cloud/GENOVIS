import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import matplotlib as mpl
import itertools
from mpl_toolkits.axes_grid1 import make_axes_locatable

IS_GUI = os.environ.get("GENOVIS_GUI") == "1"
def fail(msg):
    if IS_GUI:
        raise RuntimeError(msg)
    else:
        print(f"[ERROR] {msg}", file=sys.stderr, flush=True)
        sys.exit(1)

def add_subparser(subparsers):
    parser = subparsers.add_parser("relmap",help="Plot heatmap relationship matrix.")
    parser.add_argument('--rf',help='Format of relationship matrix ("col" or "mat", string)',type=str,choices=['mat', 'col'],default='col')
    parser.add_argument('--relfile',help='Relationship matrix file (matrix or table, string)',type=str,required=True)
    parser.add_argument('--matindex',help='Index of relationship matrix (it is required if you are using --rf mat, matindex: A dataframe including two columns: Population labels and individual IDs)',type=str,default=None)
    parser.add_argument('--mode',help='Output mode: "int" for interactive show, solid format to save as pdf,svg or png',type=str,choices=['int', 'solid'], default='int')
    parser.add_argument('--mask',help='Mask diagonal elements or not',choices=['true', 'false'],default='false',type=str)
    parser.add_argument('--f',help='Font family',default='Calibri',type=str)
    parser.add_argument('--a',help='Annotation of heatmap plot',choices=['true', 'false'],default='false',type=str)
    parser.add_argument('--av',help='Output for averages of relationships among populations',choices=['true','false'],default='false',type=str)
    parser.add_argument('--afs',help='Font size of annotations',default=6,type=float)
    parser.add_argument('--x',help='Width size (float) of figure',default=14,type=float)
    parser.add_argument('--y',help='Height size (float) of figure',default=10,type=float)
    parser.add_argument('--sl', help='Show individual labels ', choices=['true', 'false'], default='false', type=str)
    parser.add_argument('--xyfs',help='Font size of individual labels',default=1,type=float)
    parser.add_argument('--lws',help='Size of separator lines',default=0.45,type=float)
    parser.add_argument('--c',help='Colormap (string) user wants to use (please see https://matplotlib.org/stable/users/explain/colors/colormaps.html, default: YlOrRd)',default="YlOrRd",type=str)
    parser.add_argument('--lc',help='Color of separator lines',default="black",type=str)
    parser.add_argument('--t',help='Title of legend',type=str,default="Relationship")
    parser.add_argument('--pfs',help='Font size of population labels',default=12,type=float)
    parser.add_argument('--ft',help='Format type pdf, tif, tiff, jpg, jpeg, eps, pgf, png, ps, raw, rgba, svgz, svg or webp',choices=['pdf','svg','svgz','png','tif','tiff','jpg','jpeg','eps','pgf','ps','raw','rgba','webp'],type=str,default='jpg')
    parser.add_argument('--o',help='Output file prefix',default="Relmap",type=str)
    parser.add_argument('--dpi', help='dpi', type=int, default=300)
    parser.set_defaults(func=run)

def run(args):
    if not os.path.isfile(args.relfile): fail(f"Dataframe not found: {args.relfile}") 
    if args.x <= 0 or args.y <= 0: fail("--x/--y (figure width/height) must be > 0")
    if args.sl == 'true' and args.xyfs <= 0: fail("--xyfs (Font size of individual labels) must be > 0")
    if args.lws <= 0: fail("--lws (Size of separator lines) must be > 0")
    if args.pfs <= 0: fail("--pfs (Font size of population labels) must be > 0")
    if args.dpi < 300: fail("--dpi must be >= 300")
    print("Dataframe preparation ...")
    if args.rf == 'col':
        cols = ['POP1', 'ID1', 'POP2', 'ID2','Relationship']
        df = pd.read_csv(args.relfile,header=None,sep=r'\s+')
        if df.shape[1]!=5: fail("Dataframe shape is not compatible!")
        df.columns = cols
        try:df['Relationship'] = pd.to_numeric(df['Relationship'], errors='raise')
        except Exception as e:fail(f"'Relationship' must be numeric: {e}")
        pop_by_id = {}
        for _, r in df.iterrows():
            for id_, pop_ in ((r['ID1'], r['POP1']), (r['ID2'], r['POP2'])):
                if id_ in pop_by_id and pop_by_id[id_] != pop_: fail(f"Inconsistent population for ID '{id_}': {pop_by_id[id_]} vs {pop_}")
                pop_by_id[id_] = pop_
        pop_map = {}
        for _, r in df.iterrows():
            pop_map[r['ID1']] = r['POP1']
            pop_map[r['ID2']] = r['POP2']
        labels = sorted(pop_map.keys(), key=lambda x: (pop_map[x], x))
        mat = pd.DataFrame(np.nan, index=labels, columns=labels)
        for _, r in df.iterrows():
            i, j, v = r['ID1'], r['ID2'], r['Relationship']
            mat.at[i, j] = v
            mat.at[j, i] = v
        print('Dataframe reading is done')
        print(mat)
        pops = [pop_map[l] for l in labels]
        if mat.shape[0] != mat.shape[1]: fail("Matrix must be square (rows == columns).")
        heatmap_datframe=mat
    elif args.rf == 'mat':
        if not os.path.isfile(args.matindex): fail(f"Dataframe not found: {args.matindex}")
        index=pd.read_csv(args.matindex,sep=r'\s+',header=None)
        mat = pd.read_csv(args.relfile,sep=r'\s+',header=None)
        if len(mat)!=len(index): fail("dataframe format is not compatible!: number of index is not matched with your dataframe!")
        if mat.shape[1]!=len(index): fail("dataframe format is not compatible!: number of index is not matched with your dataframe!")
        if mat.shape[1] < 2 or len(index) < 2 : fail("Number of individuals must be higher than one!")
        if pd.to_numeric(mat.stack(), errors='coerce').isna().any(): fail("Matrix contains non-numeric values!")
        labels_series = index.iloc[:, 1]
        if labels_series.duplicated().any():fail("matindex: duplicate IDs found in the 2nd column.")
        if mat.shape[0] != mat.shape[1]: fail("Matrix must be square (rows == columns).")
        labels = labels_series.astype(str).tolist()
        mat.index = labels
        mat.columns = labels
        pops_series = index.iloc[:, 0].astype(str)
        pop_map = dict(zip(labels, pops_series))
        pops = [pop_map[l] for l in labels]
        print(mat)
        heatmap_datframe=mat
    else: fail(f"Unsupported format for relationship matrix: {args.rf}")
    if args.av == 'true':
            if args.rf == 'col':
                df_pairs = df.copy()
            elif args.rf == 'mat':
                df_pairs = mat.stack().reset_index()
                df_pairs.columns = ['ID1','ID2','Relationship']
                df_pairs = df_pairs[df_pairs['ID1'] <= df_pairs['ID2']]
                df_pairs['POP1'] = df_pairs['ID1'].map(pop_map)
                df_pairs['POP2'] = df_pairs['ID2'].map(pop_map)
            pops_pairs = sorted(set(df_pairs['POP1']) | set(df_pairs['POP2']))
            results = []
            for popA, popB in itertools.combinations_with_replacement(pops_pairs, 2):
                mask = (((df_pairs['POP1'] == popA) & (df_pairs['POP2'] == popB))|((df_pairs['POP1'] == popB) & (df_pairs['POP2'] == popA)))
                mean_rel = df_pairs.loc[mask, 'Relationship'].mean()
                results.append({'POP1': popA,'ID1':  popA,'POP2': popB,'ID2':  popB,'Relationship': mean_rel})
            df_pop_avg = pd.DataFrame(results)
            outfile = f"{args.o}_pop_avg.col"
            df_pop_avg.to_csv(outfile, sep='\t', index=False, header=False)
            print(f"Averages saved to {outfile}")
    n=len(heatmap_datframe)
    mpl.rcParams['font.family']=args.f
    if args.mask == 'true':
        mask_arr = np.eye(n, dtype=bool)
    else:
        mask_arr = None    
    annot_flag = True if args.a == 'true' else False
    if args.a == 'true' and args.afs <= 0: fail("--afs (Font size of annotations) must be > 0")
    fig, ax = plt.subplots(figsize=(args.x, args.y))
    image=sns.heatmap(heatmap_datframe,mask=mask_arr,cmap=args.c,annot=annot_flag,fmt=".2f",annot_kws={"size": args.afs},cbar=False,linewidths=0,square=True,ax=ax)    
    if args.sl == 'true':
        ax.set_xticks(np.arange(n) + 0.5)  
        ax.set_xticklabels(labels, rotation=90, ha='right', size=args.xyfs)
        ax.set_yticks(np.arange(n) + 0.5)     
        ax.set_yticklabels(labels, rotation=0, size=args.xyfs)
        ax.tick_params(axis='x', which='both', length=0)
        ax.tick_params(axis='y', which='both', length=0)
    if args.sl == 'false':
        ax.set_xticks([])
        ax.set_yticks([])
    boundaries = [i for i in range(1, n) if pops[i] != pops[i-1]]
    for b in boundaries:
        ax.axhline(b, color=args.lc, linestyle='--', linewidth=args.lws, clip_on=False)
        ax.axvline(b, color=args.lc, linestyle='--', linewidth=args.lws, clip_on=False)
    fig.canvas.draw()
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="2%", pad=0.05)
    cbar = fig.colorbar(image.collections[0] if hasattr(image, "collections") else image, cax=cax)
    cbar.set_label(args.t, size=args.pfs)
    cbar.ax.tick_params(labelsize=args.pfs)
    renderer = fig.canvas.get_renderer()
    xt_heights = [lbl.get_window_extent(renderer).height for lbl in ax.get_xticklabels()]
    max_xt_ht = max(xt_heights) if xt_heights else 0
    yt_widths = [lbl.get_window_extent(renderer).width for lbl in ax.get_yticklabels()]
    max_yt_wd = max(yt_widths) if yt_widths else 0
    margin_xt = max_xt_ht + args.xyfs + args.pfs
    margin_yt = max_yt_wd + args.xyfs + args.pfs
    group_pos = {}
    for idx, lab in enumerate(labels):
        group_pos.setdefault(pop_map[lab], []).append(idx)
    for pop, idxs in group_pos.items():
        start, end = min(idxs), max(idxs)
        center = (start + end + 1) / 2
        ax.annotate(pop,xy=(center, n),xycoords='data',xytext=(0,-2*margin_xt),textcoords='offset points',
                    ha='center', va='bottom',fontsize=args.pfs,rotation=45,clip_on=False)
        ax.annotate(pop,xy=(0, center),xycoords='data',xytext=(-1*margin_yt,0),textcoords='offset points',
                    ha='right', va='center',rotation=0,fontsize=args.pfs,clip_on=False)
    plt.subplots_adjust(top=1 - margin_xt/fig.bbox.height - 0.02,left=margin_yt/fig.bbox.width + 0.12)
    if args.mode == 'int':
            plt.show()
    else:
        path = f"{args.o}.{args.ft}"
        plt.savefig(path, format=args.ft, dpi=args.dpi)
        plt.close('all')
        print(f"Plot saved as {path} with dpi={args.dpi}")

