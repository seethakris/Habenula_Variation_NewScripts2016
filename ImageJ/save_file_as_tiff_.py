import os
from loci.plugins.util import BFVirtualStack
from loci.formats import ChannelSeparator
from ij.io import FileSaver
from ij import ImagePlus
import re
import argparse

filesep = os.path.sep

   
# Run through folder and save tiff files in appropriate folders
def run(FolderName, SaveFolder):
    # Find tiffiles in folder
    onlyfiles = [f for f in os.listdir(FolderName) if
                 os.path.isfile(os.path.join(FolderName, f)) and f.lower().endswith('.tif')]

    for ii in xrange(0, len(onlyfiles)):
        path = os.path.join(FolderName, onlyfiles[ii])
        print "Processing file..", path

        # Find stimulus, Block, regions from filename for sorting

        # Get all underscores
        underscores = [m.start() for m in re.finditer('_', onlyfiles[ii])]
		
        # Fish Name
        findfish = onlyfiles[ii].find('Fish')
        findunderscore = [i for i in underscores if i > findfish][0]
        fishnum = onlyfiles[ii][findfish:findunderscore]

        print 'Fish Number..', fishnum

        # Block
        findblock = onlyfiles[ii].find('Block')
        findunderscore = [i for i in underscores if i > findblock][0]
        blocknum = onlyfiles[ii][findblock:findunderscore]

        print 'Block Number..', blocknum

        # Stimulus
        findstimulus = onlyfiles[ii].find('Blue')
        findunderscore = [i for i in underscores if i > findstimulus][0]
        stimulustype = onlyfiles[ii][findstimulus:findunderscore]

        print 'Stimulus type..', stimulustype

        # Region
        findregion = onlyfiles[ii].find('Hb')
        findunderscore = [i for i in underscores if i > findregion][0]
        region = onlyfiles[ii][findregion-1:findunderscore]

        print 'Region..', region

        targetDir = os.path.join(SaveFolder, fishnum, region) + filesep
        print 'Images will be saved in .....', targetDir

        if not os.path.exists(targetDir):
            os.makedirs(targetDir)

        cs = ChannelSeparator()
        cs.setId(path)
        bf = BFVirtualStack(path, cs, False, False, False)
        for sliceIndex in xrange(1,bf.getSize() + 1):
            print "Processing slice", sliceIndex
            ip = bf.getProcessor(sliceIndex)
            sliceFileName = os.path.join(targetDir, "T=" + str(sliceIndex) + ".tif")
            FileSaver(ImagePlus(str(sliceIndex), ip)).saveAsTiff(sliceFileName)

#Call using foldername as an argument
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Sort 16-bit files to appropriate folders for thunder.")
    parser.add_argument('FolderName', nargs='+', type=str, help="Name of folder with registered images for sorting")
    args = parser.parse_args()
    
    for arg in args.FolderName:
        FolderName = arg
        # Create a Sorted folder for saving
        SaveFolder = os.path.join(FolderName, 'Sorted') + filesep

        if not os.path.exists(SaveFolder):
            os.makedirs(SaveFolder)

        run(FolderName, SaveFolder)
