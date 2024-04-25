#!/bin/bash

set -o pipefail

# Global configurations
NAME="$1"                              # Experiment or job prefix
TASKS="$2"                             # Number of tasks to request for each job
PHOTON_ENERGY="$3"                     # Photon energy input
JOB_LIMIT=200                          # Limit of job submissions
SUBMITTED_JOBS=0                       # Counter for submitted jobs

# Pattern_sim specifications
GEOM="Eiger4M.geom"                    # Geometry file
CRYSTAL="1IC6.cell"                    # Crystal file
INPUT="1IC6.pdb.hkl"                   # Constant HKL input file
POINT_GROUP=4/mmm
CRYSTAL_SIZE_MIN=1000
CRYSTAL_SIZE_MAX=1000
SPECTRUM="tophat"
SAMPLING=7
BANDWIDTH=0.01
N_PHOTONS=3e8
BEAM_RADIUS=5e-6

# Parses and sorts partitions by core count
parse_partitions() {
  echo "rcgpu7:13,publicgpu:15,wzhengpu1:2,rcgpu7:10,wzhengpu1:2,cmuhichgpu1:3,mrline2:2,rcgpu5:2,fn2:1,fn:1,htc:6,wildfire:19,gpu:20,htcgpu:8,publicgpu:2,htcgpu8:2,htcgpu:8,relion:2,rcgpu5:2,gmascaro:4,sulccpu1:1,htcgpu1:3,htcgpu2:2,htcgp\
u9:2,bbbartelgpu:1,htcgpu1:2,htcgpu9:2,gdcsgpu1:1,wzhengpu1:2" | tr ',' '\n' | sort -t ':' -k2,2nr
}

# Setup the main directory
setup_directory() {
  mkdir -p "$NAME" && cd "$NAME" || return 1
  ln -sf "../$GEOM" .
  ln -sf "../$CRYSTAL" .
  ln -sf "../$INPUT" .
}

# Generates and submits SLURM job scripts
generate_and_submit() {
  local partition="$1"
  local cores="$2"
  local step="$3"
  local job_name="${NAME}_${step}_${partition}"
  local slurm_file="${job_name}.sh"
  local job_time="0-60:00" # Default job time
  local job_qos="wildfire" # Default QoS

  # Adjust settings for HTC partitions
  if [[ $partition =~ htc(gpu)?([0-9]+)?$ ]]; then
    job_time="4:00:00"
    job_qos="normal"
  fi

  cat > "$slurm_file" <<EOF
#!/bin/sh

#SBATCH --time=$job_time
#SBATCH --ntasks=$cores
#SBATCH --chdir=$PWD
#SBATCH --job-name=$job_name
#SBATCH --output=${job_name}.out
#SBATCH --error=${job_name}.err
#SBATCH --partition=$partition
#SBATCH --qos=$job_qos

pattern_sim -g $GEOM -p $CRYSTAL --number=$cores -o $job_name -i $INPUT -r -y $POINT_GROUP --min-size=$CRYSTAL_SIZE_MIN --max-size=$CRYSTAL_SIZE_MAX --spectrum=$SPECTRUM -s $SAMPLING --background=0 --beam-bandwidth=$BANDWIDTH --photon-energy=$PHOTON_ENERGY --nphotons=$N_PHOTONS --beam-radius=$BEAM_RADIUS
EOF

  # Submit the job if the limit has not been reached
  if [[ $SUBMITTED_JOBS -lt $JOB_LIMIT ]]; then
    if sbatch "$slurm_file" > /dev/null; then
      ((SUBMITTED_JOBS++))
    else
      printf "Failed to submit job for step %d on partition %s.\n" "$step" "$partition" >&2
    fi
  else
    printf "Reached the limit of %d job submissions.\n" "$JOB_LIMIT" >&2
    return 1
  fi
}

# Main function for setting up and submitting jobs
main() {
  if ! setup_directory; then
    printf "Failed to set up directory '%s'.\n" "$NAME" >&2
    return 1
  fi

  local partitions
  partitions=$(parse_partitions)

  local step=1
  for pc in $partitions; do
    local partition="${pc%%:*}"
    local cores="${pc##*:}"
    while [[ $SUBMITTED_JOBS -lt $JOB_LIMIT ]] && [[ $step -le $TASKS ]]; do
      generate_and_submit "$partition" "$cores" "$step"
      ((step++))
    done
  done

  cd .. || return 1
}

main "$@"

