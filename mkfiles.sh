MaxJobs=${3:-$(nproc)}
FileSize=$1
NumFiles=$2

OutDir=/root/disktest/${FileSize}


#echo ${OutDir} ${FileSize} ${NumFiles}  ${MaxJobs}
#exit

[[ ! -d ${OutDir} ]] && mkdir -pv ${OutDir}
[[ ! -d ${OutDir} ]] && { echo 'something went wrong'; exit; }

for n in $(seq ${NumFiles})
do
  while [[ $(jobs | wc -l) -gt ${MaxJobs} ]]
  do
    sleep 1
  done
  dd if=/dev/urandom of=${OutDir}/$n bs=${FileSize} count=1 &
done
