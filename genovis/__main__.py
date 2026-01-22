import argparse
import sys
from . import pca3d,mapden,admix,relmap,rohpainter,manplot

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="genovis",
        description="GENOVIS: A Python package for the visualization of population genetic analyses"
    )
    subparsers = parser.add_subparsers(title="subcommands", dest="command", metavar="<tool>",required=True)
    mapden.add_subparser(subparsers)
    pca3d.add_subparser(subparsers)
    admix.add_subparser(subparsers)
    relmap.add_subparser(subparsers)
    rohpainter.add_subparser(subparsers)
    manplot.add_subparser(subparsers)
    return parser

def main(argv=None):
    print("-----------------------------------------------------------------")
    print("-----------------------------------------------------------------")
    print("|                                                               |")
    print("|     ██████╗ ███████╗███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗   |")
    print("|    ██╔════╝ ██╔════╝████╗  ██║██╔═══██╗██║   ██║██║██╔════╝   |")
    print("|    ██║  ███╗█████╗  ██╔██╗ ██║██║   ██║██║   ██║██║███████╗   |")
    print("|    ██║   ██║██╔══╝  ██║╚██╗██║██║   ██║╚██╗ ██╔╝██║╚════██║   |")
    print("|    ╚██████╔╝███████╗██║ ╚████║╚██████╔╝ ╚████╔╝ ██║███████║   |")
    print("|     ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝╚══════╝   |")
    print("|                                                               |")
    print("-----------------------------------------------------------------")
    print("-----------------------------------------------------------------")
    print("|                   GENOVIS Version 1.0.5                       |")
    print("|  Developers: Siavash Salek Ardestani & Elmira Mohandesan      |")
    print("|  Contact: siasia6650@gmail.com                                |")
    print("|  Released in 2025, GENOVIS is a visualization toolkit         |")
    print("|  for population genomic analyses. It supports the             |")
    print("|  generation of: Manhattan plots, three dimensional PCA,       |")
    print("|  SNP density maps, admixture plots, runs of homozygosity      |")
    print("|  (ROH) intervals, and relationship matrices.                  |")
    print("|                                                               |")
    print("|  GENOVIS is an independent academic open-source software      |")
    print("|  and is not affiliated with any commercial entity or          |")
    print("|  similarly named tools.                                       |")
    print("-----------------------------------------------------------------")
    print("-----------------------------------------------------------------")

    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr, flush=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
