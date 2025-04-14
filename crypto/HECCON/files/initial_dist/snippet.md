# Snippet

You can use the following codes as a snippet.

```python
from pathlib import Path
import numpy as np
import pyhelayers

pubkey_path = "/path/to/pubkey"
privkey_path = "/path/to/privkey"
```

Generation of your own pubkey-privkey pair for test.
I recommend to generate it because you can debug your code easily.

```python
req = pyhelayers.HeConfigRequirement(
    num_slots=N,
    integer_part_precision=10,
    fractional_part_precision=30,
    multiplication_depth=10,
    security_level=128,
)
he_context = pyhelayers.SealCkksContext()
he_context.init(req)
he_context.save_to_file(pubkey_path)
he_context.save_secret_key_to_file(privkey_path)
```

Loading of key

```python
he_context = pyhelayers.SealCkksContext()
he_context.load_from_file(pubkey_path)
# If you have privkey
# he_context.load_secret_key_from_file(privkey)
```

Creation of encoder

```python
encoder = pyhelayers.Encoder(he_context)
```

Encryption

```python
x = np.linspace(-1, 1, 2**13)
cx = encoder.encode_encrypt(x)
# You can also encrypt empty array
cy = encoder.encode_encrypt([])
```

Decryption

```python
x = encoder.decrypt_decode_double(cx)
```

Loading of encryption data from file

```python
cx = encoder.encode_encrypt([])
cx.load_from_file("/path/to/enc")
```

Save of encryption data to file
This type of files can be submitted and the server evaluate the score.

```python
cx.save_to_file("/path/to/submission")
```

Addition
Note that the operation is in-place.

```python
# vector
cx.add(cy)
# scalar
cx.add_scalar(1.0)
```

Subtraction

```python
# vector
cx.sub(cy)
```

Multiplication
Note that you can't multiply vectors so much. See `multiplication_depth` in HeConfigRequirement.

```python
# vector
cx.multiply(cy)
# scalar
cx.multiply_scalar(2.0)
```

Check current chain index

```python
cx.get_chain_index()
```

Some useful operations
Ref: https://ibm.github.io/helayers/reference/gen_pages/FunctionEvaluator.html

```python
fe = pyhelayers.FunctionEvaluator(he_context)
```
