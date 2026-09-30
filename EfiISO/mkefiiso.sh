#!/bin/sh

rm -f ventoy_efiboot.img.*

cd ISO
mkisofs -R -D -sysid 237BOOTS -V 237BOOTS -P "237Boots (C) 2026 Edmond Noumegni" -p 'https://github.com/noumegniedmond237-sketch/237Boots' -o ../ventoy_efiboot.img ./ 
cd ..

xz --check=crc32 ventoy_efiboot.img

rm -f ../INSTALL/ventoy/ventoy_efiboot.img.xz
cp -a ventoy_efiboot.img.xz ../INSTALL/ventoy/

