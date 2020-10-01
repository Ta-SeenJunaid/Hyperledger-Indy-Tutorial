sudo python3 init_indy_node.py \
--name Node1 --seed 4000F000u00000D0000000g0000Node1

sudo python3 init_indy_node.py \
--name Node2 --seed T00000000u0000I0000v0003000Node2

sudo python3 init_indy_node.py \
--name Node2 --seed 300000A00u000z0000600003000Node3


sudo python3 create_domain_ledger_genesis_file.py \
--stewardDids \
"RnXJMDxifkBaceAkPizz8F, AmJHyEZ9ofrPz1DUfx97Qo, PeVR5pdFizbK8WN9THd3mq" \
--stewardVerkeys \
"~9F4P9aQysR1YATnARMuhxt, ~CVv3mmR7QPanynNMJmTG9f, ~VPwSf359RqMB6TP5X728WJ" \
--trusteeDids \
"L4vaBJDbZiaX68mVHLuZ2E" \
--trusteeVerkeys \
"~QKV8UWR7LHB7APvrWc88xK" \
--network sandbox