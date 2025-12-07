GENOVIS
Developers: Siavash Salek Ardestani & Elmira Mohandesan
Contact: siasia6650@gmail.com
Released in 2025, GENOVIS is a visualization toolkit for population genomic analyses.
It supports the generation of: Manhattan plots, three-dimensional PCA, SNP density maps,
admixture plots, runs of homozygosity (ROH) intervals, and relationship matrices.


MIT License for GENOVIS

Copyright (c) 2025 Siavash Salek Ardestani, Elmira Mohandesan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

- ***v1.0.4 (2025-12-07)*** – Fixed a bug in the `genovis-gui` :
  - in line 2773 self.pushButton_3dpca_RUN.setText(_translate("GENOVIS_GUI", "Run 3dpca"))
	**cganged to**
	self.pushButton_3dpca_RUN.setText(_translate("GENOVIS_GUI", "Run pca3d"))

- ***v1.0.3 (2025-12-02)*** – Fixed a bug in the `rohpainter` module:
  - For defining font size of legend title:
	ax.legend(handles,pops,title='Population',loc='upper left',bbox_to_anchor=(1.02, 1.0),borderaxespad=0.)
	**changed to**
	ax.legend(handles,pops,title='Population',loc='upper left',title_fontsize=args.fs+1,bbox_to_anchor=(1.02, 1.0),borderaxespad=0.)


- ***v1.0.2 (2025-12-01)*** – Fixed a bug in the `rohpainter` module:
  - For defining font sizes:
	mpl.rcParams['axes.titlesize']= args.fs
    mpl.rcParams['axes.labelsize']= args.fs
    mpl.rcParams['legend.fontsize']= args.fs
	**were added to**
	rohpainter.py


- ***v1.0.1 (2025-11-21)*** – Fixed a bug in the `mapden` module:
  - Force chromosome IDs to be read as strings to avoid issues with mixed/leading-zero chromosome labels:
	df=pd.read_csv(args.m,names=cols,sep=r'\s+') **changed to** df=pd.read_csv(args.m,names=cols,sep=r'\s+',dtype={'Chr': str})
	genome_index=pd.read_csv(args.i,sep=r'\s+',header=None,names=['Chr','Size']) **changed to** genome_index=pd.read_csv(args.i,sep=r'\s+',header=None,names=['Chr','Size'],dtype={'Chr': str})
  - Sort chromosome IDs based on the order of chromosome IDs in index file:
	chromosomes = set(df["Chr"].unique()) 
	**changed to**
	chrs_in_map = set(df["Chr"].unique())
    chromosomes = [c for c in genome_index["Chr"] if c in chrs_in_map]