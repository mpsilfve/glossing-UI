
import time, shutil, json, model_inference, process_output
from sortedcontainers import SortedList
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# make a sorted list of jobs 
# job id is based on time stamp, so sorted list of jobs is effectively a queue.
job_list = SortedList()


if __name__ == "__main__":
    # CREATE WATCHDOG EVENT HANDLER
    # Some variables for the warchdog observer
    # defines which file patterns to observe
    patterns = "*"
    # defines which file patterns to ignore
    ignore_patterns = ""
    # if true, then Observer watches only files
    ignore_directories = True
    # sets if file directories are case sensitive or not
    case_sensitive = True
    # Watchdog event handler - object that is notified when something is chnaged in the filesystem we are observing
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

# FILESYSTEM WATCHDOG EVENT FUNCTIONS
# the following are functiosn that are run when my_event_handler receives an event
def on_created(event):
    print("on created")
    print("hey, {} has been created!".format(event.src_path))

    # the first part of new file path contains the name of the model type to be used. 
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


# attach the functions defined above to specific handler events
my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

# CREATE WATCHDOG OBSERVER
# path to be monitores
path = "/data"
# whether or not to monitor subdirectories
go_recursively = True
# create the observer and pass the event handler, path and go_recursively boolean
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)

# start the observer
my_observer.start()
try:
    while True:
        # add sleep time to avoid running continuosly
        time.sleep(1)
        while job_list.__len__() > 0:
            #  pass job from job list into model_inference.py
            model_inference.process_file(job_list.pop(0))
            # 
            # process_output.process_output()
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()

