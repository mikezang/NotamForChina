import os
import sys
import subprocess
import psutil

class mytool:
    def __init__(self):
        self.count = 0
        self.copied_file = ['./in001.png', './in002.png']
        self.slideshow_list_filename = 'mytext.txt'

    def add_fade_effect(self, infilename, outfilename = 'final'):
        # Makes two frames : at the beginning and at the end
        # This is done by copying one I-Frame for a slide
        # Then, adds fades at both ends
 
        for f in self.copied_file:
            cmd = map(lambda x: '%s' %x, ['cp', infilename, f])
            subprocess.call(cmd)

        # make normal slide
        # ffmpeg -r 1/5 -i in%03d.png -c:v libx264 -r 30 -y -pix_fmt yuv420p slide.mp4 
        in_framerate = 1./5
        out_framerate = 30
        cmd = ['ffmpeg', '-r', in_framerate, '-i','in%03d.png','-c:v','libx264', 
              '-r', out_framerate, '-y','-pix_fmt','yuv420p','slide.mp4'] 
        cmd = map(lambda x: '%s' %x, cmd)
        subprocess.call(cmd)

        # add fade-in effect - from 0th to 30th frame
        #ffmpeg -i slide.mp4 -y -vf fade=in:0:30 slide_fade_in.mp4
        cmd = ['ffmpeg', '-i','slide.mp4','-y','-vf','fade=in:0:30','slide_fade_in.mp4']
        subprocess.call(cmd)

        # add fade-out effect to the slide that has fade-in effect already : 30 frames starting from 120th  
        #ffmpeg -i slide_fade_in.mp4 -y -vf fade=out:120:30 slide_fade_in_out.mp4 
        cmd = ['ffmpeg', '-i','slide_fade_in.mp4','-y','-vf','fade=out:120:30', 'slide_fade_in_out.mp4'] 
        subprocess.call(cmd)

        # rename the output to 'final#.mp4'
        slide_name = outfilename+str(self.count)+'.mp4'
        cmd = map(lambda x: '%s' %x, ['cp', 'slide_fade_in_out.mp4', slide_name]) 
        subprocess.call(cmd)

        # remove the copied files
        for f in self.copied_file:
            cmd = map(lambda x: '%s' %x, ['rm','-f', f])
            subprocess.call(cmd)

        self.count += 1
 
        return slide_name
 
    # make concat list
    def make_slideshow_list(self, slides, fname='mylist.txt'):
        self.slideshow_list_filename = fname
        with open(self.slideshow_list_filename, mode='wb') as f:
            for slide in slides:
                f.write('file ' + slide +'\n')

    # concat all slides in the slideshow list
    def concat_slides(self, slideshow_name = 'my_slideshow.mp4' ):
        cmd = ['ffmpeg', '-y', '-f','concat','-i', self.slideshow_list_filename, '-c', 'copy', slideshow_name] 
        subprocess.call(cmd)


    # get the list of file 
    def file_list(self, d):
        basedir = d
        subdir = []
        slides = []
        sorted_slides = []
        for item in os.listdir(d):
            fullpath = os.path.join(basedir, item)
            if os.path.isdir(fullpath):
                subdir.append(fullpath)
            else:
               if item.startswith('yi') and item.endswith('.png'):
                   slides.append(fullpath)

        return sorted(slides)


if __name__ == '__main__':

    if len(sys.argv) <= 1:
        path = '.'
    else:
        path = sys.argv[1]
    m = mytool()
    slides = m.file_list(path)
    fade_slides = []
    outfile_name = 'yos'
    for slide in slides:
        s = m.add_fade_effect(slide, outfile_name)
        fade_slides.append(s)

    # make slideshow list file
    listname = 'slideshow_list.txt'
    m.make_slideshow_list(fade_slides, listname)
 
    # concatenate the slides in the list file
    slideshow_name = 'yosemite_with_fades.mp4'
    m.concat_slides(slideshow_name)
