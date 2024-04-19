import subprocess
import sys
import time

def fetch_sinfo():
    try:
        print("Fetching partition information...")
        result = subprocess.run(['sinfo', '-o', '%P %a %l %D %T %N'], capture_output=True, text=True)
        if result.returncode == 0:
            # Simple loading bar
            total = 10
            for i in range(total):
                bar_length = int((i + 1) / total * 50)
                bar = '#' * bar_length + '-' * (50 - bar_length)
                print(f"\r[{bar}] {int((i + 1) / total * 100)}%", end='', flush=True)
                time.sleep(0.5)  # Sleep to simulate loading time
            print("\n")
            return result.stdout
        else:
            print("\nFailed to fetch GPU status:", result.stderr)
            return None
    except Exception as e:
        print("\nAn error occurred while fetching GPU status:", str(e))
        return None

def parse_sinfo(sinfo_output):
    partitions = []
    for line in sinfo_output.strip().split('\n')[1:]:
        parts = line.split()
        if len(parts) >= 5:
            partitions.append({
                'name': parts[0],
                'availability': parts[1],
                'timelimit': parts[2],
                'nodes': int(parts[3]),
                'state': parts[4],
                'nodelist': parts[5] if len(parts) > 5 else None
            })
    return partitions

def select_optimal_partition(partitions, resource_type):
    optimal = None
    max_idle_nodes = -1
    for part in partitions:
        if ('gpu' in part['name'].lower() if resource_type == 'gpu' else 'gpu' not in part['name'].lower()):
            if part['state'].lower() == 'idle' and part['nodes'] > max_idle_nodes:
                max_idle_nodes = part['nodes']
                optimal = part
    return optimal

def determine_qos(partition_name):
    if 'htc' in partition_name:
        return 'normal'
    elif 'general' in partition_name:
        return 'public'
    else:
        return 'wildfire'

def start_interactive_session(partition_name, resource_type, time_hours):
    qos = determine_qos(partition_name)
    gres_option = f"--gres={resource_type}:1" if resource_type == 'gpu' else ""
    time_flag = f"--time={time_hours}"
    command = f"interactive -p {partition_name} -q {qos} {time_flag} {gres_option}"
    print("Starting interactive session with the following command:")
    print(command)
    try:
        subprocess.run(command, shell=True)
    except Exception as e:
        print("Failed to start session:", e)

def main():
    if len(sys.argv) > 3 and sys.argv[1] == 'start':
        resource_type = 'gpu' if sys.argv[2] == 'gpu' else 'cpu'
        time_hours = sys.argv[3]
        sinfo_output = fetch_sinfo()
        if sinfo_output:
            partitions = parse_sinfo(sinfo_output)
            optimal_partition = select_optimal_partition(partitions, resource_type)
            if optimal_partition:
                print("Selected optimal partition based on availability:", optimal_partition)
                start_interactive_session(optimal_partition['name'], resource_type, time_hours)
            else:
                print("No optimal partition found based on the criteria.")
    else:
        print("Usage:")
        print("python script.py start [cpu|gpu] <hours>")

if __name__ == "__main__":
    main()
