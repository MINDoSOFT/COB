import subprocess
import math
import os

data_dir = "../rcnn-depth/eccv14-code/demo-data"
images_dir = data_dir + "/images"
hha_dir = data_dir + "/hha"
output_dir = "./output"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

rgb_files = sorted(os.listdir(images_dir))
#print(rgb_files)
hha_files = sorted(os.listdir(hha_dir))

#print(rgb_files[0]);

matlab_script = """
install;
%% Setup the output file
out_file = fullfile('%s');

%% Read an input image
I = imread(fullfile('%s'));
D = imread(fullfile('%s'));

%% Run COB. For an image of PASCALContext, it should take:
%%  - less than 1s on the GPU
%%  - around 8s on the CPU
tic; [ucm2, ucms, ~, O, E] = im2ucm(cat(3,I,D)); toc;
sp = bwlabel(ucm2 < 0.20); sp = sp(2:2:end, 2:2:end);
if(~isempty(out_file)), save(out_file, 'sp'); end
disp('Compute the Superpixels OK');""";

launch_save_frame_batch_wait = "matlab -nodesktop -nosplash -r '%s;exit;'"
launch_save_frame_batch = '%s &' % (launch_save_frame_batch_wait)

testing = False; # If true just messages will be displayed

def clearWorkers():
  # Clear the worker scripts
  for x in range(0, workers):
    worker_script = "worker" + str(x+1);
    worker_script_filename = worker_script + ".m";
    if os.path.exists(worker_script_filename):
      os.remove(worker_script_filename);

#print(len(rgb_files))

#for image, hha in zip(rgb_files, hha_files):
    #print(image, hha)
#    fileName = os.path.splitext(image)[0]
#    print matlab_script % (output_dir + '/' + fileName + '.mat', images_dir + '/' + image, hha_dir + '/' + hha)

#print(launch_generate_frame_list)
#print(launch_save_frame_batch)

#workers = cnt - 1;
# For testing
#workers = 4;
workers = 4;

cnt = len(rgb_files);

# Keep launching workers in batches until frame list is consumed
for ii in range(0, int(math.ceil(float(cnt)/workers))):
  # Spawn the workers
  for x in range(0, workers):
    batchId = (x+1+(ii * workers))
    if (batchId > cnt):
      clearWorkers();
      exit();
    print('BatchId: %d' % (batchId))
    if(True or batchId==121): # adjust if you want only a specific file
      fileName = os.path.splitext(rgb_files[batchId-1])[0]
      matlab_script_with_vars = matlab_script % (output_dir + '/' + fileName + '.mat', images_dir + '/' + rgb_files[batchId-1], hha_dir + '/' + hha_files[batchId-1])
      
      worker_script = "worker" + str(x+1);
      if (x == (workers-1) or (batchId == cnt)): # Wait at last worker of current or total batch
        spawn_command = launch_save_frame_batch_wait % (worker_script)
      else:
        spawn_command = launch_save_frame_batch % (worker_script)
      if (testing):
        print(spawn_command)
      else:
        with open(worker_script + ".m", "w") as text_file:
          text_file.write("{0}".format(matlab_script_with_vars))
        subprocess.call(spawn_command, shell=True)

clearWorkers();
exit();

