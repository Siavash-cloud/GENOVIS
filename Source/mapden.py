import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import matplotlib as mpl
import argparse
parser=argparse.ArgumentParser(description="mapden")
parser.add_argument('--m',help='PLINK map file (1st column: Chromosome, 2nd column: SNPID, 3rd column: Genetic distance (morgans), 4th column: Base-pair position)',type=str,default=None,required=True)
parser.add_argument('--i',help='Genome index file (1st column:chromosome, 2nd column: size)',type=str,default=None,required=True)
parser.add_argument('--Chr',help='Chromosomal prefix(chr,chromosome, contig or ...)',type=str,default="Chr")
parser.add_argument('--Chrfs',help='Font size of chromosomes',type=float,default=10)
parser.add_argument('--f',help='Font family (default=Calibri)',default='Calibri',type=str)
parser.add_argument('--fs',help='Font size',default=12,type=float)
parser.add_argument('--x',help='Horizontal size of figure (default=8)',default=8,type=float)
parser.add_argument('--y',help='Vertical size of figure (default=5)',default=5,type=float)
parser.add_argument('--c',help='Choosing colormaps (default=plasma)',default="plasma",type=str)
parser.add_argument('--b',help='Bin size (Mbp, default=1)',default=1,type=float)
parser.add_argument('--ft',help='Format type pdf, tif, tiff, jpg, jpeg, eps, pgf, png, ps, raw, rgba, svgz, svg or webp',choices=['pdf','svg','svgz','png','tif','tiff','jpg','jpeg','eps','pgf','ps','raw','rgba','webp'],type=str,default='png')
parser.add_argument('--pad',help='Distance between legend and main figure',default=0.05,type=float)
parser.add_argument('--dpi', help='dpi', type=int, default=300)
parser.add_argument('--o',help='Output file prefix',default="mapden",type=str)
args=parser.parse_args()

print("Genome Map:")
cols=['Chr','SNPID','Position(cM)','Position(bp)']
df=pd.read_csv(args.m,names=cols,sep='\s+')
if df.empty: raise ValueError("Input map file is empty!")
print(df)
genome_index=pd.read_csv(args.i,sep='\s+',header=None,names=['Chr','Size'])
if genome_index.empty: raise ValueError("Input genome index file is empty!")
missing_chrs = set(df['Chr'].unique()) - set(genome_index['Chr'].unique())
if missing_chrs:raise ValueError(f"Chromosomes {missing_chrs} found in map but not in genome index!")
max_genome_size=genome_index['Size'].max()
print("Genome index:")
print(genome_index)
if df.shape[1]!=4:raise ValueError("Dataframe shape is not compatible!")
if genome_index.shape[1]!=2:raise ValueError("Dataframe shape is not compatible!")

mpl.rcParams['font.family']=args.f
chromosomes=df["Chr"].unique()
bin_size=args.b
bins_dict={}
heatmap_data_dict={}
n_bins_dict={}
max_bins=0
if len(chromosomes) == 0:raise ValueError("No chromosomes found in input!")


for chrom in chromosomes:
    chrom_df=df[df["Chr"]==chrom]
    max_bp=chrom_df['Position(bp)'].max()
    bins=np.arange(0,max_bp+bin_size*1e6,bin_size*1e6)
    counts,_=np.histogram(chrom_df['Position(bp)'],bins=bins)
    bins_dict[chrom]=bins
    heatmap_data_dict[chrom]=counts
    n_bins=len(bins)-1
    n_bins_dict[chrom]=n_bins
    if n_bins > max_bins: max_bins=n_bins
    if max_bins == 0:raise ValueError("No bins found (max_bins == 0)!")

global_min=min([np.min(counts) for counts in heatmap_data_dict.values()])
global_max=max([np.max(counts) for counts in heatmap_data_dict.values()])
fig=plt.figure(figsize=(args.x,args.y))
left=0.05
right=0.94
max_width_ratio=right-left
n_chrom=len(chromosomes)
gap=0.01
ax_height=(1-(n_chrom+1)*gap)/n_chrom
bottoms=[]
current_bottom=1-gap-ax_height
for i in range(n_chrom):
    bottoms.append(current_bottom)
    current_bottom -=(ax_height+gap)

