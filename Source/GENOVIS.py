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
print("|                    GENOVIS Version 1.0                        |")
print("|  Developers: Siavash Salek Ardestani & Elmira Mohandesan      |")
print("|  Contact: siasia6650@gmail.com                                |")
print("|  Released in 2025, GENOVIS is a visualization toolkit         |")
print("|  for population genomic analyses. It supports the             |")
print("|  generation of: Manhattan plots, three dimensional PCA,       |")
print("|  SNP density maps, admixture plots, runs of homozygosity      |")
print("|  (ROH) intervals, and relationship matrices.                  |")
print("-----------------------------------------------------------------")
print("-----------------------------------------------------------------")
import argparse
import subprocess
import sys
import os
VERSION = "1.0"
def main():
    parser = argparse.ArgumentParser(prog='GENOVIS')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    subparsers = parser.add_subparsers(dest='command', required=True)
    subparsers.add_parser('3dpca', help='3D PCA plot (3dpca.py)')
    subparsers.add_parser('manplot', help='Manhattan plot (manplot.py)')
    subparsers.add_parser('mapden', help='SNP Density heatmap (mapden.py)')
    subparsers.add_parser('relmap', help='Genomic relationship heatmap plot (relmap.py)')
    subparsers.add_parser('admix', help='Admixture plot (admix.py)')
    subparsers.add_parser('rohpainter', help='ROH plot (rohpainter.py)')
    help_parser = subparsers.add_parser('help', help='Show help for a specific module "{3dpca,manplot,mapden,relmap,admix,rohpainter}"')
    help_parser.add_argument('module', nargs='?', help='Module name (e.g., relmap)')
    args, rest = parser.parse_known_args()
    script_map = {'3dpca':'3dpca.py','manplot':'manplot.py','mapden':'mapden.py','relmap':'relmap.py','admix':'admix.py','rohpainter':'rohpainter.py'}
    if args.command == 'help':
        if not args.module:
            parser.print_help()
            sys.exit(0)
        module = args.module
        if module not in script_map:
            print(f"Unknown module: {module}", file=sys.stderr)
            print(f"Available modules: {', '.join(script_map.keys())}", file=sys.stderr)
            sys.exit(1)
        script_path = os.path.join(os.path.dirname(__file__), script_map[module])
        if not os.path.exists(script_path):
            print(f"Error: {script_map[module]} not found in {os.path.dirname(__file__)}", file=sys.stderr)
            sys.exit(1)
        sys.exit(subprocess.run([sys.executable, script_path,'--help']).returncode)
    if args.command not in script_map:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        print(f"Available commands: {', '.join(script_map.keys())} or 'help <module>'", file=sys.stderr)
        sys.exit(1)
    script_name = script_map[args.command]
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    if not os.path.exists(script_path):
        print(f"Error: {script_name} not found in {os.path.dirname(__file__)}", file=sys.stderr)
        sys.exit(1)
    cmd = [sys.executable, script_path] + rest
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()