# Instalación basada en fichero de configuración preseed.

1. Descargamos la imagen iso de debian en este caso:

```
curl -#LO https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-11.5.0-amd64-netinst.iso
```

2. Instalamos una aplicación que nos permita manipular la imagen ISO y extraiga los fecheros que tiene contenido en la imagen y crear asi una imagen ISO a partir del sistema de ficheros:

```
sudo apt -y install xorriso
```

3. Se introducen los ficheros contenidos en la imagen net-install en el sistema de ficheros "isofiles" con el siguiente comando, si no existe el directorio lo crea automáticamente:

```
xorriso -osirrox on -indev debian-11.5.0-amd64-netinst.iso -extract / isofiles/
```

4. Descargamos la plantilla preseed de debian:

```
curl -#L https://www.debian.org/releases/stable/example-preseed.txt -o preseed.cfg
```

5. Modificamos la plantilla preseed de acuerdo a nuestra necesidades, en principio se editará de forma sencilla para usar el idioma español y evitar que se realice la encuesta final, además de elegir el entorno de trabajo y la localización del GRUB:

    [preseed.cfg](/preseed_lvm_cryp.cfg)

- GRUB:

```
d-i grub-installer/only_debian boolean true
d-i grub-installer/with_other_os boolean true
d-i grub-installer/bootdev  string default
```

- Selección de paquetes instalados:

```
d-i pkgsel/run_tasksel boolean false
d-i pkgsel/include string openssh-server build-essential
```

- Evitar la encuesta final:

```
popularity-contest popularity-contest/participate boolean false
```

- LVM:

```
d-i partman-auto/method string lvm

##modificación
# If one of the disks that are going to be automatically partitioned
# contains an old LVM configuration, the user will normally receive a
# warning. This can be preseeded away...
d-i partman-lvm/device_remove_lvm boolean true
# The same applies to pre-existing software RAID array:
d-i partman-md/device_remove_md boolean true
# And the same goes for the confirmation to write the lvm partitions.
d-i partman-lvm/confirm boolean true
#d-i partman-lvm/confirm_nooverwrite boolean true
# You can define the amount of space that will be used for the LVM volume
# group. It can either be a size with its unit (eg. 20 GB), a percentage of
# free space or the 'max' keyword.
d-i partman-auto-lvm/guided_size string max
##añadido

d-i partman-auto/choose_recipe select boot-root
d-i partman-auto-lvm/new_vg_name string vg00
d-i partman-auto/expert_recipe string                         \
      boot-root ::                                            \
              1024 1024 1024 ext4                             \
                      $primary{ } $bootable{ }                \
                      method{ format } format{ }              \
                      use_filesystem{ } filesystem{ ext4 }    \
                      mountpoint{ /boot }                     \
              .                                               \
              100 1000 1000000000 ext4                        \
                      $defaultignore{ }                       \
                      $primary{ }                             \
                      method{ lvm }                           \
                      device{ /dev/vda }                      \
                      vg_name{ vg00 }                         \
              .                                               \
              1024 2048 1024 swap                               \
                      $lvmok{ } lv_name{ lv_swap } in_vg{ vg00 } \
                      method{ swap } format{ }                \
              .                                               \
              3072 3072 3072 ext4                               \
                      $lvmok{} lv_name{ lv_var } in_vg{ vg00 } \
                      method{ format } format{ }              \
                      use_filesystem{ } filesystem{ ext4 }    \
                      mountpoint{ /var }                         \
              .                                               \
              3072 3072 3072 ext4                               \
                      $lvmok{} lv_name{ lv_raiz } in_vg{ vg00 } \
                      method{ format } format{ }              \
                      use_filesystem{ } filesystem{ ext4 }    \
                      mountpoint{ / }                         \
              .                                               \
              1072 1072 1072 ext4                               \
                      $lvmok{} lv_name{ lv_home } in_vg{ vg00 } \
                      method{ format } format{ }              \
                      use_filesystem{ } filesystem{ ext4 }    \
                      mountpoint{ /home }                         \
```

6. Modificamos el fichero txt.cfg para que se realice la instalación en español y establezca el teclado en español:

```
label install
    menu label ^Install
    kernel /install.amd/vmlinuz
    append vga=788 initrd=/install.amd/initrd.gz --- quiet 
label unattended-gnome
        menu label ^Instalacion Debian Desatendida Preseed
        kernel /install.amd/gtk/vmlinuz
        append vga=788 initrd=/install.amd/gtk/initrd.gz preseed/file=/cdrom/preseed.cfg locale=es_ES console-setup/ask_detect=false keyboard-configuration/xkb-keymap=es --
```

7. Introducimos el fichero preseed.cfg al directorio isofiles:

```
cp preseed.cfg isofiles
```

8. Creamos la imagen ISO dando permisos de escritura a todos y generamos la imagen con el comando genisoimage:

```
chmod a+w isofiles/isolinux/isolinux.bin
genisoimage -r -J -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -o preseed-debian-11.iso isofiles
```

9. Creamos la máquina (con 10GB de almacenamiento mínimo) introduciendo como imagen ISO la creada con preseed, al iniciar la máquina aparecerá un menu del que tendremos que seleccionar la opción de instalación desatendida: