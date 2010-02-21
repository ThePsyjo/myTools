#create="2005-10-05 14:20:00"
#create="2008-01-29"

create="$*"

secs() { echo $(( $(date +%s) - $(date -d "${create}" +%s) )); }


date "+current date > %A, %Y-%m-%d %H:%M:%S %Z"
date -d "${create}" "+object created at > %A, %Y-%m-%d %H:%M:%S %Z"


echo "
age: $(echo "$(date +%Y -d @$(secs)) - 1970"  | bc) years, $(echo "$(date +%m -d @$(secs)) - 1"  | bc) months, $(date +%d -d @$(secs)) days.
     $(date +%H -d @$(secs)) hours, $(date +%M -d @$(secs)) minutes, $(date +%d -d @$(secs)) seconds.
     
     $(secs) sec.
     "

