# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow
#
# Note that file loading and saving (with 'l' and 's') do not work on
# Mac OSX, so you will have to change 'imgFilename' below, instead, if
# you want to work with different images.
#
# Note that images, when loaded, are converted to the YCbCr
# colourspace, and that you should manipulate only the Y component of
# each pixel when doing intensity changes.


import sys, os, numpy, math

try: # Pillow
  from PIL import Image
except:
  print 'Error: Pillow has not been installed.'
  sys.exit(0)

try: # PyOpenGL
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print 'Error: PyOpenGL has not been installed.'
  sys.exit(0)



# Globals

windowWidth  = 600 # window dimensions
windowHeight =  800

localHistoRadius = 5  # distance within which to apply local histogram equalization



# Current image

imgDir      = 'images'
imgFilename = 'mandrill.png'

currentImage = Image.open( os.path.join( imgDir, imgFilename ) ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )
tempImage    = None



# File dialog (doesn't work on Mac OSX)

if sys.platform != 'darwin':
  import Tkinter, tkFileDialog
  root = Tkinter.Tk()
  root.withdraw()



# Apply brightness and contrast to tempImage and store in
# currentImage.  The brightness and constrast changes are always made
# on tempImage, which stores the image when the left mouse button was
# first pressed, and are stored in currentImage, so that the user can
# see the changes immediately.  As long as left mouse button is held
# down, tempImage will not change.

def applyBrightnessAndContrast( brightness, contrast ):

  width  = currentImage.size[0]
  height = currentImage.size[1]

  srcPixels = tempImage.load()
  dstPixels = currentImage.load()

  for i in range(width):
    for j in range(height):
      #read from source image
      y, cb, cr = srcPixels[i,j]
      #update Y value
      y = (y*contrast + brightness)
      #put pixels back into dest image
      dstPixels[i,j] = y, cb, cr

  print 'adjust brightness = %f, contrast = %f' % (brightness,contrast)

  

# Perform local histogram equalization on the current image using the given radius.

def performHistoEqualization( radius ):

  pixels = currentImage.load()
  width  = currentImage.size[0]
  height = currentImage.size[1]

  histo = []

  # YOUR CODE HERE
  if radius > width/2 or radius > height/2:
    #floor the radius if it exceeds the image dimensions
    radius = min(width/2, height/2)
    print 'Radius exceeds dimensions of image, radius changed to %d' % radius

  histo = [0 for i in range(256)]
  for i in range(-radius, radius+1):
    for j in range(-radius, radius+1):
      x = width/2 + i
      y = height/2 + j

      pixelIntesity = pixels[x,y][0]
      histo[pixelIntesity] = histo[pixelIntesity] + 1

  print histo
  print 'perform local histogram equalization with radius %d' % radius



# Scale the tempImage by the given factor and store it in
# currentImage.  Use backward projection.  This is called when the
# mouse is moved with the right button held down.

def scaleImage( factor ):

  width  = currentImage.size[0]
  height = currentImage.size[1]

  srcPixels = tempImage.load()
  dstPixels = currentImage.load()

  # Now with back projection

  T = [[factor, 0],[0, factor]] #Matrix that is used to perform scaling
  T = numpy.linalg.inv(T) #Inverse is need for the division in back projection

  for i in range(width):
    for j in range(height):
      #Below half the width and half the height are subtracted to keep the image centered, they are later readded in the next two lines of code
      newX, newY = numpy.matmul([i-width/2,j-height/2], T) #calulate this pixels new X and Y coordinates with inverse transform matrix
      
      #Now center the image
      newX += width/2
      newY += height/2

      dstPixels[i, j] = 255,128,128  #make all other pixels uniform colour so it's not picture, white background

      if newX > 0 and newY > 0 and newX < width and newY < height:
        dstPixels[i, j] = srcPixels[newX, newY] #place rgb/ycbcr value in that new pixel

  print dstPixels[300,300]
  print 'scale image by %f' % factor

  

# Set up the display and draw the current image

def display():

  # Clear window

  glClearColor ( 1, 1, 1, 0 )
  glClear( GL_COLOR_BUFFER_BIT )

  # rebuild the image

  img = currentImage.convert( 'RGB' )

  width  = img.size[0]
  height = img.size[1]

  # Find where to position lower-left corner of image

  baseX = (windowWidth-width)/2
  baseY = (windowHeight-height)/2

  glWindowPos2i( baseX, baseY )

  # Get pixels and draw

  imageData = numpy.array( list( img.getdata() ), numpy.uint8 )

  glDrawPixels( width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

  glutSwapBuffers()


  
# Handle keyboard input

def keyboard( key, x, y ):

  global localHistoRadius

  if key == '\033': # ESC = exit
    sys.exit(0)

  elif key == 'l':
    if sys.platform != 'darwin':
      path = tkFileDialog.askopenfilename( initialdir = imgDir )
      if path:
        loadImage( path )

  elif key == 's':
    if sys.platform != 'darwin':
      outputPath = tkFileDialog.asksaveasfilename( initialdir = '.' )
      if outputPath:
        saveImage( outputPath )

  elif key == 'h':
    performHistoEqualization( localHistoRadius )

  elif key in ['+','=']:
    localHistoRadius = localHistoRadius + 1
    print 'radius =', localHistoRadius

  elif key in ['-','_']:
    localHistoRadius = localHistoRadius - 1
    if localHistoRadius < 1:
      localHistoRadius = 1
    print 'radius =', localHistoRadius

  else:
    print 'key =', key    # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

  glutPostRedisplay()



# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.


def loadImage( path ):

  global currentImage

  currentImage = Image.open( path ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )


def saveImage( path ):

  global currentImage

  currentImage.transpose( Image.FLIP_TOP_BOTTOM ).convert('RGB').save( path )
  


# Handle window reshape


def reshape( newWidth, newHeight ):

  global windowWidth, windowHeight

  windowWidth  = newWidth
  windowHeight = newHeight

  glutPostRedisplay()



# Mouse state on initial click

button = None
initX = 0
initY = 0



# Handle mouse click/release

def mouse( btn, state, x, y ):

  global button, initX, initY, tempImage

  if state == GLUT_DOWN:
    tempImage = currentImage.copy()
    button = btn
    initX = x
    initY = y
  elif state == GLUT_UP:
    tempImage = None
    button = None

  glutPostRedisplay()

  

# Handle mouse motion

def motion( x, y ):

  if button == GLUT_LEFT_BUTTON:

    diffX = x - initX
    diffY = y - initY

    applyBrightnessAndContrast( 255 * diffX/float(windowWidth), 1 + diffY/float(windowHeight) )

  elif button == GLUT_RIGHT_BUTTON:

    initPosX = initX - float(windowWidth)/2.0
    initPosY = initY - float(windowHeight)/2.0
    initDist = math.sqrt( initPosX*initPosX + initPosY*initPosY )
    if initDist == 0:
      initDist = 1

    newPosX = x - float(windowWidth)/2.0
    newPosY = y - float(windowHeight)/2.0
    newDist = math.sqrt( newPosX*newPosX + newPosY*newPosY )

    scaleImage( newDist / initDist )

  glutPostRedisplay()
  


# Run OpenGL

glutInit()
glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
glutInitWindowSize( windowWidth, windowHeight )
glutInitWindowPosition( 50, 50 )

glutCreateWindow( 'imaging' )

glutDisplayFunc( display )
glutKeyboardFunc( keyboard )
glutReshapeFunc( reshape )
glutMouseFunc( mouse )
glutMotionFunc( motion )

glutMainLoop()
