import argparse
from .split_idx import doc_vad

def main():
    parser = argparse.ArgumentParser(description="vad args")
    parser.add_argument("audio", help="audio dir")
    parser.add_argument("lab", help="lab dir")
    args = parser.parse_args()

    doc_vad(args.audio, args.lab)

if __name__ == "__main__":
    main()

