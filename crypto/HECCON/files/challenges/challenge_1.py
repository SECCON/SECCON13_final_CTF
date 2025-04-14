from pathlib import Path

import numpy as np
import pyhelayers


N = 2**13


class Challenge:
    @classmethod
    def generate(cls, pubkey: Path, dist_dir: Path):
        """Generate the challenge data.

        dist_dir is a distributed directory to contestants.

        Args:
            pubkey (Path): Path to the public key file.
            dist_dir (Path): Path to the directory where the challenge data is saved.
        """
        he_context = pyhelayers.SealCkksContext()
        he_context.load_from_file(str(pubkey))
        encoder = pyhelayers.Encoder(he_context)
        x = np.random.uniform(-3, 3, N)
        cx = encoder.encode_encrypt(x)
        cx.save_to_file(str(dist_dir / "enc"))
        (dist_dir / "challenge.py").write_text(Path(__file__).read_text())

    @classmethod
    def evaluate(
        cls, pubkey: Path, privkey: Path, enc: Path, submission: Path
    ) -> float:
        """Evaluate the submission.

        submission is a path to a submitted file and the server evaluate it.
        Contestants are supposed to get better MAE as much as possible.

        Args:
            pubkey (Path): Path to the public key file.
            privkey (Path): Path to the private key file.
            enc (Path): Path to the encrypted data file.
            submission (Path): Path to the submitted file.
        """
        he_context = pyhelayers.SealCkksContext()
        he_context.load_from_file(str(pubkey))
        he_context.load_secret_key_from_file(str(privkey))
        encoder = pyhelayers.Encoder(he_context)

        cx = encoder.encode_encrypt([])
        cx.load_from_file(str(enc))
        x = encoder.decrypt_decode_double(cx)
        cy_sub = encoder.encode_encrypt([])
        cy_sub.load_from_file(str(submission))
        y_sub = encoder.decrypt_decode_double(cy_sub)

        y_true = np.maximum(x, 0.0)
        mae = np.mean(np.abs(y_true - y_sub))  # less is better
        return float(mae)
