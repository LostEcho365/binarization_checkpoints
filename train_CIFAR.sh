#!/usr/bin/env sh

############### Host   ##############################
HOST=$(hostname)
echo "Current host is: $HOST"

# Automatic check the host and configure
case $HOST in
"alpha")
    PYTHON="/home/jiaqigu/pkgs/miniforge3/envs/python310venv/bin/python" # python environment path
    TENSORBOARD='/home/jiaqigu/pkgs/miniforge3/envs/python310venv/bin/tensorboard' # tensorboard environment path
    data_path='/home/dataset/'
    ;;
esac

DATE=`date +%Y-%m-%d`

if [ ! -d "$DIRECTORY" ]; then
    mkdir ./save/${DATE}/
fi

############### Configurations ########################
enable_tb_display=false # enable tensorboard display
model=vgg8_bn_bin
data_path='/home/dataset/cifar10'
dataset=cifar10
epochs=160
train_batch_size=128
test_batch_size=128
optimizer=SGD

label_info=binarized

save_path=./save/${DATE}/${dataset}_${model}_${epochs}_${optimizer}_${label_info}
tb_path=${save_path}/tb_log  #tensorboard log path

############### Neural network ############################
{
$PYTHON main.py --dataset ${dataset} \
    --data_path ${data_path}   \
    --arch ${model} --save_path ${save_path} \
    --epochs ${epochs} --learning_rate 0.1 \
    --optimizer ${optimizer} \
	--schedule 80 120  --gammas 0.1 0.1 \
    --attack_sample_size ${train_batch_size} \
    --test_batch_size ${test_batch_size} \
    --workers 4 --ngpu 1 --gpu_id 2 \
    --print_freq 100 --decay 0.0003 --momentum 0.9 \
    # --clustering --lambda_coeff 1e-3    
} &
############## Tensorboard logging ##########################
{
if [ "$enable_tb_display" = true ]; then 
    sleep 30 
    wait
    $TENSORBOARD --logdir $tb_path  --port=6006
fi
} &
{
if [ "$enable_tb_display" = true ]; then
    sleep 45
    wait
    case $HOST in
    "Hydrogen")
        firefox http://0.0.0.0:6006/
        ;;
    "alpha")
        google-chrome http://0.0.0.0:6006/
        ;;
    esac
fi 
} &
wait