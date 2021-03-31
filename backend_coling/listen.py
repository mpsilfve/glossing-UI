
import time, shutil, json, model_inference
from sortedcontainers import SortedList
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# make a sorted list of jobs 
job_list = SortedList()


if __name__ == "__main__":
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = True
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

def on_created(event):
    print("on created")
    print("hey, {} has been created!".format(event.src_path))

    path = str(event.src_path)
    path_components = path.split("_")

    if path_components[0] == "/data/coling":
        newPath = shutil.copy(path, "./jobs")
        further_path_components = path_components[1].split(".")
        job_id = further_path_components[0]
        job_list.add(job_id)
        # pass this new_job_data dicitonary to the unwrap.py script
        # add it to the sorted list 
        # act on the first item in the list 


def on_deleted(event):
    print "on_deleted"
    # print(f"what the f**k! Someone deleted {event.src_path}!")

def on_modified(event):
    print "on_modified"
    # print(f"hey buddy, {event.src_path} has been modified")

def on_moved(event):
    print "on_moved"
    # print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")

my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

path = "/data"
go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)

my_observer.start()
try:
    while True:
        time.sleep(1)
        while job_list.__len__() > 0:
            #  pass job from job list into model_inference.py
            model_inference.process_file(job_list.pop(0))
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()

