ArcMaxM=$(sysctl hw.physmem | awk '{print $2}')
ArcM=$(sysctl kstat.zfs.misc.arcstats.size | awk '{print $2}')

Wid=${1:-100}
let Wid-=19

Stat=$(echo "${ArcM} / ${ArcMaxM} * 100" | bc -l | sed -n 's/\([0-9]*.[0-9]\{3\}\).*/\1/p')
_Max=${Stat}
_Max=$(echo "${_Max}*${Wid}/100" | bc -l)
Max=$(awk '{printf("%.0f\n", $1)}' <<< "${_Max}")

echo -n "["
Cnt=1
while [[ ${Cnt} -le ${Wid} ]]
do
	let Cnt++
	if [[ ${Cnt} -lt $Max ]]
	then
		echo -n "="
	else
		echo -n "."
	fi
done
echo  "] ${Stat}% $(echo ${ArcM} | awk '{print $1/1024/1024}')M"
