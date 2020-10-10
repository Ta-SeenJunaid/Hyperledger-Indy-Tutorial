sudo python3 init_indy_node.py \
--name Node1 --seed 4000F000u00000D0000000g0000Node1

sudo python3 init_indy_node.py \
--name Node2 --seed T00000000u0000I0000v0003000Node2

sudo python3 init_indy_node.py \
--name Node3 --seed 300000A00u000z0000600003000Node3


sudo python3 create_domain_ledger_genesis_file.py \
--stewardDids \
"RnXJMDxifkBaceAkPizz8F, AmJHyEZ9ofrPz1DUfx97Qo, HBgMBsgaEytzE38djLfNe7" \
--stewardVerkeys \
"~9F4P9aQysR1YATnARMuhxt, ~CVv3mmR7QPanynNMJmTG9f, ~H9LbyNQEZPR1oKzBaNMrDW" \
--trusteeDids \
"L4vaBJDbZiaX68mVHLuZ2E" \
--trusteeVerkeys \
"~QKV8UWR7LHB7APvrWc88xK" \
--network sandbox


sudo python3 create_pool_ledger_genesis_file.py \
--nodeVerkeys \
"85f5c5a0de4236dc01a97e20e1ddf33699c4ddfe5431ced2c8f09e03634edda7, 499ae101d85af6e3093663d98afa631a258518a2ccb2dc5985d5ca248b39ee0e, 41f152fe61923ba93012e1a2309c07a5dc62d1772ec715a44fbb6afef18c8aa7" \
--nodeBlskeys \
"tP6NHFxgWayNLXWrAu6jSdkauHRAmViF11BhELfNenMJxC9vbg7GQwqh1W9w3bzbR6kCSjZuqwfktvtdzzx8Bx1NZuWzUN9a7nEehRWjH4ozKPH7P6tw6Et9W1yyX7wj33nVWAotZ2r9zoYouGV7ybg9ijmQHhYiqAYqXerQ6n7zD2, CkXUu3Sqrm8212ahXf2G6fpQctMW86rPR5o4AFi5LJytw3NsDPzba83m5xCNuvSS353NYEdDg8EZtsWEDMMpgUpAJAB1hYzaxAybcozwkYgoSi941wi6HqJHiNLxWgHzizwXGRY2KymcTqC385WkGnMLew6SzhajcP8wVniyZRz3pi, ftbhBQme51s3UZPavohqouyQkGNWf43fDn9ddey1Jm1vGpoquWh3suR9MCEj4BVvfnwnd7BiLGwSb6FfHF3wwPxYqKdzi3qq4MrxRkTDFCm7ZmbTPBkuSUy5Yr41cFeGFDP21TrZrYZb8oNjYCbJe9VxskrJyXpmbY2s2hWWVCsTNe" \
--nodeBlsProofs \
"QwxHLEJFt1HXuE7P6UdpXztNaNVAoFdiTbhMGXtQgPFCC7GbSG5UAXPFHdkmfsSV9jjyVataX2ujKCEqZn2hpxcnfeBEYioYdqehPGH2VLh1Qw3XZKC3vFW1kc3uMaRtHqWWR6m4Enu2qLuSdFcLtYCJreDpHghB8ds42QHXwoZ8T1, QmrjxheeyDAFknchT4AEBLD6fKVLS9ZMuXDmhstXXnecB64zBtzgmUFHQgoHtrvfPU6A4RS1uWb3AjBVBZh8QBquB1DMfGTGpYszvCQDhgLJtnvrJjVX7whtVT4r33KyCvicPyHXk1ku3H3MYJSbKgC8a9NUv19q2BugsZn1nLSgHm, Qy4DvpUTGiegNyaNhhPXv2oURCciHASsWV9YPB44wsopipJd8Yknu6pJ2Nm4m6BoFGmAnRMHNhw6LupYyNY1UGQkwrSZkFWERExrKMYS7xyi33K1PDpzoM3Wfag7ivLCBHRqfsUpbSBep3VgyqogEGCwmwSkVVSe7kJDBsNW9JYVnw" \
--nodeName \
"Node1, Node2, Node3" \
--nodePort \
"9701, 9703, 9705" \
--clientPort \
"9702, 9704, 9706" \
--stewardDids \
"RnXJMDxifkBaceAkPizz8F, AmJHyEZ9ofrPz1DUfx97Qo, PeVR5pdFizbK8WN9THd3mq" \
--nodeNum 1 2 3 \
--network sandbox \