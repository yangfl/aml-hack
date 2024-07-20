openssl enc -d -aes-256-cbc -iv 00000000000000000000000000000000 -K a72741f1bedf00bf51e4fe073300ba42978ad9d9ad8735bcf5873236227b6b8d -in DDR_ENC.USB -out DDR.USB

dd if=UBOOT.USB of=fip_enc bs=512 skip=1 conv=notrunc
openssl enc -d -aes-256-cbc -iv 00000000000000000000000000000000 -K 9cfbd37054a010c7dbf4a283707615e0442fe3c7e37be93e04a99ac50cb7df8b -in fip -out aaa
