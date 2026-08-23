function locus-checkpoint () {
    if [ "$1" == "backup" ]; then
        echo "########################################"
        echo "backup"
        mkdir -p ../checkpoint/scratch-backup
        cp -rv ./scratch/* ../checkpoint/scratch-backup/
    elif [ "$1" == "restore" ]; then
        echo "########################################"
        echo "restore"
        mkdir -p ./scratch
        cp -rv ../checkpoint/scratch-backup/* ./scratch/
        rm -rfv ../checkpoint/scratch-backup/*
    else
        echo "usage: locus-checkpoint <backup|restore>"
        return 1
    fi
}
