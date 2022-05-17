# file watch 
# dynet_seed = 42  # Load that from the JSON
# run_command([
#     "python", "run_transducer.py",
#     "--dynet-seed", dynet_seed,
#     "--dynet-mem", "1000"
# ])
import time, shutil, os
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from sortedcontainers import SortedList
import model_inference

# job_list is a sorted list, by job ID
job_list = SortedList()

if __name__ == "__main__":
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = True
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

# I need 
def on_created(event):
    print(f"hey, {event.src_path} has been brought to life!")
    path = str(event.src_path)
    path_components = path.split("_")
    # path_components = path.split("/")

    if path_components[0] == "/data/inputs/fairseq":
        newPath = shutil.copy(f"{event.src_path}", "./jobs")
        #  then remove the file from /data/fairseq
        #  then make a list of current jobs
        #  feed the next in line job 
        #  pass the next job into a script  

        # TODO: just write the files to backend_fairseq for now
        #os.remove(event.src_path)
        further_path_components = path_components[1].split(".")
        job_id = further_path_components[0]
        job_list.add(job_id)

    elif path_components[0] == "/data/results/sentence":
        print("Spotted sentence!")
    
    # add it to the sorted list 
    # act on the first item in the list 

def on_deleted(event):
    print(f"what the f**k! Someone deleted {event.src_path}!")

def on_modified(event):
    print(f"hey buddy, {event.src_path} has been modified")

def on_moved(event):
    print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")

my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

path = "/data"
go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)

# object for submitting Fairseq jobs
submitter = model_inference.FairseqSubmitter()

my_observer.start()
try:
    while True:
        # sleep to avoid running constantly
        time.sleep(1)
        # process jobs in the job list
        if len(job_list) > 0:
            # pass job to model_inference.py
            tic = time.time()
            current_job = job_list.pop(0)

            # process file
            submitter.process_batch(current_job)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()