first_chrom=chromosomes[0]
first_n_bins=n_bins_dict[first_chrom]
first_width_ratio=max_width_ratio*(first_n_bins/max_bins)
first_max_bp=genome_index.loc[genome_index['Chr']==first_chrom,'Size'].values[0]
first_bin_max=first_max_bp/1e6
first_ax_bottom=bottoms[0]
first_ax_height=ax_height
scalebar_height=ax_height/3.5
if scalebar_height < 0.01:print("Warning: scalebar height is very small, output may be hard to read.")
scalebar_bottom=first_ax_bottom+first_ax_height+0.01
ax_scalebar=fig.add_axes([left,scalebar_bottom,first_width_ratio,scalebar_height])
ax_scalebar.set_xlim(0,first_bin_max)
ax_scalebar.set_ylim(0,1)
ax_scalebar.spines['bottom'].set_visible(False)
ax_scalebar.spines['right'].set_visible(False)
ax_scalebar.spines['left'].set_visible(False)
ax_scalebar.spines['top'].set_position(('data',1.0))
ax_scalebar.xaxis.set_ticks_position('top')
ax_scalebar.xaxis.set_label_position('top')
ax_scalebar.yaxis.set_visible(False)
ticks=np.linspace(0,first_bin_max,5)
ax_scalebar.set_xticks(ticks)
ax_scalebar.set_xticklabels([str(int(round(x))) for x in ticks],fontname=args.f,fontsize=args.fs)
ax_scalebar.tick_params(axis='x',which='both',direction='out',length=8,width=1.5,top=True,bottom=False)
ax_scalebar.set_xlabel("Genome size (Mbp)",fontsize=args.fs,fontname=args.f,fontweight='bold',labelpad=10)
axes_list=[]
label_positions=[]

for ax_bottom,chrom in zip(bottoms,chromosomes):
    n_bins=n_bins_dict[chrom]
    width_ratio=max_width_ratio*(n_bins/max_bins)
    bins=bins_dict[chrom]
    counts=heatmap_data_dict[chrom]
    bin_labels=[f"{int(b)}-{int(b+bin_size*1e6)}" for b in bins[:-1]]
    heatmap_data=pd.DataFrame([counts],columns=bin_labels)
    ax=fig.add_axes([left,ax_bottom,width_ratio,ax_height])
    axes_list.append(ax)
    sns.heatmap(heatmap_data,cmap=args.c,cbar=False,vmin=global_min,vmax=global_max,ax=ax,xticklabels=False,yticklabels=False)
    ax.set_xlabel("")
    ax.set_ylabel("")
    bbox=ax.get_position()
    label_x=bbox.x1+0.005
    label_y=0.5*(bbox.y0+bbox.y1)
    fig.text(label_x,label_y,f"{args.Chr} {chrom}",va='center',ha='left',fontname=args.f,fontsize=args.Chrfs,clip_on=False,zorder=10)
    label_positions.append(label_x)

norm=Normalize(vmin=global_min,vmax=global_max)
sm=ScalarMappable(norm=norm,cmap=args.c)
sm.set_array([])
legend_x=max(label_positions)+args.pad
cb_ax=fig.add_axes([legend_x,0.1,0.02,0.8])
cbar=fig.colorbar(sm,cax=cb_ax,orientation='vertical')
cbar.set_label(f'Number of SNPs in each {bin_size} Mb',fontweight='bold',fontname=args.f,fontsize=args.fs,labelpad=15,rotation=90)
cbar.ax.tick_params(labelsize=args.fs)

path = f"{args.o}.{args.ft}"
plt.savefig(path, format=args.ft, dpi=args.dpi,bbox_inches='tight', pad_inches=0.1)
plt.close('all')
print(f"Plot saved as {path} with dpi={args.dpi}")
