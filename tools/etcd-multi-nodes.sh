#!/bin/bash


# more details for https://coreos.com/etcd/docs/latest

which etcd &>/dev/null || { echo "etcd not installed, please install etcd first" && exit 1; }

if [ $# -eq 0 ] ; then
    echo "Usage: `basename $0` ip1 ip2 ip3"
    echo "    ip1 ip2 ip3 are the ip address of node etcd_1 etcd_2 etcd_3"
    exit 1
fi

etcd_1=$1
index=1
while [ $# -gt 0 ] ; do
    h="etcd_$index" 
    if [ $index -eq 1 ] ; then
        CLUSTER="$h=http://$1:2380"
    else
        CLUSTER="$CLUSTER,$h=http://$1:2380"
    fi 
    index=$(($index+1))
    shift
done

network_device=${network_device:-eth1}
echo $network_device
hostname=$(hostname)
hostip=$(ifconfig $network_device | grep "inet addr" | cut -d ':' -f 2 | cut -d ' ' -f 1)
# -initial-advertise-peer-urls  :  tell others what peer urls of me
# -listen-peer-urls             :  what peer urls of me

# -listen-client-urls           :  what client urls to listen
# -advertise-client-urls        :  tell others what client urls to listen of me

# -initial-cluster-state        :  new means join a new cluster; existing means join an existing cluster
#                               :  new not means clear 

<<<<<<< HEAD

etcd --name $hostname \
     --initial-advertise-peer-urls http://$hostip:2380 \
     --listen-peer-urls http://$hostip:2380 \
     --listen-client-urls http://$hostip:2379,http://127.0.0.1:2379 \
     --advertise-client-urls http://$hostip:2379 \
     --discovery $cluster_url \
     --initial-cluster-state new &
=======
etcd --name etcd_1 \
     --initial-advertise-peer-urls http://$etcd_1:2380 \
     --listen-peer-urls http://$etcd_1:2380 \
     --listen-client-urls http://$etcd_1:2379 \
     --advertise-client-urls http://$etcd_1:2379 \
     --initial-cluster-token etcd-cluster \
     --initial-cluster $CLUSTER \
     --initial-cluster-state new 
>>>>>>> fab8ab478995fd60402b77cf632599780896963c
