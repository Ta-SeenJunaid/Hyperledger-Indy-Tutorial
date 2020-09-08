import sys
import argparse

from plenum.common.signer_did import DidSigner


def read_args():
    parser = argparse.ArgumentParser(
        description="Generate Did and verification key using seed"
    )
    parser.add_argument('--seed', required=True,
                        help= 'Provide 32 character'
                        'long seed value', type=str)

    return parser.parse_args()


if __name__ == '__main__':
    args = read_args()

    if len(args.seed) != 32 :
        raise argparse.ArgumentTypeError('The length of the seed should be 32 digit long')
    
    seedValue = args.seed.encode()
    signer = DidSigner(seed=seedValue)
    did = signer.identifier
    verkey = signer.verkey

    print("Did: ")
    print(did)

    print("Verification key: ")
    print(verkey)



