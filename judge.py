import random
import subprocess
import threading
import time
import os
from queue import Queue
import collections
from datetime import datetime

# --- 配置区 ---
JAR_FILES = [
    'uploads/1.jar',
    'uploads/2.jar',
    'uploads/3.jar',
    'uploads/4.jar',
    ...
]
NUM_JARS = len(JAR_FILES)
NUM_COMMANDS_PER_TEST = 12000  # 每次对拍生成的指令数量 (可以增加)
...
LOG_FILE = 'error_log.txt'  # Changed log file name
TIMEOUT_SECONDS = 1  # 单个 JAR 执行超时时间 (秒) - 可能需要增加
OUTPUT_DIR = 'test_results'

def ensure_output_dir():
    """确保输出目录存在"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def create_test_case_dir(test_count):
    """为每个测试用例创建单独的目录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"test_{test_count}"  # Added timestamp for uniqueness
    dir_path = os.path.join(OUTPUT_DIR, dir_name)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


# --- 数据生成 ---

# code here

# --- Updated Test Data Generation ---
def generate_test_data(num_commands):
    """生成包含指定数量指令的测试数据列表"""
    # Clear state for the new test case
    # code here
    return commands


# --- JAR 执行与比对 (No changes needed below this line generally) ---

def run_jar(jar_path, input_data, output_queue, jar_index, commands, results_dict, test_count):
    """在单独的进程中运行 JAR 文件并获取输出"""
    try:
        process = subprocess.Popen(
            ['java', '-jar', jar_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,  # 捕获错误输出
            text=True,
            # Ensure consistent encoding, though Popen's default text=True usually handles UTF-8 well.
            # Explicitly setting encoding might be needed if issues arise.
            # encoding='utf-8', # Try adding if encoding issues with stdout/stderr occur
            # errors='ignore' # Or handle encoding errors if they are problematic
        )
        stdout, stderr = process.communicate(input=input_data, timeout=TIMEOUT_SECONDS)
        # print(f"JAR {jar_index+1} ({os.path.basename(jar_path)}) stderr:\n{stderr}") # Debug: show stderr
        output_queue.put((jar_index, stdout.strip().splitlines()))
    except subprocess.TimeoutExpired:
        process.kill()  # Ensure process is killed
        # Try to communicate again to get any final output/error
        stdout_after_kill, stderr_after_kill = process.communicate()
        print(f"Error: JAR {jar_index + 1} ({os.path.basename(jar_path)}) timed out.")
        # print(f"  Stderr after timeout kill for {os.path.basename(jar_path)}:\n{stderr_after_kill}") # Debug
        output_queue.put((jar_index, ["TIMEOUT_ERROR"]))
        current_test_case_dir = create_test_case_dir(test_count)
        write_output_files(current_test_case_dir, commands, results_dict)
    except FileNotFoundError:
        print(f"Error: Java command not found. Make sure Java is installed and in your PATH.")
        output_queue.put((jar_index, ["JAVA_NOT_FOUND_ERROR"]))
        # This is a fatal error for this script, so maybe exit or handle differently
    except Exception as e:
        print(f"Error running JAR {jar_index + 1} ({os.path.basename(jar_path)}): {e}")
        output_queue.put((jar_index, [f"EXECUTION_ERROR: {str(e).splitlines()[0]}"]))  # Keep error brief


def write_output_files(test_case_dir, input_commands, outputs_dict):
    """将输入和每个JAR的输出写入单独的文件"""
    # 写入输入文件
    with open(os.path.join(test_case_dir, "Input.txt"), 'w', encoding='utf-8') as f:
        f.write("\n".join(input_commands))

    # 写入每个JAR的输出文件
    for i in range(NUM_JARS):  # Iterate up to NUM_JARS to handle missing outputs
        output_lines = outputs_dict.get(i, [f"NO_OUTPUT_CAPTURED_FOR_JAR_{i + 1}"])  # Default if no output
        jar_name = os.path.basename(JAR_FILES[i]) if i < len(JAR_FILES) else f"Unknown_JAR_{i + 1}"
        with open(os.path.join(test_case_dir, f"result_{jar_name}.txt"), 'w', encoding='utf-8') as f:
            f.write("\n".join(output_lines))


def write_log(test_case_dir, input_commands, outputs_dict):
    """将错误信息写入日志文件"""
    log_path = os.path.join(test_case_dir, "error_summary_log.txt")  # More descriptive name
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write(f"Test Case Directory: {os.path.basename(test_case_dir)}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Input Commands:\n")
        f.write("\n".join(input_commands))
        f.write("\n\n")
        f.write("Outputs Comparison:\n")

        if not outputs_dict or 0 not in outputs_dict:
            f.write("Error: No output from the reference JAR (JAR 1) or no outputs at all.\n")
            for i in range(NUM_JARS):
                jar_name = os.path.basename(JAR_FILES[i]) if i < len(JAR_FILES) else f"Unknown_JAR_{i + 1}"
                f.write(f"--- Output from JAR {i + 1} ({jar_name}) ---\n")
                f.write("\n".join(outputs_dict.get(i, ["NO_OUTPUT"])))
                f.write("\n")
            f.write("=" * 50 + "\n\n")
            return

        ref_output = outputs_dict[0]
        f.write(f"--- Reference Output (JAR 1: {os.path.basename(JAR_FILES[0])}) ---\n")
        f.write("\n".join(ref_output))
        f.write("\n\n")

        for i in range(1, NUM_JARS):
            jar_name = os.path.basename(JAR_FILES[i]) if i < len(JAR_FILES) else f"Unknown_JAR_{i + 1}"
            current_output = outputs_dict.get(i)
            f.write(f"--- Output from JAR {i + 1} ({jar_name}) ---\n")
            if current_output is None:
                f.write("NO_OUTPUT_CAPTURED\n")
            else:
                f.write("\n".join(current_output))
            f.write("\n")

            if current_output != ref_output:
                f.write(f"MISMATCH with JAR 1!\n")
                # Add more detailed diff if desired here
            f.write("\n")
        f.write("=" * 50 + "\n\n")


# --- 主逻辑 ---

if __name__ == "__main__":
    # ensure_output_dir() # Create base output directory
    if not all(os.path.exists(jar) for jar in JAR_FILES):
        print("Error: One or more JAR files specified in JAR_FILES do not exist.")
        print("Please check the paths:")
        for jar_path_check in JAR_FILES:  # Renamed variable to avoid conflict
            if not os.path.exists(jar_path_check):
                print(f"- {jar_path_check}")
        exit(1)
    if NUM_JARS == 0:
        print("Error: No JAR files specified in JAR_FILES. Exiting.")
        exit(1)

    test_count = 0
    error_count = 0
    print(f"Starting parallel testing with {NUM_JARS} JAR files...")
    print(f"Timeout per JAR: {TIMEOUT_SECONDS}s. Commands per test: {NUM_COMMANDS_PER_TEST}.")
    print(f"Outputting results to: {OUTPUT_DIR}")

    try:
        while True:  # Loop for multiple test cases
            test_count += 1
            # current_test_case_dir = create_test_case_dir(test_count) # Create dir for this test
            print(f"\n--- Running Test Case {test_count} ---")

            commands = generate_test_data(NUM_COMMANDS_PER_TEST)
            if not commands:
                print("Failed to generate any commands. Skipping test case.")
                continue
            input_str = "\n".join(commands)

            output_queue = Queue()
            threads = []
            results_dict = {}  # Use a dictionary {jar_index: output_lines}

            start_time = time.time()

            for i, jar_file_to_run in enumerate(JAR_FILES):  # Renamed variable
                thread = threading.Thread(target=run_jar,
                                          args=(jar_file_to_run, input_str, output_queue, i, commands, results_dict,
                                                test_count))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()  # This is simpler and ensures all threads finish

            end_time = time.time()
            print(f"Test Case {test_count} execution time: {end_time - start_time:.2f} seconds")

            # Collect results from queue
            while not output_queue.empty():
                jar_idx, output_lines_from_q = output_queue.get()  # Renamed variable
                results_dict[jar_idx] = output_lines_from_q

            # Write all outputs to files first
            # write_output_files(current_test_case_dir, commands, results_dict)

            # --- Comparison Logic ---
            inconsistent_found = False
            if 0 not in results_dict:  # Reference JAR failed or no output
                print(
                    f"Error: Reference JAR (JAR 1: {os.path.basename(JAR_FILES[0])}) did not produce output or failed.")
                inconsistent_found = True
            else:
                ref_output_lines = results_dict[0]
                for i in range(1, NUM_JARS):
                    current_output_lines = results_dict.get(i)
                    if current_output_lines is None:
                        print(f"Warning: JAR {i + 1} ({os.path.basename(JAR_FILES[i])}) did not produce output.")
                        inconsistent_found = True
                        break  # Mismatch found
                    if current_output_lines != ref_output_lines:
                        print(
                            f"Inconsistency detected between JAR 1 and JAR {i + 1} ({os.path.basename(JAR_FILES[i])})!")
                        inconsistent_found = True
                        break  # Mismatch found

            if inconsistent_found:
                error_count += 1
                current_test_case_dir = create_test_case_dir(test_count)
                print(f"Details saved to: {current_test_case_dir}")
                write_output_files(current_test_case_dir, commands, results_dict)
                write_log(current_test_case_dir, commands, results_dict)  # Write detailed log on error
            else:
                print("Outputs are consistent for this test case.")
                # Optionally, clean up non-error directories if desired, or keep all
                # For now, keep all for inspection.

    except KeyboardInterrupt:
        print("\n--- Testing Interrupted by User ---")
    except Exception as e:
        print(f"\n--- An unexpected error occurred in the judge script: {e} ---")
        import traceback

        traceback.print_exc()
    finally:
        print(f"\n--- Testing Finished ---")
        print(f"Total test cases run: {test_count}")
        print(f"Inconsistencies / Failures logged: {error_count}")
        if error_count > 0:
            print(f"Check the subdirectories in '{OUTPUT_DIR}' for details of failed tests.")
        else:
            print(f"All run test cases were consistent (if any errors occurred before comparison, check console).")
