function locus-checkpoint () {
    if [ "$1" == "backup" ]; then
        echo "########################################"
        echo "backup"
        mkdir -p /tmp/locus-scratch-checkpoint
        cp -rv ~/locus/scratch/* /tmp/locus-scratch-checkpoint/
    elif [ "$1" == "restore" ]; then
        echo "########################################"
        echo "restore"
        mkdir -p /tmp/locus-scratch-checkpoint
        cp -rv /tmp/locus-scratch-checkpoint/* ~/locus/scratch/
        rm -rfv /tmp/locus-scratch-checkpoint/*
    else
        echo "usage: locus-checkpoint <backup|restore>"
        return 1
    fi
}

