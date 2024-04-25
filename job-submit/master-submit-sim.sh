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
POINT_GROUP="4/mmm"
CRYSTAL_SIZE_MIN=10000                 # corrected from 1000
CRYSTAL_SIZE_MAX=10000                 # Crystal size range (min, max)
SPECTRUM="tophat" 
SAMPLING=7
BANDWIDTH=0.01
N_PHOTONS=3e8                           # flux
BEAM_RADIUS=10e-6                       # 10 microns
NUMBER_OF_PATTERNS=10000

# Setup the main directory
setup_directory() {
  mkdir -p "$NAME" && cd "$NAME" || return 1
  ln -sf "../$GEOM" .
  ln -sf "../$CRYSTAL" .
  ln -sf "../$INPUT" .
}

# Generates and submits SLURM job scripts
generate_and_submit() {
  # local partition="htc1"
  # local cores=9
  # local job_time="4:00:00" # Default job time
  # local job_qos="normal" # Default QoS

  # local partition="htc1"
  # local cores=11
  # local job_time="4:00:00" # Default job time
  # local job_qos="normal" # Default QoS

  # local partition="htc2"
  # local cores=11
  # local job_time="4:00:00" # Default job time
  # local job_qos="normal" # Default QoS

  local partition="rcgpu4"
  local cores=1
  local job_time="10:00:00" # Default job time
  local job_qos="wildfire" # Default QoS

  # local partition="publicgpu"
  # local cores=4
  # local job_time="10:00:00" # Default job time
  # local job_qos="wildfire" # Default QoS

  # local partition="rcgpu3"
  # local cores=2
  # local job_time="10:00:00" # Default job time
  # local job_qos="wildfire" # Default QoS

  # local partition="phi"
  # local cores=18
  # local job_time="10:00:00" # Default job time
  # local job_qos="wildfire" # Default QoS

  # local partition="cidsegpu3"
  # local cores=2
  # local job_time="10:00:00" # Default job time
  # local job_qos="wildfire" # Default QoS

  local step="$1"
  local job_name="${NAME}_${step}_${partition}"
  local slurm_file="${job_name}.sh"
  {
    printf "#!/bin/sh\n\n"
    printf "#SBATCH --time=%s\n" "$job_time"
    printf "#SBATCH --ntasks=%s\n" "$cores"
    printf "#SBATCH --chdir=%s\n" "$PWD"
    printf "#SBATCH --job-name=%s\n" "$job_name"
    printf "#SBATCH --output=%s.out\n" "$job_name"
    printf "#SBATCH --error=%s.err\n" "$job_name"
    printf "#SBATCH --partition=%s\n" "$partition"
    printf "#SBATCH --qos=%s\n\n" "$job_qos"
    printf "pattern_sim -g $GEOM -p $CRYSTAL --number=$NUMBER_OF_PATTERNS -o $job_name -i $INPUT -r -y $POINT_GROUP --min-size=$CRYSTAL_SIZE_MIN --max-size=$CRYSTAL_SIZE_MAX --spectrum=$SPECTRUM -s $SAMPLING --background=0 --beam-bandwidth=$BANDWIDTH --photon-energy=$PHOTON_ENERGY --nphotons=$N_PHOTONS --beam-radius=$BEAM_RADIUS\n"
  } > "$slurm_file"

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

  for ((step=1; step <= TASKS; step++)); do
    generate_and_submit "$step"
  done

  cd .. || return 1
}

main "$@"
