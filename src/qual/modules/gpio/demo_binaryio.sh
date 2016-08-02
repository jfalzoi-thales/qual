#!/bin/sh

if [ "$1" = "setDiscreteOutput" ]; then
    echo "Set $2 $3"
    if [ "$3" = "1" ]; then
        touch /tmp/binaryio_$2
    else
        rm -f /tmp/binaryio_$2
    fi
    exit 0
fi

if [ "$1" = "getDiscreteInput" ]; then
    case $2 in
        LLS_IN_GP_KL_01)
            OUT_PIN=GPIO_MGR_OUTPUT_6
            ;;
        LLS_IN_GP_KL_02)
            OUT_PIN=LLS_OUT_GP_KL_01
            ;;
        LLS_IN_GP_KL_03)
            OUT_PIN=LLS_OUT_GP_KL_02
            ;;
        LLS_IN_GP_KL_04)
            OUT_PIN=LLS_OUT_GP_KL_03
            ;;
        *)
            echo "Unknown input pin $2"
            exit 1
            ;;
    esac
    if [ -e /tmp/binaryio_$OUT_PIN ]; then
        echo "$2 Discrete value = 1"
    else
        echo "$2 Discrete value = 0"
    fi
    exit 0
fi

echo "Unrecognized command"
exit 1
