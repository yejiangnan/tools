import argparse
from .xcorr_csv import make_csv
from .gen_lab import gen_lab

def main():
    parser = argparse.ArgumentParser(description="xcorr args")  
    parser.add_argument("type", help="file type")
    parser.add_argument("audio", help="audio dir")
    parser.add_argument("lab", help="lab dir")
    args = parser.parse_args()
    
    make_csv(args.type, args.audio, args.lab)
    gen_lab(args.type, args.lab)

if __name__ == "__main__":
    main()
