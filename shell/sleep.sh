echo sudo pmset repeat sleep MTWRFSU 00:10:00 wakeorpoweron MTWRFSU 08:00:00
sudo pmset repeat wake MTWRFSU 08:01:00 sleep MTWRFSU 00:10:00
#sudo pmset repeat sleep MTWRFSU $1 wakeorpoweron MTWRFSU $2
pmset -g sched
