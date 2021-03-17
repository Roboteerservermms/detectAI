DISK_TOTAL=`df -P | grep -v ^Filesystem | awk '{sum += $2} END { print sum; }'`
DISK_USED=`df -P | grep -v ^Filesystem | awk '{sum += $3} END { print sum; }'`
DISK_PER=`echo "100*$DISK_USED/$DISK_TOTAL" | bc -l`
echo "$DISK_PER"