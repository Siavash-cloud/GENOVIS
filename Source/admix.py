import sys
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
parser = argparse.ArgumentParser(description="admix")
parser.add_argument('--d',help='Input dataframe (1th column:population lable, 2th column: Individual IDs, 3th column:K1 to Kn)',type=str,required=True)
parser.add_argument('--c',help='Colormap (string) user wants to use (please see https://matplotlib.org/stable/users/explain/colors/colormaps.html, default: hsv)',default="hsv",type=str)
parser.add_argument('--sl',help='Show individual lables',choices=['true','false'],default='false',type=str)
parser.add_argument('--x',help='Width size of figure',default=8.4,type=float)
parser.add_argument('--y',help='Height size of figure',default=4,type=float)
parser.add_argument('--f',help='Font family of figure',default='Calibri',type=str)
parser.add_argument('--fs',help='Font size',default=14,type=float)
parser.add_argument('--lws',help='Size of separator lines',default=0.75,type=float)
parser.add_argument('--xt',help='Font size of individual labels',default=9,type=float)
parser.add_argument('--o',help='Output file prefix',default="admix_plot",type=str)
parser.add_argument('--ft',help='Format type pdf, tif, tiff, jpg, jpeg, eps, pgf, png, ps, raw, rgba, svgz, svg or webp',choices=['pdf','svg','svgz','png','tif','tiff','jpg','jpeg','eps','pgf','ps','raw','rgba','webp'],type=str,default='png')
parser.add_argument('--dpi', help='dpi', type=int, default=300)
args = parser.parse_args()
df = pd.read_csv(args.d,sep='\s+',header=None)
n = df.shape[1] - 2
if n < 2:
    print("Error: The number of provided columns is not enough! Number of columns must be higher than three")
    sys.exit()
Ks = [f'K{i+1}' for i in range(n)]
df.columns = ["Pop","ID"]+ Ks
df["likely_assignment"] = df[Ks].idxmax(axis=1)
df["assignment_prob"]  = df[Ks].max(axis=1)
df_sorted = df.sort_values(by=["Pop", "assignment_prob"],ascending=[True, False]).reset_index(drop=True)
tbl = (df_sorted.melt(id_vars=["Pop","ID","likely_assignment","assignment_prob"],value_vars=Ks,var_name="pop",value_name="prob").reset_index(drop=True))
tbl = tbl.sort_values(by=["Pop","likely_assignment"],ascending=[True, False]).reset_index(drop=True)
print(tbl)
order = tbl["ID"].unique().tolist()
order_df = pd.DataFrame({"ID": order})
df = df.iloc[:, :-2]
df2 = order_df.merge(df, on="ID", how="left")
group_sizes = df2["Pop"].value_counts().loc[df2["Pop"].unique()].cumsum()
boundaries = group_sizes[:-1]
pops = df2["Pop"].unique()
counts = df2["Pop"].value_counts().reindex(pops)
cum = counts.cumsum()
start = cum.shift(fill_value=0)
mid = start + counts/2

print("Plot prepration...")

sns.set_theme(style="whitegrid")
mpl.rcParams['font.family']=args.f
mpl.rcParams['font.size']=args.fs
mpl.rcParams['xtick.labelsize']=args.xt
mpl.rcParams['mathtext.rm']=args.f
mpl.rcParams['mathtext.it']=args.f
mpl.rcParams['mathtext.bf']=args.f
colors = sns.color_palette(args.c, n)
fig, ax = plt.subplots(figsize=(args.x, args.y))
df2[Ks].plot(kind="bar",stacked=True,color=colors,width=1,edgecolor="white",linewidth=0,ax=ax,legend=False,alpha=1)

if args.sl.lower() == 'true':
    ax.set_xticks(range(len(df2)))
    ax.set_xticklabels(df2["ID"], rotation=90, ha='center', fontsize=args.xt)
    ax.tick_params(left=False, labelleft=False)
elif args.sl.lower() == 'false':
    ax.set_xticks([])
    ax.set_xticklabels([])

ax.set_yticks([])
ax.set_yticklabels([])
for b in boundaries:
    ax.axvline(x=b-0.5,color="black",linestyle="--",linewidth=args.lws,zorder=2,clip_on=False)
for pop, m in zip(pops, mid):
    ax.text(x=m - 0.5,y=1.1,s=pop,ha="center",va="top",transform=ax.get_xaxis_transform(),fontsize=args.fs)
ax.grid(False)
sns.despine(ax=ax, top=True, right=True, left=True, bottom=True)
assignment = f"{args.o}_likely_assignment.txt"
tbl1 = tbl.sort_values(by=["Pop","ID"],ascending=[True, False]).reset_index(drop=True)
tbl1.to_csv(assignment, sep='\t', index=False)
#plt.tight_layout()
path = f"{args.o}.{args.ft}"
plt.savefig(f"{args.o}.{args.ft}", dpi=args.dpi)
plt.close('all')
print(f"Plot saved as {path} with dpi={args.dpi}")




