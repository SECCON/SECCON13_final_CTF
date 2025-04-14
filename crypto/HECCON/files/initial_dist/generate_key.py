import pyhelayers

pubkey_path = "/path/to/pubkey"
privkey_path = "/path/to/privkey"

req = pyhelayers.HeConfigRequirement(
    num_slots=2**13,
    integer_part_precision=10,
    fractional_part_precision=30,
    multiplication_depth=10,
    security_level=128,
)
he_context = pyhelayers.SealCkksContext()
he_context.init(req)
he_context.save_to_file(pubkey_path)
he_context.save_secret_key_to_file(privkey_path)
